import os
import pandas as pd
import numpy as np
import random
from datetime import date


def create_time_list(column):
	temp=[]
	for x in column:
		x=x.split('_')[1:]
		temp.append((x[1],x[0]))
	return temp
	
def calculate_time_diff(temp):
	daysDifference=[]
	for day in temp:
		excel_date = date(int(day[0]), int(day[1]), random.randint(1, 28))
		final_date = date(2021, 10, 31)
		delta = final_date - excel_date
		daysDifference.append(delta.days)
	return daysDifference

df = pd.DataFrame()
df=df = df.append(pd.read_csv('Final_Output.csv'), ignore_index=True)

print(df['filename'])

time_list=create_time_list(df['filename'])
daysDifference=calculate_time_diff(time_list)
print(daysDifference)
df['Age']=daysDifference
df.to_csv('Time_Diff.csv',index=False)

