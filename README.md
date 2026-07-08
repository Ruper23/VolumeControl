# Volume Control

[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/Ruper23/VolumeControl/build.yml?label=Build&logo=github)](https://github.com/Ruper23/VolumeControl/actions)

Утилита для управления громкостью Windows: прокрутка колесом мыши над панелью задач, системный трей с настройками, автозапуск.

## ✨ Возможности

| Действие | Результат |
|----------|-----------|
| `Scroll ↑` на панели задач | Громкость `+` (шаг настраивается) |
| `Scroll ↓` на панели задач | Громкость `-` (шаг настраивается) |
| `Средняя кнопка` на панели задач | Mute / Unmute |
| `Правый клик` по иконке в трее | Меню: **Настройки** / **Выход** |

**Настройки (в меню трея):**
- 🎚 **Шаг громкости** — 1–10%
- 🔄 **Автозапуск с Windows** — включить/выключить
- 💾 Настройки сохраняются в `%APPDATA%\VolumeControl\config.json`

## 📥 Установка

### Вариант 1: Готовый EXE (рекомендуется)
1. Скачайте `VolumeControl.exe` из [Releases](https://github.com/Ruper23/VolumeControl/releases/latest)
2. Запустите — появится иконка в трее (нижний правый угол)
3. (Опционально) Добавьте в автозагрузку через настройки в меню трея

### Вариант 2: Сборка из исходников
```cmd
git clone https://github.com/Ruper23/VolumeControl.git
cd VolumeControl
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --noconsole --name "VolumeControl" ^
  --hidden-import=pystray ^
  --hidden-import=PIL ^
  --hidden-import=PIL.Image ^
  --hidden-import=PIL.ImageDraw ^
  --hidden-import=pycaw ^
  --hidden-import=comtypes ^
  --hidden-import=comtypes.client ^
  --hidden-import=pynput ^
  --hidden-import=pynput.mouse ^
  --hidden-import=winreg ^
  volume_control.py
```
Готовый `VolumeControl.exe` будет в папке `dist/`.

## ⚙️ Как это работает

- **pycaw** (Windows Core Audio API) — управление громкостью системы
- **pynput** — глобальный хук мыши для отслеживания скролла над таскбаром
- **pystray** + **Pillow** — иконка в системном трее (генерация программная, без внешних файлов)
- **tkinter** — оверлей громкости и окно настроек
- **winreg** — запись/удаление автозапуска в `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`

## 📁 Структура проекта

```
VolumeControl/
├── volume_control.py   # Основной скрипт
├── requirements.txt    # Зависимости Python
├── build.bat           # Скрипт сборки для Windows
├── LICENSE             # MIT License
├── .gitignore
└── .github/
    └── workflows/
        └── build.yml   # GitHub Actions: автосборка EXE при теге
```

## 🛠 Разработка

```bash
# Запуск в режиме разработки (с консолью)
python volume_control.py

# Проверка синтаксиса
python -m py_compile volume_control.py
```

## 📄 Лицензия

MIT License — см. [LICENSE](LICENSE).

---

*Сделано для личного удобства, делюсь на случай, если кому пригодится.*