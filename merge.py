import os
import pandas as pd
cwd = os.path.abspath('') 
files = os.listdir(cwd)  

## Method 1 gets the first sheet of a given file
df = pd.DataFrame()
for file in files:
    if file.endswith('.xlsx'):
        df = df.append(pd.read_excel(file), ignore_index=True) 
df.head() 
df.to_excel('one_sheet_excel.xlsx')



## Method 2 gets all sheets of a given file
df_total = pd.DataFrame()
for file in files:                         # loop through Excel files
    if file.endswith('.xlsx'):
        excel_file = pd.ExcelFile(file)
        sheets = excel_file.sheet_names
        for sheet in sheets:               # loop through sheets inside an Excel file
            df = excel_file.parse(sheet_name = sheet)
            df_total = df_total.append(df)
df_total.to_excel('combined_sample_file.xlsx')