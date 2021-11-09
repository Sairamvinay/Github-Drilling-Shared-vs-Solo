import pandas as pd
import numpy as np
import statsmodels.api as sm
from pytimeparse.timeparse import timeparse
import matplotlib.pyplot as plt

np.random.seed(999)


INPUT_CSV_FILE = "check/one_sheet_excel_shuffle_ROW_800.csv"
feats = ['num_contributors','total closed issued','total issues','avg contributor per issue']#,"Age"]

df = pd.read_csv(INPUT_CSV_FILE)

X = df[feats]
y = df['average latency']

#pre-process the features and the output

X = X.astype(float)
X_or = X
X = sm.add_constant(X)


y = y.apply(lambda x: str(x)[:str(x).find('.')])
y = y.apply(lambda x: timeparse(x))


model = sm.OLS(y,X)
results = model.fit()
print("TOTAL MSE: ",results.mse_total)
print(results.summary())