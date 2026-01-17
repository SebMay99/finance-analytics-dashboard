@echo off
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo Cleaning previous builds...
if exist dist move dist dist_old_%TIMESTAMP% >nul 2>&1
if exist build move build build_old_%TIMESTAMP% >nul 2>&1
if exist *.spec del /q *.spec >nul 2>&1

echo Building application...
streamlit-desktop-app build app.py ^
 --name HPE_Financial_App_v0.6 ^
 --icon .\assets\HPE_icon.png ^
 --pyinstaller-options ^
 --add-data "functions;functions" ^
 --add-data "assets;assets" ^
 --add-data "public;public" ^
 --add-data "style.css;." ^
 --add-data ".streamlit/config.toml;.streamlit" ^
 --add-data ".venv\Lib\site-packages\kaleido;kaleido" ^
 --hidden-import kaleido ^
 --hidden-import kaleido.scopes.plotly ^
 --hidden-import tkinter ^
 --hidden-import tkinter.filedialog ^
 --collect-all kaleido ^
 --copy-metadata kaleido ^
 --onedir --noconsole --noconfirm --clean

echo Build complete!
pause