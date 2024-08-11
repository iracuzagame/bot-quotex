import time
from quotexapi.stable_api import Quotex
import talib

email = "tu_correo@ejemplo.com"
password = "tu_contraseña"
client = Quotex(email=email, password=password, ...)

def buy(asset):
    client.buy(asset, 1)

def calcular_indicadores(candles):
    # Convertir los datos de las velas a formato NumPy (necesario para talib)
    close_prices = np.array([candle['close'] for candle in candles])

    # Calcular los indicadores
    macd, macdsignal, macdhist = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    alligator_teeth, alligator_jaws, alligator_lips = talib.ALMA(close_prices, timeperiod=8, offset=0.85, sigma=6)
    rsi = talib.RSI(close_prices, timeperiod=4)

    return macd, macdsignal, macdhist, alligator_teeth, alligator_jaws, alligator_lips, rsi

# Función para tomar decisiones de trading
def tomar_decision(macd, macdsignal, macdhist, rsi, alligator_teeth, alligator_jaws, alligator_lips):
    if (macd[-1] > macdsignal[-1] and macdhist[-1] > 0 and
        rsi[-1] > 70 and alligator_jaws[-1] < alligator_teeth[-1] and
        alligator_jaws[-1] < alligator_lips[-1]):
        return "buy"
    elif (macd[-1] < macdsignal[-1] and macdhist[-1] < 0 and
          rsi[-1] < 30 and alligator_jaws[-1] > alligator_teeth[-1] and
          alligator_jaws[-1] > alligator_lips[-1]):
        return "sell"
    else:
        return "hold"

while True:

    # Tomar decisión y ejecutar orden
    decision = tomar_decision(macd, macdsignal, macdhist, rsi, alligator_teeth, alligator_jaws, alligator_lips)
    if decision == "buy":
        client.buy("EURUSD", 1)
    elif decision == "sell":
        client.sell("EURUSD", 1)

    time.sleep(60)
