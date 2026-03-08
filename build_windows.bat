@echo off
setlocal

python -m pip install --upgrade pip
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name ControlCenter app.py

echo.
echo Build completed: dist\ControlCenter.exe
pause
