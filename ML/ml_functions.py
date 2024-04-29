import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import requests
import os
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from skgarden import RandomForestQuantileRegressor
from scipy.stats import boxcox
from scipy.special import inv_boxcox
import plotly.express as px
from plotly.io import write_html
from datetime import date, timedelta
from datetime import datetime
import json




def get_historical_data(ticker, days_previous):
    
    """
    This function takes a ticker symbol and a number for the amount of days you would like
    pull historical data on.  It will return a dataframe with Date as the index and close for closing
    prices as the column. The data is pull from Cryptocompare's API.
    """
    
    url = "https://min-api.cryptocompare.com/data/v2/histoday"
    key = os.getenv("cryptocompare_key")
    payload = {
    "api_key": key,
    "fsym": ticker,
    "tsym": "USD",
    "limit": days_previous
    }
    result = requests.get(url, params = payload).json()
    coin_df = pd.DataFrame(result['Data']['Data'])
    coin_df['time'] = pd.to_datetime(coin_df['time'], unit = 's')
    coin_df = coin_df[['close', 'time']]
    coin_df = coin_df.rename(columns = {'time': 'Date'}).set_index('Date')
    return coin_df

def get_arima_forecast(ticker):
    
    """
    This function takes a ticker symbol as an argument that will be passed to get_historical_data().
    Once it receives the dataframe from get_historical_data, ARIMA models will be run on the selected
    ticker.  This function will return 2 dataframes.  One with the initial dataframe from get_historical_data
    and one dataframe that has predictions, upper limits of confidence interval, and lower limits of confidence interval.
    """
    
    days_previous_dict = {'BTC': 730, 'ETH': 730, 'LTC': 730}
    days_previous = days_previous_dict[ticker]
    coin_df = get_historical_data(ticker, days_previous)
    transformed_data, lmda = boxcox(coin_df)
    transformed_data = transformed_data.flatten().tolist()
    transformed_df = coin_df.copy()
    transformed_df['close'] = transformed_data
    if ticker == 'BTC':
        model = SARIMAX(transformed_df, order = ((1,0,0,1),0,1), freq = 'D')
    elif ticker == 'ETH':
        model = SARIMAX(transformed_df, order = (1,1,(0,1)), freq = 'D')
    else:
        model = SARIMAX(transformed_df, order = ((1,0,0,0,0,0,0,0,1),1,1), freq = 'D')
    model_fit = model.fit(disp = False)
    conf_int = model_fit.get_forecast(5, converged = False)
    confidence_intervals = conf_int.conf_int()
    confidence_intervals = inv_boxcox(confidence_intervals, lmda)
    start = days_previous + 1
    end = days_previous + 6
    predictions = model_fit.predict(start= start, end = end, converged = False)
    predicted_close = inv_boxcox(predictions, lmda)
    final_df = confidence_intervals.copy()
    final_df['Predicted Price'] = predicted_close
    final_df = final_df.round(2)
    final_df = final_df.reset_index()
    final_df = final_df.rename(columns = {'index': 'Date'})
    return final_df, coin_df

def get_arima_forecast_plot():
    
    """
    This function requires no arguments at this time since we are only forecasting for BTC, ETH, and LTC.
    It will call the get_arima_forecast() function and will return an .html file for the plots and
    a .json file that is used to load the values in the dashboard.
    """
    ticker_list = ['BTC', 'ETH', 'LTC']
    for ticker in ticker_list:
        forecast_df, coin_df = get_arima_forecast(ticker)
        fig = px.line(forecast_df, x ='Date', y = 'Predicted Price')
        fig.update_xaxes(nticks = 5)
        fig.update_yaxes(automargin=True)
        fig.update_layout(title_text = f'{ticker} ARIMA Model (Autoregressive Integrated Moving Average)', autosize = True, height = 900, width = 930, template = 'plotly_dark')
        write_html(fig, f'./web/{ticker}Arima.html')
        table_df = forecast_df.copy()   
        todays_price = coin_df['close'][-1]
        tommorows_prediction = table_df['Predicted Price'][0]
        upper_limit = table_df['upper close'][0]
        lower_limit = table_df['lower close'][0]
        price_dict = {'todays_price': todays_price, 'tommorows_prediction': tommorows_prediction, 'upper_limit': upper_limit, 'lower_limit': lower_limit}
        with open(f'./web/{ticker}Arima.json', 'w') as fp:
            json.dump(price_dict, fp)

def get_random_forest_df():
    
    """
    This function does not require any parameters at this time.  It will call get_historical_data to retrive
    a dataframe for BTC,ETH, and LTC.  It will return a dataframe for training a model.
    """
    
    end_date = date.today().isoformat()
    delta = timedelta(730)
    start_date = (date.today() - delta).isoformat()
    url = 'https://api.exchangeratesapi.io/history'
    payload = {
    "start_at": start_date,
    "end_at": end_date,
    "symbols": "CNY,JPY,EUR",
    "base": "USD"
    }
    result = requests.get(url, params = payload).json()
    rate_df = pd.DataFrame(result['rates']).transpose()
    rate_df = rate_df.sort_index()
    rate_df.index = pd.to_datetime(rate_df.index, format = '%Y-%m-%d')
    btc_price = get_historical_data('BTC', 730)
    btc_price = btc_price.rename(columns = {'close': 'BTC'})
    eth_price = get_historical_data('ETH', 730)
    eth_price = eth_price.rename(columns = {'close': 'ETH'})
    ltc_price = get_historical_data('LTC', 730)
    ltc_price = ltc_price.rename(columns = {'close': 'LTC'})
    coin_df = btc_price
    coin_df['LTC'] = ltc_price
    coin_df['ETH'] = eth_price
    combined_df = pd.concat([coin_df, rate_df], axis = 1 )
    combined_df['EUR'] = combined_df['EUR'].ffill()
    combined_df['CNY'] = combined_df['JPY'].ffill()
    combined_df['JPY'] = combined_df['CNY'].ffill()
    combined_df = combined_df.reset_index()
    delta = timedelta(1)
    last_day = combined_df['index'].iloc[-1]
    add_row_date = (last_day + delta).isoformat()
    df2 = pd.DataFrame([[add_row_date,0,0,0,0,0,0]], columns= ['index','BTC','LTC','ETH','EUR','CNY','JPY'])
    combined_df = combined_df.append(df2, ignore_index = True)
    combined_df = combined_df.set_index('index')
    combined_df['BTC_Previous_Day'] = combined_df['BTC'].shift(1)
    combined_df['LTC_Previous_Day'] = combined_df['LTC'].shift(1)
    combined_df['ETH_Previous_Day'] = combined_df['ETH'].shift(1)
    combined_df['EUR_Previous_Day'] = combined_df['EUR'].shift(1)
    combined_df['CNY_Previous_Day'] = combined_df['CNY'].shift(1)
    combined_df['JPY_Previous_Day'] = combined_df['JPY'].shift(1)
    combined_df = combined_df.drop(columns = ['EUR', 'CNY', 'JPY'])
    combined_df = combined_df.dropna()
    return combined_df

def get_rf_ensemble_model(ticker):
    
    """
    This function requires a ticker as an argument to be passed when calling the function.  It trains a Random Forest Regressor.
    It will return a dataframe with actual values, predicted values, lower limits of confidence in interval, and upper limits of
    confidence interval.
    """
    
    combined_df = get_random_forest_df()
    X = combined_df.drop(columns = ['BTC', 'LTC', 'ETH'])
    if ticker == 'BTC':    
        y = combined_df['BTC']
    elif ticker == 'ETH':
        y = combined_df['ETH']
    else:
        y = combined_df['LTC']
    test_start_point = len(X) - 5
    X_train = X[:test_start_point]
    y_train = y[:test_start_point]
    X_test = X[test_start_point:]
    y_test = y[test_start_point:]
    regressor = RandomForestQuantileRegressor(random_state = 0, n_estimators = 500)
    model = regressor.fit(X_train, y_train)
    predictions = model.predict(X_test)
    uppers = model.predict(X_test, quantile = 98.5)
    lowers = model.predict(X_test, quantile = 2.5)
    actuals = pd.DataFrame(y_test)
    actuals_vs_predictions = actuals.copy()
    actuals_vs_predictions['lower close'] = lowers.round(2)
    actuals_vs_predictions['upper close'] = uppers.round(2)
    actuals_vs_predictions['Predictions'] = predictions.round(2)
    actuals_vs_predictions = actuals_vs_predictions.reset_index()
    return actuals_vs_predictions

def get_rf_ensemble_plot():
    
    """
    This function does not take any arguments because we are only modeling for BTC, ETH, and LTC at this time.
    The function will return a plot in a .html file and values in a .json file.
    
    """
    
    
    ticker_list = ['BTC', 'ETH', 'LTC']
    for ticker in ticker_list:
        forecast_df = get_rf_ensemble_model(ticker)
        fig = px.line(forecast_df, x = 'index', y = 'Predictions')
        fig.update_xaxes(nticks = 5, title = 'Date')
        fig.update_yaxes(automargin=True, title = 'Predicted Price')
        fig.update_layout(autosize = True, height = 900, width = 930, title_text = f'{ticker} Random Forest Ensemble', template = 'plotly_dark')
        write_html(fig, f'./web/{ticker}RFEnsemble.html')
        todays_price = forecast_df[f'{ticker}'][3]
        tommorows_prediction = forecast_df['Predictions'][4]
        upper_limit= forecast_df['upper close'][4]
        lower_limit = forecast_df['lower close'][4]
        price_dict = {'todays_price': todays_price, 'tommorows_prediction': tommorows_prediction, 'upper_limit': upper_limit, 'lower_limit': lower_limit}
        with open(f'./web/{ticker}RFEnsemble.json', 'w') as fp:
            json.dump(price_dict, fp)