import os
import pandas as pd
import numpy as np
cwd = os.path.abspath('') 
files = os.listdir(cwd)  
np.random.seed(999)
## Method 1 gets the first sheet of a given file
df = pd.DataFrame()
temp=''
file_finals = []
for file in files:
    if file.endswith('.csv'):
        print(file)

        file_finals += [str(file)]* 1001
        temp=pd.read_csv(file,names=['User',"Name","Url"],skiprows=1,nrows=1001)
        print(temp.shape)
        df = df.append(temp, ignore_index=True) 
print(len(file_finals))
print(df.shape)

df['FileName']=file_finals

df.head() 
df.to_csv('one_sheet_excel.csv',index=False)

df2 = pd.read_csv('one_sheet_excel.csv',names=['User',"Name","Url",'FileName'], header=None)

ds = df2.sample(frac=1)
ds.to_csv('one_sheet_excel_shuffle.csv',index=False)