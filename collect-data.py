from binance.client import Client
from binance.spot import Spot
from dotenv import load_dotenv
import os
import datetime

# Constants for candlestick and pattern types
KO = 0
BULLISH = 0
BEARISH = 1
BEARISH_ENGULFING_BAR = 1
DOJI_CANDLESTICK = 1

# Load environment variables from a .env file
load_dotenv()

# Function to determine if a candlestick is bullish or bearish
def is_bullish_bearish(tab):
    if tab[1] < tab[4]:  # Open price less than close price -> bullish
        return BULLISH
    else:
        return BEARISH

# Function to check for a Bearish Engulfing Bar pattern
def is_bearish_engulfing_bar(tab1, tab2):
    # A Bearish Engulfing Bar occurs when the first candlestick is bullish and the second is bearish
    if is_bullish_bearish(tab1) == BULLISH and is_bullish_bearish(tab2) == BEARISH:
        # The second candlestick's range should be larger than the first one
        if abs(float(tab1[4]) - float(tab1[1])) < abs(float(tab2[4]) - float(tab2[1])):
            return BEARISH_ENGULFING_BAR
    return KO

# Function to check if a candlestick is a Doji
def is_doji_candlestick(tab1):
    # A Doji candlestick has open and close prices equal or very close to each other
    if abs(float(tab1[1])) == abs(float(tab1[4])):
        if abs(float(tab1[1])) != abs(float(tab1[2])) and abs(float(tab1[1])) != abs(float(tab1[3])):
            return DOJI_CANDLESTICK
    return KO

# Function to initialize the Binance client and fetch historical data
def fetch_data():
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    client2 = Client(api_key, api_secret)  # For historical data
    client = Spot()  # For real-time data

    # Get server timestamp from Binance
    actual_timestamp = client.time()['serverTime']
    tz = datetime.timezone.utc

    # Convert timestamp to human-readable date and time
    datetime_now = datetime.datetime.fromtimestamp(actual_timestamp / 1000.0, tz)
    print(f"Current Time: {datetime_now}")

    # Fetch 30-minute klines (candlesticks) for December 2017
    values = client2.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")
    
    return values, tz

# Function to write data to files
def write_data(values, tz):
    # Open output files for writing
    with open("data_crypto.txt", "w") as f, open("bearish_engulfing_bar.txt", "w") as f2, open("doji_candlestick.txt", "w") as f3:
        f.write("OpenTime,Open,High,Low,Close,Volume,CloseTime,QuoteAssetVolume,Trades,TakerBuyBase,TakerBuyQuote\n")
        i = 0
        for value in values:
            # Write Kline data to the file
            kline_time = datetime.datetime.fromtimestamp(value[0] / 1000.0, tz) + datetime.timedelta(hours=1)
            f.write(f"{kline_time},")
            f.write(f"{value[1]},{value[2]},{value[3]},{value[4]},{value[5]},{value[6]},{value[7]},{value[8]},{value[9]},{value[10]}\n")
            
            # Test for Doji Candlestick pattern
            test_doji_candlestick = is_doji_candlestick(value)
            if test_doji_candlestick == DOJI_CANDLESTICK:
                f3.write(f"{kline_time}\n")
            
            # Test for Bearish Engulfing Bar pattern
            if i < len(values) - 1:
                test_bearish_engulfing_bar = is_bearish_engulfing_bar(value, values[i + 1])
                if test_bearish_engulfing_bar == BEARISH_ENGULFING_BAR:
                    f2.write(f"{kline_time}\n")
            i += 1

# Main function to orchestrate the logic
def main():
    # Fetch data from Binance
    values, tz = fetch_data()

    # Process and write data to files
    write_data(values, tz)

# Entry point of the program
if __name__ == "__main__":
    main()
