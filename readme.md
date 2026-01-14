Checkout the **Releases** page for the latest executable. 

# Setup instructions
Follow these instrucctions to clone the repo and install the required libraries to run and compile the app.

### 1. Clone the repository to your machine
Go into your local directory
`cd path/to/your/local/directory`

Clone the repository into your directory
`git clone https://github.com/SebMay99/business-intelligence.git`

Go into the project folder
`cd business-intelligence`

### 2. Create a local virtual enviroment inside your project folder
This is recommended to keep the project libraries separate from the rest of the system
`python -m venv .venv`

### 3. Activate virtual enviroment
`.\.venv\Scripts\activate`
### 4. Install the libraries in requirements.txt 
`pip install -r requirements.txt`

# Run Streamlit local server
For testing and debugging run to try the app in a local browser:

`streamlit run app.py`

# Compile Python code into a distributable .exe
To compile the code into an .exe run build.bat:

`.\build.bat`

Each file and asset has to be specified, otherwise it won't be included in the compilation and the .exe won't work. 

## TODO
# Data Frame examples for debugging
### filtered_table_df

|index     | Category |   Cost   | Revenue  |  Margin  | Percentage |
| -------- | -------- | -------- | -------- | -------- | ---------- |       
| 1        | Compute   | 2.301275e+05|  4.826505e+05|  2.525230e+05|   52.320055|
| 2        |    Storage  |8.319115e+06|  3.542283e+07|  2.710372e+07|   76.514822|
| 5        | Total Product|  8.549242e+06|  3.590548e+07|  2.735624e+07|   76.189590|
| 6        |  Installation | 5.940000e+03|  3.960000e+04|  3.366000e+04|   85.000000|
| 7        |     Support  |3.643517e+05|  2.010798e+06|  1.646447e+06|   81.880248|
| 8        | Complete Care|  3.569123e+05| -1.653450e+06| -2.010362e+06|  121.585916|
| 13       |       SaaS  |7.009200e+02|  1.993200e+04|  1.923108e+04|   96.483444|
| 16       | Total Services|  7.279049e+05|  4.168805e+05| -3.110245e+05|  -74.607591|
| 22       |    Pan HPE  |9.277147e+06|  3.632236e+07|  2.704521e+07|   74.458854|
