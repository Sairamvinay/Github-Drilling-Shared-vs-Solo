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
import re
import random
import datetime
import time
import warnings
warnings.filterwarnings(action='ignore')
from pandas.io.json import json_normalize

#from pydriller import Repository


#############
# Constants #
#############

#"https://api.github.com/repos/{owner}/{repository}/issues"

api_token = "YOUR_TOKEN"
URL = "https://api.github.com/search/issues?q=repo:" # The basic URL to use the GitHub API
headers = {'Authorization': 'token %s' % api_token} # The authorization needed for Github API
authorization = ("YOUR_USERNAME", api_token)
CHECKPOINT_DIR = "check/"
SAMPLE_LIMIT = 1000
START_LIMIT = 1001

cols = ['User','Name','Url','Forks','Project Size','Contributors','Avg Created Repos Out',\
'Avg Forked Repos Out','Total Closed Issues','Avg Latency','Avg Comments','Day','month','year'\
,'Age','filename']

if not os.path.isdir(CHECKPOINT_DIR):
    os.mkdir(CHECKPOINT_DIR)


#############
# Functions #
#############
def getUrl(url):
    global total_calls, authorization
    """ Given a URL it returns its body """
    response = requests.get(url, auth=authorization)
    if response.status_code != 200:
        print('response: ', response.status_code)
        #time.sleep(60)
        rate_limit_url = 'https://api.github.com/rate_limit'
        r = requests.get(rate_limit_url, auth=authorization)
        resources = r.json()['resources']
        if resources['core']['remaining'] == 0:
            time_left = np.abs(int(time.time()) - resource['core']['reset'])
            if time_left > 0:
                print('sleeping seconds in core: ', time_left)
                time.sleep(time_left + 1)
        elif resources['search']['remaining'] == 0:
            time_left = np.abs(int(time.time()) - resource['search']['reset'])
            if time_left > 0:
                print('sleeping seconds in search: ', time_left)
                time.sleep(time_left + 1)
        response = requests.get(url, auth=authorization)
        if response.status_code != 200:
            return False 
    return response

def get_contributors_top_ten_url(repo_owner, repo_name):
    global authorization
    contributors_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contributors?per_page=10"
    response = getUrl(contributors_url)
    return response

def get_contributors_url(repo_owner, repo_name):
    global authorization
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contributors?per_page=1&anon=true'
    response = getUrl(url)
    return response

def get_cross_dev(repo_owner,repo_name,repo_url,day,month,year):
    
    excel_date = datetime.date(int(year),int(month),int(day))
    #get top 10 contributors
    contributors = get_contributors_top_ten_url(repo_owner,repo_name)
    if not contributors:
        return 0,0

    contributors = contributors.json()
    num_forks_per_contributor = []
    num_repos_per_contributor = []
    #print("Working on this URL: ",repo_url)
    #print("The top ten contributors are: ")
    i = 0
    for contributor in contributors:
        try:
            username = contributor['login']
        except:
            print('*'*100)
            print("PROBLEM BRINGS")
            print('URL',repo_url)
            print(contributor)
            #df_c = pd.DataFrame(contributor)
            #print(df_c)
            continue
        
        i += 1
        user_url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=created"
        user_repos = getUrl(user_url)
        user_repos = user_repos.json()
        if not user_repos:
            continue
        df_user_repos = pd.DataFrame(user_repos)
        df_user_repos['created_at'] = pd.to_datetime(df_user_repos['created_at'])
        user_repos_datetime= [datetime.datetime(x.year,x.month,x.day,x.hour,x.minute,x.second) for x in df_user_repos['created_at']]
        df_user_repos['created_at_datetime'] = user_repos_datetime
        excel_date = pd.to_datetime(excel_date)
        
        df_filtered_user_repos = df_user_repos[df_user_repos['created_at_datetime'] >= excel_date]
        num_repos = df_filtered_user_repos.shape[0] #all repos created during the timeframe of current project by this user
        num_forks = df_filtered_user_repos[df_filtered_user_repos['fork']==True].shape[0]
        num_repos_per_contributor.append(num_repos)
        num_forks_per_contributor.append(num_forks)
        # print(f"Username {i}: ",username)
        # print(f"number of repos created after this project was started by {username}:",num_repos)
        # print(f"number of forks created after this project was started by {username}:",num_forks)
        # print('='*100)
        #df_filtered_user_repos.to_csv(f"usr_temp/{username}.csv",index=False)
    return np.mean(num_repos_per_contributor),np.mean(num_forks_per_contributor)


  


#needs HEADERS
def get_contributors(repo_owner, repo_name):
    val = get_contributors_url(repo_owner, repo_name)
    if not val:
        return False
    if 'Link' not in val.headers:
        return 1
    return int(val.headers['Link'].split('&anon')[2].split('&page=')[1].split('>')[0])




def find_output(n):
    return int(n.split(';')[-2].split('=')[-1].split('>')[0])


#needs HEADERS
def getTotalCount(repo_owner,repo_name):
    issue_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues?state=closed&per_page=1"
    pull_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=closed&per_page=1"

    issue_op = getUrl(issue_url)
    pull_op = getUrl(pull_url)



    num_total = 0
    num_pulls = 0

    if issue_op and pull_op:
        issue_op = issue_op.headers
        pull_op = pull_op.headers
        
        if ('link' in issue_op):
            num_total = find_output(issue_op['link'])

        if ('link' in pull_op):
            num_pulls = find_output(pull_op['link'])

        
        return num_total,(num_total - num_pulls)

    

    return 0,0




def getForksSize(repo_owner,repo_name):

    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}'
    r = getUrl(url)
    if not r:
        return 0,0


    r = r.json()
    forks = 0
    size  = 0
    if 'forks_count'  in r:
        forks = r['forks_count']

    if 'size'  in r:
        size = r['size']

    return forks,size


def getIssues(repo_owner,repo_name,num_total,num_closed):
    df_issues = pd.DataFrame()
    perPage = 100
    numPages = (num_total//perPage) + 1
    for page in range(1,numPages + 1):
        url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues?state=closed&per_page={perPage}&page={page}'
        result = getUrl(url)
        
        if not result:
            continue

        result = result.json()
        df_issues_now = pd.DataFrame(result)
        df_issues_now = df_issues_now.reset_index(drop = True)

        df_issues = df_issues.append(df_issues_now,ignore_index=True)


    if 'pull_request' in df_issues.columns.tolist():
        df_issues = df_issues[df_issues['pull_request'].isna()]
    
    df_issues = df_issues.reset_index(drop=True)
    return df_issues



    
def getIssueMetrics(repo_owner,repo_name):
    #get total issue count
    num_total,num_closed = getTotalCount(repo_owner,repo_name)


    print("TOTAL PR + ISSUES: ",num_total)
    print("TOTAL CLOSED ISSUES: ",num_closed)

    if num_closed != 0:
        df_issues = getIssues(repo_owner,repo_name,num_total,num_closed)

        return num_closed,df_issues

    return 0,pd.DataFrame()

def getLatency(num_closed_issues):
    if not num_closed_issues.empty:
        time_diff = pd.to_datetime(num_closed_issues['closed_at']) - pd.to_datetime(num_closed_issues['created_at'])
        return time_diff.mean()

    return 0

def getComments(num_closed_issues):
    if not num_closed_issues.empty:
        comments = num_closed_issues['comments']
        return comments.mean()

    return 0


def get_age(year,month,day):
    time_created = datetime.datetime(year,month,day)
    time_now = datetime.datetime(2021,10,31)

    age = (time_now - time_created).days
    return (age)

def save_checkpoint(out_df,row_val):
    if (row_val % 100 == 0 and row_val != 0):
        out_df = out_df.rename(columns = dict(enumerate(['url','num_contributors','total closed issued','total issues','avg contributor per issue','average latency','filename'])))
        out_df.to_csv(f"{CHECKPOINT_DIR}{INPUT_CSV_FILE[:-4]}_ROW_{row_val}.csv",index = False)


def get_repo_features(url,repo_owner,repo_name,day,month,year,filename):

    df_repo = pd.DataFrame(columns = cols)
    print("For the URL: ",url)

    forks,proj_size = getForksSize(repo_owner,repo_name)
    contributors = get_contributors(repo_owner,repo_name)
    num_closed_issues,all_closed_issues = getIssueMetrics(repo_owner,repo_name)
    avg_latency = getLatency(all_closed_issues)
    avg_comments = getComments(all_closed_issues)
    avg_created_out,avg_forks_out = get_cross_dev(repo_owner,repo_name,url,day,month,year)

    print("Num forks: ",forks)
    print("Project Size in KB:",proj_size)
    print("Contributors:",contributors)
    print("Avg Created OUT: ",avg_created_out)
    print("Avg Forks OUT: ",avg_forks_out)
    print("Total closed issues: ",num_closed_issues)
    print("Avg Latency: ",avg_latency)
    print("Avg comments per issue:",avg_comments)

    df_repo['User'] = [repo_owner]
    df_repo['Name'] = [repo_name]
    df_repo['Url'] = [url]
    df_repo['Forks'] = [forks]
    df_repo['Project Size'] = [proj_size]
    df_repo['Contributors'] = [contributors]
    df_repo['Avg Created Repos Out'] = [avg_created_out]
    df_repo['Avg Forked Repos Out'] = [avg_forks_out]
    df_repo['Total Closed Issues'] = [num_closed_issues]
    df_repo['Avg Latency'] = [avg_latency]
    df_repo['Avg Comments'] = [avg_comments]
    df_repo['Day'] = [day]
    df_repo['month'] = [month]
    df_repo['year'] = [year]
    df_repo['Age'] = [get_age(year,month,day)]
    df_repo['filename'] = [filename]

    
    df_repo = df_repo.reset_index(drop = True)

    

    return df_repo
    

    # all_closed_issues.to_csv("issues.csv",index = False)
    # print("Possible dataframe of issues is saved into csv now\n")
########
# MAIN #
########


start_time = time.time()
INPUT_CSV_FILE = 'final_bunch_merge.csv'

df = pd.read_csv(INPUT_CSV_FILE)
res_df = pd.DataFrame()

for row in range(START_LIMIT,START_LIMIT + SAMPLE_LIMIT):
    repo_owner = df.iloc[row]["User"]
    repo_name = df.iloc[row]["Name"]
    repo_url = df.iloc[row]["Url"]
    day = df.iloc[row]['Day']
    month = df.iloc[row]['month']
    year = df.iloc[row]['year']
    filename = df.iloc[row]['filename']

    print("REPO ",row+1)
    df_repo = get_repo_features(repo_url,repo_owner,repo_name,day,month,year,filename)
    

    res_df = res_df.append(df_repo,ignore_index=True)
    save_checkpoint(res_df,row)
    print('='*100)


res_df.to_csv("final_issues_features.csv",index=False)



# repo_name = 'swift-algorithms'
# repo_owner = 'apple'
# url = 'https://github.com/apple/swift-algorithms.git'
# day = '01'
# month = '10'
# year = '2020'

# #find the forks and size of project
# print("For the URL: ",url)

# forks,proj_size = getForksSize(repo_owner,repo_name)
# contributors = get_contributors(repo_owner,repo_name)
# num_closed_issues,all_closed_issues = getIssueMetrics(repo_owner,repo_name)
# avg_latency = getLatency(all_closed_issues)
# avg_comments = getComments(all_closed_issues)
# avg_created_out,avg_forks_out = get_cross_dev(repo_owner,repo_name,url,day,month,year)

# print("Num forks: ",forks)
# print("Project Size in KB:",proj_size)
# print("Contributors:",contributors)
# print("Avg Created OUT: ",avg_created_out)
# print("Avg Forks OUT: ",avg_forks_out)
# print("Total closed issues: ",num_closed_issues)
# print("Avg Latency: ",avg_latency)
# print("Avg comments per issue:",avg_comments)

# all_closed_issues.to_csv("issues.csv",index = False)
# print("Possible dataframe of issues is saved into csv now\n")


end_time = time.time()
diff = (end_time - start_time)/60.0
print("Minutes elapsed: ",round(diff,2))



