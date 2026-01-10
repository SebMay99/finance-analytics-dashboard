# Activate virtual enviroment

.\.venv\Scripts\activate     

# Compile Python code into a distributable .exe

To compile the code into an .exe run:

streamlit-desktop-app build app.py --name HPE_Financial_App_v0.2 --icon .\assets\HPE_icon.png --pyinstaller-options --add-data "processing.py;." --add-data "assets\HPE_icon.webp;assets" --add-data "style.css;." --add-data ".streamlit/config.toml;.streamlit" --onedir --noconsole --noconfirm --clean 

# Run Streamlit local server

For testing and debuggin run:

streamlit run app.py
