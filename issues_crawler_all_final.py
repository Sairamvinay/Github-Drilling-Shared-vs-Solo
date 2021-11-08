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
import os
import math
import pandas as pd
import numpy as np
import time
import warnings
warnings.filterwarnings(action='ignore')
from pandas.io.json import json_normalize

from pydriller import Repository


#############
# Constants #
#############

#"https://api.github.com/repos/{owner}/{repository}/issues"

api_token = "YOUR_TOKEN"
URL = "https://api.github.com/search/issues?q=repo:" # The basic URL to use the GitHub API
headers = {'Authorization': 'token %s' % api_token} # The authorization needed for Github API
authorization = ("YOUR_USERNAME", api_token)
CHECKPOINT_DIR = "check/"
PARAMETERS = "%20is:closed"
PAGE_LIMIT = 30
SAMPLE_LIMIT = 2000

if not os.path.isdir(CHECKPOINT_DIR):
    os.mkdir(CHECKPOINT_DIR)


#############
# Functions #
#############
total_calls = 1
curr_iter = 1
def getUrl(url):
    global total_calls, authorization
    """ Given a URL it returns its body """
    if total_calls % 30 == 0:
        time.sleep(60)
    response = requests.get(url, auth=authorization)
    if response.status_code != 200:
        print('total calls: ', total_calls, 'response: ', response.status_code)
        time.sleep(60)
        return False 
    total_calls += 1
    return response.json()
  
def get_contributors_url(repo_owner, repo_name):
    global authorization
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contributors?per_page=1&anon=true'
    response = requests.get(url, auth=authorization)
    if response.status_code != 200:
        return False
    return response

def get_contributors(repo_owner, repo_name):
    val = get_contributors_url(repo_owner, repo_name)
    if not val:
        return False
    if 'Link' not in val.headers:
        return 1
    return int(val.headers['Link'].split('&anon')[2].split('&page=')[1].split('>')[0])

def buildUrl(repo_owner,repo_name, parameters = ''):
    url = f'https://api.github.com/search/issues?q=repo:{repo_owner}/{repo_name}%20is:issue' + parameters
    return url


def getTotalCount(repo_owner,repo_name):
    data = json.loads(json.dumps(getUrl(buildUrl(repo_owner, repo_name))))
    if not data:
        return 0, 0
    total_issues = data['total_count']

    data = json.loads(json.dumps(getUrl(buildUrl(repo_owner, repo_name, PARAMETERS))))
    total_closed_issues = data['total_count']

    return total_closed_issues,total_issues

def find_intersection(developers, create_time, closed_time):
    num_intersection = 0
    for _, time_frame in developers.items():
        start, end = time_frame
        if create_time < start < closed_time or create_time < end < closed_time or start < create_time < end or start < closed_time < end:
            num_intersection += 1
    return num_intersection

def iterateIssues(iter,data,df_data,repo_url, developers, num_dev_per_issue):
    val = 0
    if data:
        for i in range(0,len(data)):

            df_data = df_data.append(json_normalize(data[i]),ignore_index=True)
            create_time = np.datetime64(data[i]['created_at'])
            closed_time = np.datetime64(data[i]['closed_at'])
            num_dev_per_issue.append(find_intersection(developers, create_time, closed_time))
    
    return df_data

def gather_issues(repo_owner, repo_name, total_issues,repo_url):
    num_covered_issues = 0
    page_number = 0
    df_issues = pd.DataFrame()
    developers = get_developer_per_issue(repo_url)
    num_dev_per_issue = []

    while num_covered_issues <= total_issues:
        url = buildUrl(repo_owner,repo_name, PARAMETERS)+ "&page="+str(page_number)
        data = json.loads(json.dumps(getUrl(url)))['items']
        df_issues = iterateIssues(num_covered_issues,data,df_issues,repo_url, developers, num_dev_per_issue)
        num_covered_issues += PAGE_LIMIT
        page_number += 1
    df_issues['num_dev_per_issue'] = num_dev_per_issue
    return df_issues



def get_developer_per_issue(repo_url):
    num_commiter_per_issue = {}
    val = 0
    for commit in Repository(path_to_repo=repo_url).traverse_commits():
        commiter_date = np.datetime64(str(commit.committer_date))

        if commit.author.email in num_commiter_per_issue:
            num_commiter_per_issue[commit.author.email][1] = commiter_date #in case we see the commiter again, we re-update the end date
        else:
            num_commiter_per_issue[commit.author.email] = [commiter_date, commiter_date] #we set basic start and end date as same at beginning of new user

    return num_commiter_per_issue


def save_checkpoint(out_df,row_val):
    if (row_val % 100 == 0 and row_val != 0):
        out_df = out_df.rename(columns = dict(enumerate(['url','num_contributors','total closed issued','total issues','avg contributor per issue','average latency','filename'])))
        out_df.to_csv(f"{CHECKPOINT_DIR}{INPUT_CSV_FILE[:-4]}_ROW_{row_val}.csv",index = False)

########
# MAIN #
########


start_time = time.time()
number_of_non_zero_repos = 0
# Output CSV file which will contain information about repositories
INPUT_CSV_FILE = f'one_sheet_excel_shuffle.csv' # Path to the CSV file generated as output
df = pd.read_csv(INPUT_CSV_FILE)
res_df = pd.DataFrame()
for row in range(0,SAMPLE_LIMIT):
    repo_owner = df.iloc[row][0]
    repo_name = df.iloc[row][1]
    repo_url = df.iloc[row][2]
    repo_date = df.iloc[row][3]
    
    try:
        total_closed_issues,total_issues = getTotalCount(repo_owner,repo_name)
    except:
        continue

    # Run queries to get information in json format and download ZIP file for each repository
    # Obtain the number of pages for the current subquery (by default each page contains 100 items)
    print('-'*100)
    print("REPO ",row+1)
    print("TOTAL CALLS: ",total_calls)
    print("TOTAL CLOSED ISSUES AVAILABLE: ",total_closed_issues)
    print("TOTAL ISSUES AVAILABLE: ",total_issues)
    print("REPO URL: ",repo_url)

    if total_closed_issues != 0:
        number_of_non_zero_repos += 1
        try:
            df_issues = gather_issues(repo_owner, repo_name, total_closed_issues,repo_url)

        except:
            save_checkpoint(res_df,row)
            continue
        

        if not df_issues.empty:
            time_diff = pd.to_datetime(df_issues['closed_at']) - pd.to_datetime(df_issues['created_at'])
            try:
                num_contributors = get_contributors(repo_owner, repo_name)
            except:
                save_checkpoint(res_df,row)
                continue

            df_issues['Latency_issues'] = time_diff
            avg_dev_per_repo_issue = df_issues['num_dev_per_issue'].mean()

            print("Average number of contributors per issue for this repository is: ",avg_dev_per_repo_issue)
            print('number of contributors = ', num_contributors)
            print(time_diff.mean(),' is average time to close issues')
            print((float(total_closed_issues)/total_issues),"is proportion of how many closed issues")

            res_df = res_df.append(pd.Series([repo_url,num_contributors, total_closed_issues, total_issues, avg_dev_per_repo_issue,time_diff.mean(),repo_date[:-4]]), ignore_index = True)

    save_checkpoint(res_df,row)


res_df = res_df.rename(columns = dict(enumerate(['url','num_contributors','total closed issued','total issues','avg contributor per issue','average latency','filename'])))
print(number_of_non_zero_repos,' many non-zero repos')

end_time = time.time()
diff = (end_time - start_time)/60.0
print("Minutes elapsed: ",round(diff,2))

res_df.to_csv(f"{INPUT_CSV_FILE[:-4]}_issues_final.csv",index = False)


