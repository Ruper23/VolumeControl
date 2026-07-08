#!/usr/bin/env python3
"""
Volume Control Utility – taskbar scroll + tray icon + settings
"""

import sys
import time
import json
import os
import threading
import ctypes
from ctypes import wintypes, windll
from pycaw.pycaw import AudioUtilities
from pynput import mouse
import tkinter as tk
from tkinter import ttk, messagebox
import pystray
from PIL import Image, ImageDraw
import winreg

# -------------------- Константы --------------------
APP_NAME = "VolumeControl"
CONFIG_DIR = os.path.join(os.getenv("APPDATA"), APP_NAME)
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
# ICON_PATH теперь будет в папке конфига, чтобы быть доступным для EXE
ICON_PATH = os.path.join(CONFIG_DIR, "icon.ico")
# Также проверяем иконку рядом с exe/скриптом для упаковки в EXE
BUNDLED_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
STEP_DEFAULT = 3
AUTOSTART_DEFAULT = False

# -------------------- Вспомогательные --------------------
def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    ensure_config_dir()
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"step": STEP_DEFAULT, "autostart": AUTOSTART_DEFAULT}

def save_config(cfg):
    ensure_config_dir()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def create_default_icon():
    """Генерируем иконку динамика и сохраняем как ICO."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2

    # фон — круг с градиентом (тёмно-синий)
    for r in range(cx, 0, -1):
        ratio = r / cx
        c = int(30 + 15 * (1 - ratio))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(c, c, c + 40, 255))

    # корпус динамика (трапеция)
    body_pts = [
        (int(cx - size * 0.12), int(cy - size * 0.18)),
        (int(cx + size * 0.02), int(cy - size * 0.14)),
        (int(cx + size * 0.02), int(cy + size * 0.14)),
        (int(cx - size * 0.12), int(cy + size * 0.18)),
    ]
    draw.polygon(body_pts, fill=(80, 80, 90, 255), outline=(120, 120, 130, 255))

    # конус динамика
    cone_pts = [
        (int(cx + size * 0.02), int(cy - size * 0.10)),
        (int(cx + size * 0.18), int(cy - size * 0.22)),
        (int(cx + size * 0.18), int(cy + size * 0.22)),
        (int(cx + size * 0.02), int(cy + size * 0.10)),
    ]
    draw.polygon(cone_pts, fill=(60, 60, 70, 255), outline=(100, 100, 110, 255))

    # звуковые волны — яркие голубые
    wave_color = (0, 200, 255, 255)
    for i, (r, w) in enumerate([(0.28, 4), (0.36, 3), (0.44, 2)]):
        radius = int(size * r)
        alpha = 255 - i * 40
        draw.arc(
            (cx + int(size * 0.10) - radius, cy - radius,
             cx + int(size * 0.10) + radius, cy + radius),
            start=-50, end=50,
            fill=(0, 200, 255, alpha), width=w
        )

    img.save(ICON_PATH, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    return Image.open(ICON_PATH)

def get_icon_image():
    # При запуске из PyInstaller bundle (sys._MEIPASS) иконка лежит рядом с exe
    if getattr(sys, 'frozen', False):
        # В скомпилированном EXE иконка распакована в _MEIPASS
        base_path = sys._MEIPASS
        bundled_icon = os.path.join(base_path, "icon.ico")
        if os.path.isfile(bundled_icon):
            return Image.open(bundled_icon)
    
    # При обычном запуске — ищем рядом со скриптом
    if os.path.isfile(BUNDLED_ICON_PATH):
        return Image.open(BUNDLED_ICON_PATH)
    
    # Fallback — иконка в конфиге (сгенерированная при первом запуске)
    if os.path.isfile(ICON_PATH):
        return Image.open(ICON_PATH)
    
    return create_default_icon()

# -------------------- Регистр автозапуска --------------------
def set_autostart(enable: bool):
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE)
        if enable:
            exe_path = os.path.abspath(sys.argv[0])
            winreg.SetValueEx(reg, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
        else:
            try:
                winreg.DeleteValue(reg, APP_NAME)
            except FileNotFoundError:
                pass
        reg.Close()
    except Exception as e:
        print(f"Autostart error: {e}")

# -------------------- Основной класс --------------------
class VolumeControl:
    def __init__(self):
        self.cfg = load_config()
        self.step = self.cfg.get("step", STEP_DEFAULT)
        self.autostart = self.cfg.get("autostart", AUTOSTART_DEFAULT)
        set_autostart(self.autostart)

        # audio
        self.volume = AudioUtilities.GetSpeakers().EndpointVolume

        # win32
        self.user32 = windll.user32
        self.taskbar_hwnd = None
        self.find_taskbar()

        # overlay (tkinter)
        self.overlay_root = None
        self.overlay_label = None
        self.overlay_progress = None
        self.overlay_visible = False
        self.hide_timer = None

        # tray
        self.tray_icon = None
        self.tray_thread = None
        self.tray_stop_event = threading.Event()

        # settings
        self.settings_open = False

        # mouse
        self.mouse_listener = None
        self.last_scroll_time = 0
        self.scroll_cooldown = 0.1

    # ---------- taskbar ----------
    def find_taskbar(self):
        self.taskbar_hwnd = self.user32.FindWindowW("Shell_TrayWnd", None)
        if not self.taskbar_hwnd:
            for cls in ("Shell_TrayWnd", "Shell_SecondaryTrayWnd", "WorkerW"):
                self.taskbar_hwnd = self.user32.FindWindowW(cls, None)
                if self.taskbar_hwnd:
                    break

    def is_mouse_on_taskbar(self, x, y):
        if not self.taskbar_hwnd:
            self.find_taskbar()
            if not self.taskbar_hwnd:
                return False
        rect = wintypes.RECT()
        self.user32.GetWindowRect(self.taskbar_hwnd, ctypes.byref(rect))
        return rect.left <= x <= rect.right and rect.top <= y <= rect.bottom

    # ---------- volume ----------
    def get_volume(self):
        return int(self.volume.GetMasterVolumeLevelScalar() * 100)

    def set_volume(self, level):
        level = max(0, min(100, level))
        self.volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return level

    def volume_up(self):
        self.set_volume(min(100, self.get_volume() + self.step))
        self.show_overlay(self.get_volume())

    def volume_down(self):
        self.set_volume(max(0, self.get_volume() - self.step))
        self.show_overlay(self.get_volume())

    def toggle_mute(self):
        muted = self.volume.GetMute()
        self.volume.SetMute(not muted, None)
        self.show_overlay(self.get_volume(), muted=not muted)

    # ---------- overlay ----------
    def create_overlay(self):
        self.overlay_root = tk.Tk()
        self.overlay_root.withdraw()
        self.overlay_root.overrideredirect(True)
        self.overlay_root.attributes("-topmost", True)
        self.overlay_root.attributes("-alpha", 0.9)
        self.overlay_root.configure(bg="#1a1a2e")

        sw = self.overlay_root.winfo_screenwidth()
        sh = self.overlay_root.winfo_screenheight()
        w, h = 300, 80
        x = (sw - w)//2
        y = sh - h - 50
        self.overlay_root.geometry(f"{w}x{h}+{x}+{y}")

        frm = tk.Frame(self.overlay_root, bg="#1a1a2e")
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        self.overlay_label = tk.Label(frm, text="🔊 50%", font=("Segoe UI", 18, "bold"),
                                      fg="#00d4ff", bg="#1a1a2e")
        self.overlay_label.pack(pady=(5,5))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Volume.Horizontal.TProgressbar",
                        troughcolor="#0f0f23", background="#00d4ff",
                        borderwidth=0, lightcolor="#00d4ff", darkcolor="#0099cc")
        self.overlay_progress = ttk.Progressbar(frm, style="Volume.Horizontal.TProgressbar",
                                                orient="horizontal", length=260, mode="determinate")
        self.overlay_progress.pack(pady=(0,5))
        self.overlay_progress["value"] = 50

    def show_overlay(self, vol, muted=False):
        if self.overlay_root is None:
            self.create_overlay()
        icon = "🔇" if muted or vol==0 else ("🔈" if vol<30 else "🔉" if vol<70 else "🔊")
        self.overlay_label.config(text=f"{icon} {vol}%")
        self.overlay_progress["value"] = vol

        if muted or vol==0:
            self.overlay_label.config(fg="#ff4444")
            style = ttk.Style()
            style.configure("Volume.Horizontal.TProgressbar", background="#ff4444")
        elif vol<30:
            self.overlay_label.config(fg="#ffaa00")
            style = ttk.Style()
            style.configure("Volume.Horizontal.TProgressbar", background="#ffaa00")
        else:
            self.overlay_label.config(fg="#00d4ff")
            style = ttk.Style()
            style.configure("Volume.Horizontal.TProgressbar", background="#00d4ff")

        if not self.overlay_visible:
            self.overlay_root.deiconify()
            self.overlay_visible = True
        if self.hide_timer:
            self.overlay_root.after_cancel(self.hide_timer)
        self.hide_timer = self.overlay_root.after(1500, self.hide_overlay)
        self.overlay_root.update_idletasks()
        self.overlay_root.update()

    def hide_overlay(self):
        if self.overlay_root and self.overlay_visible and not self.settings_open:
            self.overlay_root.withdraw()
            self.overlay_visible = False
            self.hide_timer = None

    # ---------- mouse ----------
    def on_scroll(self, x, y, dx, dy):
        now = time.time()
        if now - self.last_scroll_time < self.scroll_cooldown:
            return
        self.last_scroll_time = now
        if self.is_mouse_on_taskbar(x, y):
            if dy > 0:
                self.volume_up()
            elif dy < 0:
                self.volume_down()

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.middle and pressed:
            if self.is_mouse_on_taskbar(x, y):
                self.toggle_mute()

    # ---------- tray ----------
    def tray_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Настройки", self.show_settings, default=True),
            pystray.MenuItem("Выход", self.exit_app)
        )

    def show_settings(self, icon=None, item=None):
        if self.settings_open:
            return
        self.settings_open = True

        win = tk.Toplevel()
        win.title("Настройки Volume Control")
        win.resizable(False, False)
        win.attributes("-topmost", True)

        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        w, h = 320, 160
        x = (sw - w) // 2
        y = (sh - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        frm = tk.Frame(win, padx=15, pady=15)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Шаг громкости (%):", anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        step_var = tk.IntVar(value=self.step)
        step_slider = ttk.Scale(frm, from_=1, to=10, orient="horizontal",
                                variable=step_var, length=200)
        step_slider.grid(row=0, column=1, pady=4)
        step_val_lbl = tk.Label(frm, textvariable=step_var, width=3)
        step_val_lbl.grid(row=0, column=2, padx=(5,0))

        autostart_var = tk.BooleanVar(value=self.autostart)
        tk.Checkbutton(frm, text="Автозапуск с Windows", variable=autostart_var).grid(row=1, column=0, columnspan=3, pady=8, sticky="w")

        def on_save():
            self.step = step_var.get()
            self.autostart = autostart_var.get()
            self.cfg["step"] = self.step
            self.cfg["autostart"] = self.autostart
            save_config(self.cfg)
            set_autostart(self.autostart)
            self.settings_open = False
            win.destroy()

        def on_cancel():
            self.settings_open = False
            win.destroy()

        def on_close():
            self.settings_open = False
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        btn_frm = tk.Frame(frm)
        btn_frm.grid(row=2, column=0, columnspan=3, pady=(10,0))
        ttk.Button(btn_frm, text="Сохранить", command=on_save).pack(side="left", padx=5)
        ttk.Button(btn_frm, text="Отмена", command=on_cancel).pack(side="left", padx=5)

        win.grab_set()
        win.wait_window()

    def exit_app(self, icon=None, item=None):
        self.tray_stop_event.set()
        if self.tray_icon:
            self.tray_icon.stop()
        self.stop()

    def run_tray(self):
        image = get_icon_image()
        self.tray_icon = pystray.Icon(APP_NAME, image, "Volume Control", self.tray_menu())
        self.tray_icon.run()

    def start_tray(self):
        self.tray_thread = threading.Thread(target=self.run_tray, daemon=True)
        self.tray_thread.start()

    # ---------- start / stop ----------
    def start(self):
        print("Volume Control started!")
        print(f"Шаг: {self.step}% | Автозапуск: {'Вкл' if self.autostart else 'Выкл'}")
        print("Scroll ↑ на таскбаре → громкость +step%")
        print("Scroll ↓ на таскбаре → громкость -step%")
        print("Средняя кнопка на таскбаре → Mute/Unmute")
        print("Правый‑клик по иконке в трее → Настройки / Выход")
        print("Ctrl+C в консоли → выход")

        self.create_overlay()
        self.start_tray()
        self.mouse_listener = mouse.Listener(on_scroll=self.on_scroll, on_click=self.on_click)
        self.mouse_listener.start()

        try:
            self.overlay_root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        print("\nОстановка Volume Control...")
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        if self.overlay_root:
            self.overlay_root.quit()
            self.overlay_root.destroy()
        print("Остановлено.")

def main():
    # Проверка админа (не обязателен, но pycaw может потребовать)
    try:
        ctypes.windll.shell32.IsUserAnAdmin()
    except:
        pass
    VolumeControl().start()

if __name__ == "__main__":
    main()
