import numpy as np
import datetime
from binance.client import Client
from binance.spot import Spot
from dotenv import load_dotenv
import os

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

# Fonction pour calculer les Bandes de Bollinger
def calcul_bollinger(prix_cloture, periode=20, k=2):
    """
    Calcule les Bandes de Bollinger.

    :param prix_cloture: Liste des prix de clôture.
    :param periode: Période de la moyenne mobile simple (par défaut 20).
    :param k: Facteur multiplicatif pour l'écart-type (par défaut 2).
    :return: Liste des bandes supérieures, des moyennes mobiles et des bandes inférieures
    """
    bandes_superieures = []
    bandes_inferieures = []
    moyennes_mobiles = []

    # Vérifier que nous avons suffisamment de données pour calculer la SMA et l'écart-type
    if len(prix_cloture) < periode:
        raise ValueError("Pas assez de données pour la période donnée")

    # Calcul des Bandes de Bollinger pour chaque période
    for i in range(periode, len(prix_cloture) + 1):
        # Prendre la sous-liste des derniers prix de clôture sur la période
        prix_sublist = prix_cloture[i - periode:i]

        # Calcul de la SMA (moyenne mobile simple)
        sma = np.mean(prix_sublist)

        # Calcul de l'écart-type
        ecart_type = np.std(prix_sublist)

        # Calcul des bandes supérieure et inférieure
        bande_superieure = sma + (k * ecart_type)
        bande_inferieure = sma - (k * ecart_type)

        bandes_superieures.append(bande_superieure)
        bandes_inferieures.append(bande_inferieure)
        moyennes_mobiles.append(sma)

    return bandes_superieures, moyennes_mobiles, bandes_inferieures

# Modifier la fonction write_data pour inclure les Bandes de Bollinger
def write_data(values, tz):
    # Extraction des prix de clôture
    prix_cloture = [float(value[4]) for value in values]

    # Calcul des Bandes de Bollinger
    bandes_superieures, moyennes_mobiles, bandes_inferieures = calcul_bollinger(prix_cloture)

    # Ouverture des fichiers pour écrire les données
    with open("data_crypto.txt", "w") as f, open("bearish_engulfing_bar.txt", "w") as f2, open("doji_candlestick.txt", "w") as f3, open("bollinger.txt", "w") as f4:
        f.write("OpenTime,Open,High,Low,Close,Volume,CloseTime,QuoteAssetVolume,Trades,TakerBuyBase,TakerBuyQuote\n")
        f4.write("OpenTime,Upper Bollinger Band,Middle Bollinger Band,Lower Bollinger Band\n")  # Titre du fichier Bollinger
        i = 0
        for value in values:
            # Extraction du temps de Kline
            kline_time = datetime.datetime.fromtimestamp(value[0] / 1000.0, tz) + datetime.timedelta(hours=1)
            f.write(f"{kline_time},")
            f.write(f"{value[1]},{value[2]},{value[3]},{value[4]},{value[5]},{value[6]},{value[7]},{value[8]},{value[9]},{value[10]}\n")
            
            # Tester pour Doji Candlestick
            test_doji_candlestick = is_doji_candlestick(value)
            if test_doji_candlestick == DOJI_CANDLESTICK:
                f3.write(f"{kline_time}\n")
            
            # Tester pour Bearish Engulfing Bar
            if i < len(values) - 1:
                test_bearish_engulfing_bar = is_bearish_engulfing_bar(value, values[i + 1])
                if test_bearish_engulfing_bar == BEARISH_ENGULFING_BAR:
                    f2.write(f"{kline_time}\n")

            # Écrire les Bandes de Bollinger dans le fichier
            if i >= 19:  # On commence à partir du 20ème élément pour avoir assez de données pour la période 20
                f4.write(f"{kline_time},{bandes_superieures[i-19]},{moyennes_mobiles[i-19]},{bandes_inferieures[i-19]}\n")

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
