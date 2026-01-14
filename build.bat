@echo off
streamlit-desktop-app build app.py ^
 --name HPE_Financial_App_v0.5-beta.1401 ^
 --icon .\assets\HPE_icon.png ^
 --pyinstaller-options ^
 --add-data "functions\processing.py;functions" ^
 --add-data "assets\HPE_icon.webp;assets" ^
 --add-data "style.css;." ^
 --add-data ".streamlit/config.toml;.streamlit" ^
 --add-data "functions\processing.py;functions" ^
 --add-data "public/config.py;public" ^
 --add-data "functions\graphicator.py;functions" ^
 --onedir --noconsole --noconfirm --clean
pause
