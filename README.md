# WSB-Scraper
Python program to scrape r/wallstreetbets for popular stocks, analyse external sentiment on the stocks and automatically buy those stocks.

Follow the first part of this guide: https://towardsdatascience.com/scraping-reddit-data-1c0af3040768 to create a Reddit application and input those values into the code. 

You may also need to create an Alpaca account  to access the API-enabled trading features.

Note: feel free to use my Finnhub and Finviz API keys (already in code) although it is recommended to create your own.

Technologies used:
 - Pandas to store data
 - PRAW to scrape Reddit
 - Requests to scrape Finnhub
 - UrlLib to scrape Finviz
 - NLTK's Vader to analyse the sentiment of articles
 - Alpace Trade API to execute orders based on signals
