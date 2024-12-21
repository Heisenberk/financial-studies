from binance.client import Client
from binance.spot import Spot
from dotenv import load_dotenv
import os

import datetime
import matplotlib.pyplot as plt

KO = 0
BULLISH = 0
BEARISH = 1
BEARISH_ENGULFING_BAR = 1
DOJI_CANDLESTICK = 1

load_dotenv()

# Returns if a candlestick (tab) is bullish or bearish
def is_bullish_bearish (tab):
	if tab[1] < tab[4]: 
		return BULLISH
	else: 
		return BEARISH

# Returns if a candlestick (tab) and the next one (tab2) match a bearish engulfing bar
def is_bearish_engulfing_bar (tab1, tab2): 
	if is_bullish_bearish(tab1) == BULLISH and is_bullish_bearish(tab2) == BEARISH: 
		if abs(float(tab1[4])-float(tab1[1])) < abs(float(tab2[4])-float(tab2[1])) : 
			return BEARISH_ENGULFING_BAR
	return KO
	
def is_doji_candlestick (tab1):
	if abs(float(tab1[1])) == abs(float(tab1[4])):
		return DOJI_CANDLESTICK
	return KO

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
client2 = Client(api_key, api_secret)
client = Spot()

# Get server timestamp
actual_timestamp = client.time()['serverTime']

crypto = "BTCUSDT"

tz = datetime.timezone.utc
datetime_now = datetime.datetime.fromtimestamp(actual_timestamp / 1000.0, tz)
print(datetime_now)

"""
# Get last 10 klines of BTCUSDT at 1h interval
#values = client.klines("BTCUSDT", "1h", limit=10)

# Get klines of BTCUSDT at 1m interval
#values = client.klines(crypto, "1m")
##values = client.klines(crypto, "1d")

# fetch 1 minute klines for the last day up until now
#values = client2.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

# fetch 30 minute klines for the last month of 2017
"""
values = client2.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")

f = open("data_crypto.txt", "w")
f.write("OpenTime,Open,High,Low,Close,Volume,CloseTime,QuoteAssetVolume,Trades,TakerBuyBase,TakerBuyQuote\n")
f2 = open("bearish_engulfing_bar.txt", "w")
f3 = open("doji_candlestick.txt", "w")

i=0
for value in values : 
	print("Kline open time : " + str(datetime.datetime.fromtimestamp(value[0] / 1000.0, tz)+ datetime.timedelta(hours=1)))
	f.write(str(datetime.datetime.fromtimestamp(value[0] / 1000.0, tz)+ datetime.timedelta(hours=1))+",")
	#f.write(str(datetime.datetime.fromtimestamp(value[0] / 1000.0, tz))+",")
	print("Open price : " + value[1] + "$")
	f.write(value[1]+",")
	print("High price : " + value[2] + "$")
	f.write(value[2]+",")
	print("Low price : " + value[3] + "$")
	f.write(value[3]+",")
	print("Close price : " + value[4] + "$")
	f.write(value[4]+",")
	print("Volume : " + value[5])
	f.write(value[5]+",")
	print("Kline close time : " + str(datetime.datetime.fromtimestamp(value[6] / 1000.0, tz)+ datetime.timedelta(hours=1)))
	f.write(str(datetime.datetime.fromtimestamp(value[6] / 1000.0, tz)+ datetime.timedelta(hours=1))+",")
	print("Quote asset volume : " + value[7])
	f.write(value[7]+",")
	print("Number of trades : " + str(value[8]))
	f.write(str(value[8])+",")
	print("Taker buy base asset volume : " + value[9])
	f.write(value[9]+",")
	print("Taker buy quote asset volume : " + value[10])
	f.write(value[10])
	print("BULLISH(0) /BEARISH(1) : "+str(is_bullish_bearish(value)))
	
	# Test DOJI CANDLESTICK
	test_doji_candlestick = is_doji_candlestick(value)
	if test_doji_candlestick == DOJI_CANDLESTICK : 
		f3.write(str(datetime.datetime.fromtimestamp(value[0] / 1000.0, tz)+ datetime.timedelta(hours=1)))
		f3.write("\n")
	print("DOJI CANDLESTICK (1) / NOT (0) : "+str(test_doji_candlestick))
	
	# Test BEARISH ENGULFING BAR
	if i < (len(values)-1): 
		test_bearish_engulfing_bar = is_bearish_engulfing_bar(value, values[i+1])
		print("IS_BEARISH_ENGULFING_BAR ? "+str(test_bearish_engulfing_bar))
		if test_bearish_engulfing_bar == BEARISH_ENGULFING_BAR : 
			f2.write(str(datetime.datetime.fromtimestamp(value[0] / 1000.0, tz)+ datetime.timedelta(hours=1)))
			f2.write("\n")
	print("\n")
	f.write("\n")
	i=i+1


f.close()
f2.close()
f3.close()
