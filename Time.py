import os
import pandas as pd
import numpy as np
import random
from datetime import date
import re

random.seed(999)
def create_time_list(column):
	temp=[]
	for x in column:
		x=re.split('_|-',x)[1:]
		temp.append((x[1],x[0]))
	return temp
	
def calculate_time_diff(temp):
	daysDifference=[]
	for day in temp:
		excel_date = date(int(day[0]), int(day[1]), 1)#random.randint(1, 28))
		final_date = date(2021, 10, 31)
		delta = final_date - excel_date
		daysDifference.append(delta.days)
	return daysDifference

df = pd.read_csv('merge_all_combine.csv')


time_list=create_time_list(df['filename'])
daysDifference=calculate_time_diff(time_list)
df['Age']=daysDifference
df.to_csv('final_data.csv',index=False)

