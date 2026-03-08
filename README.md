# Neverlose-style Windows Control Center (.exe)

Прототип переделан под стилистику как на референсе: левый тёмный сайдбар, верхняя панель с Save, центральные списки функций и правый info-блок.

## Что внутри

- UI в стиле neverlose (dark + blue accents);
- компактные списки функций с анимированными ON/OFF тумблерами;
- реестровые системные функции с чтением состояния при запуске и проверкой после записи;
- локальные UI-функции в правой панели.

## Реестровые твики

- Disable Windows notifications
- Disable lock screen toasts
- Disable advertising ID
- Disable Windows tips
- Disable Start suggestions
- Disable activity history

## Запуск

```bash
python3 app.py
```

## Сборка `.exe` (Windows)

```powershell
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name ControlCenter app.py
```
