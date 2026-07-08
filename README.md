# Volume Control

[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/Ruper23/VolumeControl/build.yml?label=Build&logo=github)](https://github.com/Ruper23/VolumeControl/actions)

Утилита для управления громкостью Windows: прокрутка колесом мыши над панелью задач, системный трей с настройками, автозапуск.

## Возможности

| Действие | Результат |
|----------|-----------|
| `Scroll ↑` на панели задач | Громкость `+` (шаг настраивается) |
| `Scroll ↓` на панели задач | Громкость `-` (шаг настраивается) |
| `Средняя кнопка` на панели задач | Mute / Unmute |
| `Правый клик` по иконке в трее | Меню: **Настройки** / **Выход** |

**Настройки (в меню трея):**
- **Шаг громкости** — 1-10%
- **Автозапуск с Windows** — включить/выключить
- Настройки сохраняются в `%APPDATA%\VolumeControl\config.json`

## Установка

### Скачать готовый EXE (рекомендуется)

1. Перейдите в [Releases](https://github.com/Ruper23/VolumeControl/releases/latest)
2. Скачайте `VolumeControl.exe`
3. Запустите — программа готова к работе

> Программа не требует установки Python или каких-либо зависимостей. Работает на любом ПК с Windows 10/11.

### Сборка из исходников

```cmd
git clone https://github.com/Ruper23/VolumeControl.git
cd VolumeControl
pip install -r requirements.txt
pip install pyinstaller pystray pywin32 pillow
pyinstaller --onefile --noconsole --name "VolumeControl" --icon=icon.ico ^
  --collect-all pystray --collect-all PIL ^
  --hidden-import=pycaw --hidden-import=pycaw.pycaw ^
  --hidden-import=comtypes --hidden-import=comtypes.client ^
  --hidden-import=pynput --hidden-import=pynput.mouse --hidden-import=pynput.keyboard ^
  --hidden-import=pystray._win32 --hidden-import=pystray._util ^
  --hidden-import=win32gui --hidden-import=win32api --hidden-import=win32con ^
  --hidden-import=win32gui_struct --hidden-import=winreg --hidden-import=_tkinter ^
  volume_control.py
```

Готовый `VolumeControl.exe` будет в папке `dist/`.

## Как это работает

- **pycaw** (Windows Core Audio API) — управление громкостью системы
- **pynput** — глобальный хук мыши для отслеживания скролла над таскбаром
- **pystray** + **Pillow** — иконка в системном трее
- **tkinter** — оверлей громкости и окно настроек
- **winreg** — запись/удаление автозапуска

## Структура проекта

```
VolumeControl/
├── volume_control.py       # Основной скрипт
├── requirements.txt        # Зависимости Python
├── build.bat               # Скрипт сборки (установка в Program Files + ярлык)
├── installer.iss           # Inno Setup скрипт для создания установщика
├── LICENSE                 # MIT License
├── .gitignore
└── .github/
    └── workflows/
        └── build.yml       # GitHub Actions: автосборка при теге
```

## Лицензия

MIT License — см. [LICENSE](LICENSE).

---

*Сделано для личного удобства, делюсь на случай, если кому пригодится.*
