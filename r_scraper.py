#importing libraries
import praw
import pandas as pd
import datetime as dt
import detectEnglish as de
from langdetect import detect
import yfinance as yf
import requests
import json
import statistics 
from statistics import mode 
from collections import Counter
from detectEnglish import *

#function to make our lives easier
def most_common(List): 
    return(mode(List))

#allowing pandas to display the all_titles table
pd.set_option("display.max_rows", None, "display.max_columns", None)

#reddit login
reddit = praw.Reddit(client_id='', \
                     client_secret='', \
                     user_agent='', \
                     username='', \
                     password='')

#subreddit
subreddit = reddit.subreddit('wallstreetbets')
top_subreddit = subreddit.new(limit = 1000)

topics_dict = { "title":[], \
                "score":[], \
                "created":[], \
                "body":[]}

for submission in top_subreddit:
    topics_dict["title"].append(submission.title)
    topics_dict["score"].append(submission.score)
    topics_dict["created"].append(submission.created)
    topics_dict["body"].append(submission.selftext)

topics_data = pd.DataFrame(topics_dict)

titles = topics_data['title'].tolist()
all_titles = ' '.join(titles)

all_titles = de.removeNonLetters(all_titles)
all_titles = all_titles.split(" ")
new_all_titles = []

#filtering out common phrases that could throw off the algorithm
for i in all_titles:
    try:
        if i.isupper() == True and len(i) < 5 and i != 'DD' and i != 'THE' and i != 'WSB' and i != 'MOON' and i != 'A' and i != 'I':
           new_all_titles.append(i)
    except:
        pass

#getting information on a ticker
for i in new_all_titles:
    try:
        r = requests.get('https://finnhub.io/api/v1/stock/profile2?symbol=' + i + '&token=bub9fhv48v6pmjua57tg')
        r = r.json()
        r = r['country']
    except:
        new_all_titles.remove(i)

c = Counter(new_all_titles)
common = c.most_common(5)
i = 0
tickers = []
popularity_main = {}
popularity = []

#appending the top 5 most popular stocks
while i < 5:
    a = common[i]
    tickers.append(a[0])
    popularity.append(a[1])
    popularity_main.update({tickers[i] : popularity[i]})
    i += 1

print(popularity_main)

#start of section 2, sentiment analysis

# Import libraries
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
from IPython import get_ipython
ipy = get_ipython()
if ipy is not None:
    ipy.run_line_magic('matplotlib', 'inline')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
pd.set_option("display.max_rows", None, "display.max_columns", None)
finwiz_url = 'https://finviz.com/quote.ashx?t='
parsed_news = []
news_tables = {}

for ticker in tickers:
    url = finwiz_url + ticker
    req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
    response = urlopen(req)    
    #read the contents of the file
    html = BeautifulSoup(response, features="lxml")
    news_table = html.find(id='news-table')
    #add the table to the dictionary
    news_tables[ticker] = news_table


#iterate through the news
for file_name, news_table in news_tables.items():
    if news_table != None:
    #iterate through all tr tags in 'news_table'
        for x in news_table.findAll('tr'):
        #read the text from each tr tag into text
            text = x.a.get_text() 
        #split text in the td tag into a list
            date_scrape = x.td.text.split()
        #if the length of 'date_scrape' is 1, load 'time' as the only element

            if len(date_scrape) == 1:
                time = date_scrape[0]
            
        #else load 'date' as the 1st element and 'time' as the second
            else:
                date = date_scrape[0]
                time = date_scrape[1]
        #extract the ticker from the file name, get the string up to the 1ist '_'
            ticker = file_name.split('_')[0]
        
        #append ticker, date, time and headline as a list to the 'parsed_news' list
            parsed_news.append([ticker, date, time, text])
        


vader = SentimentIntensityAnalyzer()

# Set column names
columns = ['ticker', 'date', 'time', 'headline']

#convert the parsed_news list into a DataFrame called 'parsed_and_scored_news'
parsed_and_scored_news = pd.DataFrame(parsed_news, columns=columns)

#iterate through the headlines and get the polarity scores using vader
scores = parsed_and_scored_news['headline'].apply(vader.polarity_scores).tolist()

#convert the 'scores' list of dicts into a DataFrame
scores_df = pd.DataFrame(scores)

#join the DataFrames of the news and the list of dicts
parsed_and_scored_news = parsed_and_scored_news.join(scores_df, rsuffix='_right')

#convert the date column from string to datetime
parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news.date).dt.date

parsed_and_scored_news.head()
plt.rcParams['figure.figsize'] = [10, 6]

#group by date and ticker columns from scored_news and calculate the mean
mean_scores = parsed_and_scored_news.groupby(['ticker','date']).mean()

#unstack the column ticker
mean_scores = mean_scores.unstack()

#get the cross-section of compound in the 'columns' axis
mean_scores = mean_scores.xs('compound', axis="columns").transpose()

#plot a bar chart with pandas
mean_scores.plot(kind = 'bar')

print(mean_scores)

sentiment = {}

for x in tickers:
    ii = mean_scores.loc[:,x]
    if pd.isnull(ii.iloc[-1]) == False and ii.iloc[-1] != 0:
        ms = ii.iloc[-1]
    elif pd.isnull(ii.iloc[-2]) == False and ii.iloc[-2] != 0:
        ms = ii.iloc[-2]
    elif pd.isnull(ii.iloc[-3]) == False and ii.iloc[-3] != 0: 
        ms = ii.iloc[-3]
    elif pd.isnull(ii.iloc[-4]) == False and ii.iloc[-4] != 0:
        ms = ii.iloc[-4]
    elif pd.isnull(ii.iloc[-5]) == False and ii.iloc[-5] != 0:
        ms = ii.iloc[-5]
    elif pd.isnull(ii.iloc[-6]) == False and ii.iloc[-6] != 0:
        ms = ii.iloc[-6]
    elif pd.isnull(ii.iloc[-7]) == False and ii.iloc[-7] != 0:
        ms = ii.iloc[-7]
    elif pd.isnull(ii.iloc[-8]) == False and ii.iloc[-8] != 0:
        ms = ii.iloc[-8]
    sentiment.update({x : ms})
    
print(sentiment)

scores = {}

#rudimentary algorithm to determine 'score' of a ticker
for a in tickers:
    r = requests.get('https://finnhub.io/api/v1/quote?symbol=' + a + '&token=bub9fhv48v6pmjua57tg')
    r = r.json()
    r = r['c']
    scores.update({a : popularity.get(a)*sentiment.get(a)})
    scores[a] = scores[a]*5000
    scores[a] = round(scores[a]/r)

print(scores)

#optional section 3, using alpaca to execute trades

import alpaca_trade_api as tradeapi

#authentication and connection details
api_key = ''
api_secret = ''
base_url = 'https://paper-api.alpaca.markets'

#instantiate REST API
api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

for a in tickers:
    if scores[a] < 0:        
        scores[a] = scores[a]*-1
    if scores[a] > 0:
        api.submit_order(symbol=a, 
		qty=scores[a], 
		side='buy', 
		time_in_force='gtc', 
		type='market')

print('Program completed')

    
