# Windows Control Center Prototype (.exe)

Десктопный прототип на `tkinter` с фокусом на **переключатели ON/OFF**.

## Что реализовано

- нативное desktop-окно (не браузер);
- разделы с функциями только формата включить/выключить;
- анимированные красивые тумблеры;
- пример реальной системной функции: **"Отключить все уведомления Windows"**;
- при запуске состояние этой функции определяется автоматически через реестр:
  - если ключи уже выставлены в режим отключения уведомлений — тумблер сразу `ON`;
  - если нет — тумблер сразу `OFF`.

## Важно по Windows-уведомлениям

Проверка/изменение делается в `HKCU` по ключам:

- `Software\Microsoft\Windows\CurrentVersion\PushNotifications -> ToastEnabled`
- `Software\Microsoft\Windows\CurrentVersion\Notifications\Settings -> NOC_GLOBAL_SETTING_TOASTS_ENABLED`

`0` = уведомления отключены, `1` = включены.

## Быстрый запуск (dev)

```bash
python3 app.py
```

## Сборка в `.exe` (Windows)

```powershell
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name ControlCenter app.py
```

Готовый файл:

```text
dist/ControlCenter.exe
```

## Быстрая сборка через bat

```powershell
build_windows.bat
```
