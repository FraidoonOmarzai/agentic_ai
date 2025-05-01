# tool: fetch stock price

from typing import Union, Dict
import datetime as dt
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
from ta.volume import volume_weighted_average_price
from langchain_core.tools import tool


from typing import Union, List, Dict
from langchain_core.tools import tool
import requests
import os

@tool
def get_stock_prices(ticker: str) -> Union[Dict, str]:
    """Fetches historical stock price data and technical indicators for a given ticker."""
    try:
        data = yf.download(
            ticker,
            start=dt.datetime.now() - dt.timedelta(weeks=12),
            end=dt.datetime.now(),
            interval='1wk'
        )

        if data.empty:
            return f"No data found for ticker: {ticker}"

        # reset index so we can access 'Date' as a column
        data.reset_index(inplace=True)
        data['Date'] = data['Date'].astype(str)

        # Technical Indicators - computed on closing prices
        indicators = {}

        # RSI detects overbought/oversold conditions
        # Show last 12 weeks of indicators for a 3-month span
        rsi_series = RSIIndicator(
            data['Close'].squeeze(), window=14).rsi().iloc[-12:]
        indicators["RSI"] = dict(
            zip(data['Date'].iloc[-12:], map(lambda x: round(x, 2), rsi_series)))

        # Compares current price to a range of previous prices
        # Another momentum indicator — complements RSI
        sto_series = StochasticOscillator(data['High'].squeeze(), data['Low'].squeeze(
        ), data['Close'].squeeze(), window=14).stoch().iloc[-12:]
        indicators["Stochastic_Oscillator"] = dict(
            zip(data['Date'].iloc[-12:], map(lambda x: round(x, 2), sto_series)))

        # MACD is a trend-following indicator (difference of two EMAs)
        # Useful for spotting trend reversals
        macd = MACD(data['Close'].squeeze())
        macd_series = macd.macd().iloc[-12:]
        indicators["MACD"] = dict(
            zip(data['Date'].iloc[-12:], map(lambda x: round(x, 2), macd_series)))

        # Signal line is a smoothed version of MACD used to generate buy/sell signals
        macd_signal_series = macd.macd_signal().iloc[-12:]
        indicators["MACD_Signal"] = dict(
            zip(data['Date'].iloc[-12:], map(lambda x: round(x, 2), macd_signal_series)))

        # VWAP helps traders understand average price based on volume
        # Commonly used by institutions to assess fair value
        vwap_series = volume_weighted_average_price(
            data['High'].squeeze(), data['Low'].squeeze(), data['Close'].squeeze(), volume=data['Volume'].squeeze()
        ).iloc[-12:]
        indicators["vwap"] = dict(
            zip(data['Date'].iloc[-12:], map(lambda x: round(x, 2), vwap_series)))

        return {
            'stock_price': data.to_dict(orient='records'),
            'indicators': indicators
        }

    except Exception as e:
        return f"Error fetching price data: {str(e)}"
    
    
    

@tool
def get_financial_metrics(ticker: str) -> Union[Dict, str]:
    """Fetches key financial ratios for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return f"No financial data found for ticker: {ticker}"

        def safe_get(key: str) -> Union[float, str]:
            value = info.get(key)
            return round(value, 3) if isinstance(value, (int, float)) else "N/A"

        return {
            'pe_ratio': safe_get('forwardPE'),
            'price_to_book': safe_get('priceToBook'),
            'debt_to_equity': safe_get('debtToEquity'),
            'profit_margins': safe_get('profitMargins'),
            'return_on_equity': safe_get('returnOnEquity'),
            'return_on_assets': safe_get('returnOnAssets'),
            'current_ratio': safe_get('currentRatio'),
            'quick_ratio': safe_get('quickRatio'),
            'gross_margins': safe_get('grossMargins'),
            'operating_margins': safe_get('operatingMargins')
        }

    except Exception as e:
        return f"Error fetching ratios: {str(e)}"
    
    



@tool
def get_stock_news(ticker: str) -> Union[List[Dict], str]:
    """
    Fetches recent news articles related to the given stock ticker using NewsAPI.
    Returns top 5 articles with title, description, source, and URL.
    """
    try:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={ticker}&"
            f"sortBy=publishedAt&"
            f"language=en&"
            f"pageSize=5&"
            f"apiKey=00131bbfeba447b7b6d338347ab19c15"
        )

        response = requests.get(url)
        if response.status_code != 200:
            return f"Failed to fetch news: {response.status_code} - {response.text}"

        data = response.json()
        articles = data.get("articles", [])
        if not articles:
            return f"No recent news found for ticker: {ticker}"

        return [
            {
                "title": a["title"],
                "description": a["description"],
                "source": a["source"]["name"],
                "url": a["url"],
                "published_at": a["publishedAt"]
            }
            for a in articles
        ]

    except Exception as e:
        return f"Error fetching news: {str(e)}"
