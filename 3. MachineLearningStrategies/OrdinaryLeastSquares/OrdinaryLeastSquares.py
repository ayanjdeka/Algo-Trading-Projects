import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from pandas_datareader import data
import yfinance as yf


def create_classification_trading_condition(df):
    df['Open-Close'] = df.Open - df.Close
    df['High-Low'] = df.High - df.Low
    df = df.dropna()
    X = df[['Open-Close', 'High-Low']]
    Y = np.where(df['Close'].shift(-1) > df['Close'], 1, -1)
    return (df, X, Y)

def create_regression_trading_condition(df):
    df['Open-Close'] = df.Open - df.Close
    df['High-Low'] = df.High - df.Low
    df['Target'] = df['Close'].shift(-1) - df['Close']
    df = df.dropna()
    X = df[['Open-Close', 'High-Low']]
    Y = df[['Target']]
    return (df, X, Y)
def create_train_split_group(X, Y, split_ratio=0.8):
    return train_test_split(X, Y, shuffle=False, train_size=split_ratio)


start_date = '2018-01-01'
end_date = '2023-01-01'
google_data_frame = yf.download('GOOG', start = start_date, end = end_date)

google_data_frame, X, Y = create_regression_trading_condition(google_data_frame)

X_train,X_test,Y_train,Y_test=create_train_split_group(X,Y,split_ratio=0.8)

from sklearn import linear_model

ols = linear_model.LinearRegression()
ols.fit(X_train,Y_train)
print('Coeffecients: \n', ols.coef_)

google_data_frame['Predicted_Signal'] = ols.predict(X)
google_data_frame['GOOG_Returns'] = np.log(google_data_frame['Close'] / google_data_frame['Close'].shift(1))

print(google_data_frame.head())

def calculate_return(df, split_value, symbol):
    goog_return = df[split_value:]['%s_Returns' % symbol].cumsum() * 100
    df['Strategy_Returns'] = df['%s_Returns' % symbol] * df['Predicted_Signal'].shift(1)

    return goog_return

def calculate_strategy_return(df, split_value, symbol):
    strategy_return = df[split_value:]['Strategy_Returns'].cumsum() * 100
    return strategy_return


goog_return = calculate_return(
    google_data_frame, split_value=len(X_train), symbol='GOOG')
strategy_return = calculate_strategy_return(
    google_data_frame, split_value=len(X_train), symbol='GOOG')


def plot_shart(cum_symbol_return, cum_strategy_return, symbol):
    plt.figure(figsize=(10, 5))
    plt.plot(cum_symbol_return, label='%s Returns' % symbol)
    plt.plot(cum_strategy_return, label='Strategy Returns')
    plt.legend()
    plt.show()

plot_shart(goog_return, strategy_return, symbol='GOOG')

def sharpe_ratio(symbol_returns, strategy_returns):
    strategy_std = strategy_returns.std()
    sharpe = (strategy_returns - symbol_returns) / strategy_std
    return sharpe.mean()

print(sharpe_ratio(strategy_return,goog_return))

from sklearn.metrics import mean_squared_error, r2_score

# The mean squared error
print("Mean squared error: %.2f"
      % mean_squared_error(Y_train, ols.predict(X_train)))
# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % r2_score(Y_train, ols.predict(X_train)))

# The mean squared error
print("Mean squared error: %.2f"
      % mean_squared_error(Y_test, ols.predict(X_test)))
# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % r2_score(Y_test, ols.predict(X_test)))


