import os
import pandas as pd
import numpy as np

FOLDER = 'data/'
FOLDER2 = 'Terry/'

cwd = os.path.abspath(FOLDER) 
files = os.listdir(cwd)  
np.random.seed(999)

# Function for iterating over each month
def iterateMonth(temp,month,filename,perDay = 1000):
    #go thru eaach day (1000s) and pick top 50 in each

    end_range = temp.shape[0]
    pickDay = 50
    df_month = pd.DataFrame()
    #print("Month ",month)
    day = 1
    for index in range(0,end_range,perDay):
        df_day = temp.iloc[index:index + pickDay][:]
        df_day['Day'] = int(day)
        df_day['filename'] = str(filename)
        df_day = df_day.reset_index(drop = True)
        #print('\t\t',df_day.shape, 'for day ',1 + (index/perDay), ' within index ',index, ' to ',index + pickDay)
        df_month = df_month.append(df_day,ignore_index= True)
        day += 1

    return df_month

## Method 1 gets the first sheet of a given file
df = pd.DataFrame()
temp= None
file_finals = []
for file in files:
    if file.endswith('.csv'):
        
        #file_finals += [str(file)]* 1001
        temp=pd.read_csv(FOLDER + file,names=['User',"Name","Url"],header = 0)#,skiprows=1,nrows=1001)
        #print(file,'\t',temp.shape)

        month = file.split('_')[1]
        year = file.split('_')[2]
        year = year[:year.find('.')]

        df_month = iterateMonth(temp,month,file)
        df_month['month'] = int(month)
        df_month['year'] = int(year)

        df_month = df_month.reset_index(drop = True)
        print("Month: ",month, "Year ",year," #Samples: ",df_month.shape[0])

        df = df.append(df_month,ignore_index= True)
        

FOLDER2 = 'Terry/'

cwd = os.path.abspath(FOLDER2) 
files = os.listdir(cwd)  

for file in files:
    if file.endswith('.csv'):
        
        #file_finals += [str(file)]* 1001
        temp=pd.read_csv(FOLDER2 + file,names=['User',"Name","Url"],header = 0)#,skiprows=1,nrows=1001)
        print(file,'\t',temp.shape)

        month = file.split('_')[1]
        year = file.split('_')[2]
        year = year[:year.find('.')]

        df_month = iterateMonth(temp,month,file,perDay = 50)
        df_month['month'] = month
        df_month['year'] = year

        df_month = df_month.reset_index(drop = True)
        print("Month: ",month, "Year ",year," #Samples: ",df_month.shape[0])

        df = df.append(df_month,ignore_index= True)


df['Day'] = df['Day'].astype(int)
print(df.shape[0], ' samples finally')
print(df['Url'].unique().shape[0],' many unique URLs finally')
ds = df.sample(frac=1)
ds = ds.reset_index(drop = True)
ds.to_csv(f"final_bunch_merge.csv",index = True)

# df['FileName']=file_finals

# df.head() 
# df.to_csv('one_sheet_excel.csv',index=False)

# df2 = pd.read_csv('one_sheet_excel.csv',names=['User',"Name","Url",'FileName'], header=None)

# ds = df2.sample(frac=1)
# ds.to_csv('one_sheet_excel_shuffle.csv',index=False)
