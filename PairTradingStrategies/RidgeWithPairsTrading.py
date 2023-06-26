from sklearn.linear_model import Ridge
from sklearn.linear_model import LinearRegression
import warnings
import pandas as pd
warnings.filterwarnings('ignore')
import yfinance as yf
import matplotlib.pyplot as plt
start_date = '1920-01-01'
end_date = '2024-01-01'
aapl_data_frame = yf.download('AAPL', start = start_date, end = end_date)
google_data_frame = yf.download('GOOG', start = start_date, end = end_date)

class RidgeRegressionModel(object):
    def __init__(self):
        self.df_result = pd.DataFrame(columns=['Actual', 'Predicted'])

    def get_model(self):
        return Ridge(alpha=0.5)

    def learn(self, df, ys, start_date, end_date, lookback_period=20):
        model = self.get_model()

        df.sort_index(inplace=True)
        for date in df[start_date:end_date].index:
            # Fit the model
            x = self.get_prices_since(df, date, lookback_period)
            y = self.get_prices_since(ys, date, lookback_period)
            model.fit(x, y.ravel())

            # Predict the current period
            x_current = df.loc[date].values
            [y_pred] = model.predict([x_current])

            # Store predictions
            new_index = pd.to_datetime(date, format='%Y-%m-%d')
            y_actual = ys.loc[date]
            self.df_result.loc[new_index] = [y_actual, y_pred]

    def get_prices_since(self, df, date_since, lookback):
        index = df.index.get_loc(date_since)
        return df.iloc[index-lookback:index]
    



df_x = pd.DataFrame({'GOOG': google_data_frame['Adj Close']})
apple_prices = aapl_data_frame['Adj Close']

ridge_reg_model = RidgeRegressionModel()
ridge_reg_model.learn(df_x, apple_prices, start_date='2020', 
                       end_date='2022', lookback_period=20)

plt.figure(figsize=(12, 8))
plt.plot(ridge_reg_model.df_result['Actual'], label= 'Apple Actual Returns')
plt.plot(ridge_reg_model.df_result['Predicted'], label = 'Strategy Returns')
plt.legend()
plt.title('Apple Returns Trained on Google Data and Using Ridge')
plt.show()

