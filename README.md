# Windows Control Center Prototype (.exe)

Это **десктопный прототип**, а не браузерное приложение.

## Что реализовано

- нативное окно на `tkinter` с боковым меню разделов;
- секции: Профили, Система, Приватность, Внешний вид;
- карточки настроек с чекбоксами и ползунками;
- кнопка «Сохранить пресет» с визуальным подтверждением.

## Быстрый запуск (dev)

```bash
python3 app.py
```

## Сборка в `.exe` (Windows)

1. Установите Python 3.11+.
2. Установите зависимости:

```powershell
pip install -r requirements.txt
```

3. Соберите exe:

```powershell
pyinstaller --noconfirm --onefile --windowed --name ControlCenter app.py
```

4. Готовый файл будет в:

```text
dist/ControlCenter.exe
```

## Упрощенная сборка через bat

```powershell
build_windows.bat
```
