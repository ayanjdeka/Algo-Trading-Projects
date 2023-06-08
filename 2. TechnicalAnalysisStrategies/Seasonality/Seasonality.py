import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data
import yfinance as yf
start_date = '2018-01-01'
end_date = '2023-01-01'
google_data_frame = yf.download('GOOG', start = start_date, end = end_date)

goog_monthly_return = google_data_frame['Adj Close'].pct_change().groupby(
  [google_data_frame['Adj Close'].index.year,
   google_data_frame['Adj Close'].index.month]).mean()


def plot_rolling_statistics_ts(ts, titletext,ytext, window_size=12):
    ts.plot(color='red', label='Original', lw=0.5)
    ts.rolling(window_size).mean().plot(color='blue',label='Rolling Mean')
    ts.rolling(window_size).std().plot(color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.ylabel(ytext)
    plt.title(titletext)
    plt.show(block=True)


plot_rolling_statistics_ts(goog_monthly_return[1:],'GOOG prices rolling mean and standard deviation','Monthly return')

