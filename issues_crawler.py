# This script allows to crawl information and repositories from
# GitHub using the GitHub REST API (https://developer.github.com/v3/search/).
#
# Given a query, the script downloads for each repository returned by the query its ZIP file.
# In addition, it also generates a CSV file containing the list of repositories queried.
# For each query, GitHub returns a json file which is processed by this script to get information
# about repositories.
#
# The GitHub API limits the queries to get 100 elements per page and up to 1,000 elements in total.
# To get more than 1,000 elements, the main query should be splitted in multiple subqueries
# using different time windows through the constant SUBQUERIES (it is a list of subqueries).
#
# As example, constant values are set to get the repositories on GitHub of the user 'rsain'.

#CREDITS: https://github.com/rsain/GitHub-Crawler
#############
# Libraries #
#############
import json
import wget
import time
import csv
import requests
import math
import pandas as pd
from pandas.io.json import json_normalize
#############
# Constants #
#############

#"https://api.github.com/repos/{owner}/{repository}/issues"
URL = "https://api.github.com/search/issues?q=repo:" # The basic URL to use the GitHub API
PARAMETERS = "+state:closed"
PAGE_LIMIT = 30
MONTH = 10
YEAR = 2020
#############
# Functions #
#############

def getUrl(url):
    """ Given a URL it returns its body """
    response = requests.get(url)
    if response.status_code != 200:
        return False 
    return response.json()

def buildUrl(repo_owner,repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues?state=closed"
    return url


def getTotalCount(repo_owner,repo_name):
    count_url = f"{URL}{repo_owner}/{repo_name}"
    data = json.loads(json.dumps(getUrl(count_url)))
    total_issues = data['total_count']

    closed_url = f"{URL}{repo_owner}/{repo_name}" + PARAMETERS
    data = json.loads(json.dumps(getUrl(closed_url)))
    total_closed_issues = data['total_count']

    return total_closed_issues,total_issues


def iterateIssues(iter,data,df_data):
    for i in range(0,len(data)):
        print(iter + i + 1,'issue')
        df_data = df_data.append(json_normalize(data[i]),ignore_index=True)

    return df_data

########
# MAIN #
########




# Output CSV file which will contain information about repositories
INPUT_CSV_FILE = f"repositories_{MONTH}_{YEAR}.csv"  # Path to the CSV file generated as output
df = pd.read_csv(INPUT_CSV_FILE)

repo_owner = df.iloc[0][0]
repo_name = df.iloc[0][1]
repo_url = df.iloc[0][2]

total_closed_issues,total_issues = getTotalCount(repo_owner,repo_name)

# Run queries to get information in json format and download ZIP file for each repository
# Obtain the number of pages for the current subquery (by default each page contains 100 items)


print("TOTAL CLOSED ISSUES AVAILABLE: ",total_closed_issues)
print("TOTAL ISSUES AVAILABLE: ",total_issues)
print("REPO URL: ",repo_url)

num_covered_issues = 0
pageNumber = 1
df_issues = pd.DataFrame()


while num_covered_issues <= total_issues:
    url = buildUrl(repo_owner,repo_name)+ "&page="+str(pageNumber)
    print("BUILT URL:",url)
    data = json.loads(json.dumps(getUrl(url)))
    df_issues = iterateIssues(num_covered_issues,data,df_issues)
    num_covered_issues += PAGE_LIMIT
    pageNumber += 1



# data = json.loads(json.dumps(getUrl(url)))
# print("DATA Read as:\n")
# df_data = pd.DataFrame()
# for i in range(len(data)):
#     print(i+1,'issue state: ',data[i]['state'])
#     #obj = pd.DataFrame.from_dict(data[i])
#     #print("OBJECT ",str(i+1),'\n',obj,'\n')
#     df_data = df_data.append(json_normalize(data[i]),ignore_index=True)


time_diff = pd.to_datetime(df_issues['closed_at']) - pd.to_datetime(df_issues['created_at'])
df_issues['Latency_issues'] = time_diff
print(time_diff.mean(),' is average time to close issues')
print((float(total_closed_issues)/total_issues),"is proportion of how many closed issues")
df_issues.to_csv("results_issues.csv")
