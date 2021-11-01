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

#############
# Constants #
#############

MONTH = '01'
YEAR = '2020'
URL = "https://api.github.com/search/repositories?q="  # The basic URL to use the GitHub API
#QUERY = "user:rsain"  # The personalized query (for instance, to get repositories from user 'rsain')
#SUB_QUERIES = ["+created%3A2019-09-30..2020-09-30"]  # Different sub-queries if you need to collect more than 1000 elements
#2019-09-30..2020-09-30
PARAMETERS = "&per_page=100"  # Additional parameters for the query (by default 100 items per page)
DELAY_BETWEEN_QUERIES = 60  # The time to wait between different queries to GitHub (to avoid be banned)
OUTPUT_FOLDER = "GitHub-Crawler/"  # Folder where ZIP files will be stored
OUTPUT_CSV_FILE = "repositories_Terry.csv"  # Path to the CSV file generated as output
MONTH_TO_DAY = {'01':31, '02':27, '03':31, '04':30, '05':31, '06':30, '07':31, '08':31, '09':30, '10':31, '11':30, '12':31}

#############
# Functions #
#############

def getUrl(url):
    """ Given a URL it returns its body """
    response = requests.get(url)
    if response.status_code != 200:
        return False 
    return response.json()

def build_url(day):

    curr_day = str(day).zfill(2)

    date_range = '+created%3A' + YEAR + '-' + MONTH + '-' + curr_day 
    return URL + date_range + PARAMETERS
########
# MAIN #
########

# To save the number of repositories processed
countOfRepositories = 0

# Output CSV file which will contain information about repositories
csv_file = open(OUTPUT_CSV_FILE, 'w')
repositories = csv.writer(csv_file, delimiter=',')
repositories.writerow(["Username","Repository name","URL"])
# Run queries to get information in json format and download ZIP file for each repository
# Obtain the number of pages for the current subquery (by default each page contains 100 items)
for day in range(1, MONTH_TO_DAY[MONTH]):
    url = build_url(day)

    print('Day is ', day, 'url is: ', url)
    data = json.loads(json.dumps(getUrl(url)))
    numberOfPages = int(math.ceil(data['total_count'] / 100.0))
    print("No. of pages = " + str(numberOfPages))

    # Results are in different pages
    for currentPage in range(1, numberOfPages + 1):
        print("Processing page " + str(currentPage) + " of " + str(numberOfPages) + " ...")
        url = build_url(day) + "&page=" + str(currentPage)
        json_response = getUrl(url)
        if not json_response:
            break
        data = json.loads(json.dumps(json_response))

        # Iteration over all the repositories in the current json content page
        if 'items' in data:
            for item in data['items']:
                # Obtain user and repository names
                user = item['owner']['login']
                repository = item['name']
                url = item['clone_url']
                repositories.writerow([user, repository,url])
                # Update repositories counter
                countOfRepositories = countOfRepositories + 1
        if not currentPage%8:
            time.sleep(DELAY_BETWEEN_QUERIES)
    time.sleep(DELAY_BETWEEN_QUERIES)


print("DONE! " + str(countOfRepositories) + " repositories have been processed.")
csv_file.close()
