import numpy as np
from pandas.core.arrays.categorical import factorize_from_iterable
import config
from binance.client import Client
from binance.enums import *
import datetime
import requests
import time
import ta
import pandas as pd

from logs import writeLog


client = Client(config.API_KEY, config.API_SECRET) #it takes two parameter, first one api_key and second api_secret_key, i will define that in configuration file

def getminutedata(SYMBOL, TIME_PERIOD, min):
    try:
      
        res = client.get_historical_klines(SYMBOL,TIME_PERIOD,min+' min ago UTC')
        frame = pd.DataFrame(res)
        frame = frame.iloc[:,:6]
        frame.columns = ["Time","Open","High","Low","Close","Volume"]
        frame = frame.set_index('Time')
        frame.index = pd.to_datetime(frame.index,unit='ms')
        frame = frame.astype(float)
        return frame

        #now we can either save the response or convert it to numpy array , converting is more reasonable
    except Exception as e:
        writeLog("an exception occured - {}".format(e))
        return None

class Signals:
    def __init__(self,df, lags):
        self.df = df
        self.lags = lags

    def gettrigger(self):
        dfx = pd.DataFrame()
        for i in range(self.lags + 1):
            mask = (self.df['%K'].shift(i) < 20) & (self.df['%D'].shift(i) < 20)
            dfx = dfx.append(mask, ignore_index=True)
        return dfx.sum(axis=0)

    def decide(self):
        self.df['trigger'] = np.where(self.gettrigger(), 1, 0)
        self.df['Buy'] = np.where((self.df.trigger) &
        (self.df['%K'].between (20,80)) & (self.df ['%D'].between (20,80))
        & (self.df.rsi > 50) & (self.df.macd > 0), 1, 0)

def applytechnicals(df):  
    df['%K'] = ta.momentum.stoch(df.High,df.Low,df.Close,window=14,smooth_window=3)   
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close,window=14)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df.dropna(inplace=True)

def strategy(pair, qty, open_position=False):
    df = getminutedata(pair, '1m', '100')
    applytechnicals(df)
    inst = Signals(df, 25)
    inst.decide()
    print(f'current Close is '+str(df.Close.iloc[-1]))
    print(df.iloc[-1])
    if df.Buy.iloc[-1]:
        #order = client.create_order(symbol=pair,side='BUY',type='MARKET', quantity=qty)
        #print(order)
        writeLog('buy order ----')
        buyprice = float(df.Close.iloc[-1]) #float(order['fills'][0]['price'])
        open_position = True
    while open_position:
        time.sleep(1)
        df = getminutedata(pair, '1m','2')
        print(f'current Close: '+ str(df.Close. iloc(-1)))
        print(f'current Target: '+ str(buyprice * 1.005))
        print (f'current Stop is: ' + str(buyprice * 0.995))
        if df.Close[-1] <= buyprice * 0.995 or df.Close[-1] >= 1.005 * buyprice:
            #order = client.create_order(pair,side='SELL',type='MARKET',quantity=qty)
            #print(order)
            writeLog('sell order ----')
            break


while True:
    strategy('ADAUSDT',10)
    time.sleep(1)
