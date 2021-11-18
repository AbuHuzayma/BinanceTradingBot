import talib,numpy
import config
from binance.client import Client
from binance.enums import *
import requests
import time
from logs import writeLog

from sqlitDB import insertOrderDB



client = Client(config.API_KEY, config.API_SECRET) #it takes two parameter, first one api_key and second api_secret_key, i will define that in configuration file

SYMBOL = "ADAUSDT" #taking this as a example
TIME_PERIOD= "1m" #taking 15 minute time period
LIMIT = "200" # taking 200 candles as limit
QNTY = 10 # we will define quantity over here

PROFIT = 0.02
STOPLOSS = 0.05

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

Order_ID = 1
interval_time = 1

#function to get data from binance
def get_data():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol={}&interval={}&limit={}".format(SYMBOL, TIME_PERIOD, LIMIT)
        res = requests.get(url)
        return res.json()
        #now we can either save the response or convert it to numpy array , converting is more reasonable
    except Exception as e:
        writeLog("an exception occured - {}".format(e))
        return None


#function to make order
def order(side, quantity, symbol,inprice,sellprice):
    try:
        #writeLog("sending order")
        #order = client.create_order(symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=quantity)
        res = insertOrderDB(Order_ID+1,'Ref-1',symbol,quantity,sellprice,side,'Market',sellprice-inprice,sellprice-inprice,side)
        #writeLog(order)
        return res
    except Exception as e:
        writeLog("an exception occured - {}".format(e))
        return False



#function main bot proccess
def main():
    RSI_LOW = 31
    IN_PRICE = 0
    in_position = False

    while True:
        message = get_data()
        if message is None:
            continue

        closes = []
        for each in message:
            closes.append(float(each[4]))


        np_closes = numpy.array(closes)
        rsi = talib.RSI(np_closes,RSI_PERIOD)
        last_rsi = rsi[-1]
        close = closes[-1]
    
        #Sell Proccess 
        if last_rsi > RSI_OVERBOUGHT:
            if in_position:
                SellPriceProfit = IN_PRICE + (IN_PRICE * PROFIT)#Profit price
                if IN_PRICE > 0 and SellPriceProfit < close:
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, QNTY, SYMBOL,IN_PRICE,SellPriceProfit)
                    if order_succeeded:
                        in_position = False
                        msgbay = "Succeeded Sell IN_PRICE:{} - SellPriceProfit:{} - RSI:{}".format(IN_PRICE,SellPriceProfit,last_rsi)
                        writeLog(msgbay)
                    else:
                        msgbay = "Can't Sell API Error IN_PRICE:{} - SellPriceProfit:{} - RSI:{}".format(IN_PRICE,SellPriceProfit,last_rsi)
                        writeLog(msgbay)
                    
                else:
                    msgbay = "Can't Sell No Profit IN_PRICE:{} - SellPriceProfit:{} - RSI:{}".format(IN_PRICE,SellPriceProfit,last_rsi)
                    writeLog(msgbay)

            else:
                msgbay = "Can't Sell Out Position"
                writeLog(msgbay)
        
        #Buy Proccess
        if last_rsi < RSI_OVERSOLD:
            if in_position:
                #Stop Loss Proccess
                SellPriceLoss = IN_PRICE - (IN_PRICE * STOPLOSS)
                if SellPriceLoss > close: #Check Stop Price
                    order_succeeded = order(SIDE_SELL, QNTY, SYMBOL,IN_PRICE,SellPriceLoss)
                    if order_succeeded:
                        in_position = False
                        msgbay = "Succeeded Sell-StopLoss IN_PRICE:{} - SellPriceLoss:{} - RSI:{}".format(IN_PRICE,SellPriceLoss,last_rsi)
                        writeLog(msgbay)
                    else:
                        msgbay = "Can't Sell-StopLoss API Error IN_PRICE:{} - SellPriceLoss:{} - RSI:{}".format(IN_PRICE,SellPriceLoss,last_rsi)
                        writeLog(msgbay)
                else :
                    msgbay = "Can't Buy In Position IN_PRICE:{} - CURRENT_PRICE:{} - RSI:{}".format(IN_PRICE,close,last_rsi)
                    writeLog(msgbay)
                #End Stop Loss Proccess
            else:
                #Buy Check Low Proccess
                if last_rsi < RSI_LOW:                   
                    msgbay = "Can't Buy Not Low RSI_LOW:{} - CURRENT_PRICE:{} - RSI:{}".format(RSI_LOW,close,last_rsi)
                    writeLog(msgbay)
                    RSI_LOW = last_rsi
                #Buy in low
                else:               
                    # put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, QNTY, SYMBOL,close,close)
                    if order_succeeded:
                        msgbay = "Succeeded Buy IN_PRICE:{} - RSI_LOW:{} - RSI:{}".format(close,RSI_LOW,last_rsi)
                        writeLog(msgbay)
                        in_position = True
                        RSI_LOW = 31
                        IN_PRICE = close
                    else:
                        msgbay = "Can't Buy API Error IN_PRICE:{} - RSI_LOW:{} - RSI:{}".format(close,RSI_LOW,last_rsi)
                        writeLog(msgbay)
                   

        time.sleep(interval_time)#Inerval

if __name__ == "__main__":
    main()