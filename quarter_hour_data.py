import yfinance as yf
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk # Add this import statement if you need to download vader_lexicon
import datetime

nltk.download('vader_lexicon')

stocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ',
    'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS', 'PYPL', 'ADBE', 'NFLX', 'INTC',
    'CSCO', 'CMCSA', 'PEP', 'VZ', 'NKE', 'KO', 'MRK', 'PFE', 'XOM', 'T',
    'WFC', 'BA', 'ABBV', 'MCD', 'MDT', 'CRM', 'BMY', 'COST', 'LLY', 'ACN',
    'QCOM', 'TXN', 'UNP', 'LIN', 'NEE', 'HON', 'PM', 'IBM', 'AVGO', 'AMGN'
]

def get_intraday_data(stock):
    stock_data = yf.Ticker(stock)
    today = datetime.datetime.now().date()
    intraday_data = stock_data.history(interval='1m', start=today, end=today + datetime.timedelta(days=1))
    news_data = stock_data.news
    return intraday_data, news_data

def filter_today_news(news_data):
    today = datetime.datetime.now().date()
    today_news = [article for article in news_data if datetime.datetime.fromtimestamp(article['providerPublishTime']).date() == today]
    return today_news

def round_to_nearest_quarter_hour(dt):
    """Round a datetime object to the nearest 15 minutes."""
    discard = datetime.timedelta(minutes=dt.minute % 15, seconds=dt.second, microseconds=dt.microsecond)
    dt -= discard
    if discard >= datetime.timedelta(minutes=7.5):
        dt += datetime.timedelta(minutes=15)
    return dt

def get_sentiment_and_changes(news, stock, intraday_data):
    sia = SentimentIntensityAnalyzer()
    sentiments = []

    # Resample the intraday data to 15-minute intervals
    intraday_data_15m = intraday_data.resample('15min').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()

    for article in news:
        title = article['title']
        publish_time = datetime.datetime.fromtimestamp(article['providerPublishTime'])
        sentiment = sia.polarity_scores(title)['compound']

        # Round publish_time to the nearest 15-minute interval
        rounded_publish_time = round_to_nearest_quarter_hour(publish_time)

        # Find the stock price 15 minutes after the rounded publish time
        time_after_15m = (rounded_publish_time + datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        try:
            initial_price = intraday_data_15m.loc[rounded_publish_time.strftime('%Y-%m-%d %H:%M:%S')]['Close']
            final_price = intraday_data_15m.loc[time_after_15m]['Close']
            price_change = final_price - initial_price
            direction = 1 if price_change > 0 else 0
            sentiments.append((title, stock, sentiment, price_change, direction))
        except KeyError:
            print(f"Data not available for the interval ending at {time_after_15m} for stock {stock}")
    return sentiments

results = []
for stock in stocks:
    intraday_data, news_data = get_intraday_data(stock)
    today_news = filter_today_news(news_data)
    if today_news:
        sent = get_sentiment_and_changes(today_news, stock, intraday_data)
        results.extend(sent)

# Convert the results list of tuples to a DataFrame
results_df = pd.DataFrame(results, columns=['Title', 'Stock', 'Sentiment', 'Price Change', 'Direction'])

# Save the DataFrame to a CSV file
results_df.to_csv('data/news_results_15_min.csv', index=False)