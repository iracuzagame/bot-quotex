import asyncio
from quotexpy import Quotex
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing importList, Dict, Union# Configura tus credenciales


username = ""
password = ""

classTradingBot:
    def__init__(self, username: str, password: str):
        self.client = Quotex(username, password)
    
    asyncdefconnect(self) -> bool:
        try:
            await self.client.connect()
            print("Conexión exitosa")
            returnTrueexcept Exception as e:
            print(f"Error en la conexión: {e}")
            returnFalseasyncdefget_market_data(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        try:
            candles = await self.client.get_candles(symbol, timeframe, limit=limit)
            df = pd.DataFrame(candles)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            return df
        except Exception as e:
            print(f"Error al obtener datos de mercado: {e}")
            return pd.DataFrame()

    defcalculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        # MACD
        df['MACD'], df['MACD_signal'], df['MACD_hist'] = self.calculate_macd(df['close'])
        
        # RSI
        df['RSI'] = self.calculate_rsi(df['close'], period=4)
        
        # Alligator
        df['jaws'] = df['close'].rolling(window=8).mean().shift(3)
        df['teeth'] = df['close'].rolling(window=2).mean().shift(2)
        df['lips'] = df['close'].rolling(window=2).mean().shift(1)
        
        return df

    defcalculate_macd(self, prices: pd.Series, fast_period=12, slow_period=26, signal_period=9) -> pd.DataFrame:
        fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
        slow_ema = prices.ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        macd_signal = macd.ewm(span=signal_period, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist

    defcalculate_rsi(self, prices: pd.Series, period=4) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    deftrading_strategy(self, df: pd.DataFrame) -> List[Dict[str, Union[str, float, pd.Timestamp]]]:
        signals = []
        for i inrange(1, len(df)):
            # Estrategia de compraif (
                df['MACD'][i] > df['MACD_signal'][i] and df['MACD'][i - 1] <= df['MACD_signal'][i - 1] and# Cruce de MACD hacia arriba
                df['RSI'][i] > 70and df['RSI'][i - 1] <= 70and# RSI cruza sobre el nivel de sobrecompra
                df['jaws'][i] < df['lips'][i] and df['jaws'][i] < df['teeth'][i] and# Mandíbula debajo de labios y dientes
                df['lips'][i] > df['teeth'][i]  # Labios por encima de los dientes
            ):
                signals.append({"action": "buy", "time": df['timestamp'][i], "price": df['close'][i]})
            
            # Estrategia de ventaelif (
                df['MACD'][i] < df['MACD_signal'][i] and df['MACD'][i - 1] >= df['MACD_signal'][i - 1] and# Cruce de MACD hacia abajo
                df['MACD_hist'][i] < 0and# Histograma MACD debajo de 0
                df['RSI'][i] < 30and df['RSI'][i - 1] >= 30and# RSI cruza debajo del nivel de sobreventa
                df['jaws'][i] > df['lips'][i] and df['jaws'][i] > df['teeth'][i] and# Mandíbula por encima de labios y dientes
                df['lips'][i] < df['teeth'][i]  # Labios debajo de dientes
            ):
                signals.append({"action": "sell", "time": df['timestamp'][i], "price": df['close'][i]})
                
        return signals

    asyncdefplace_order(self, action: str, amount: float, symbol: str, duration: int = 2):
        try:
            if action == "buy":
                await self.client.buy(symbol, amount, duration=duration)
            elif action == "sell":
                await self.client.sell(symbol, amount, duration=duration)
            print(f"{action.capitalize()} orden ejecutada para {symbol} con cantidad {amount} y duración {duration} minutos")
        except Exception as e:
            print(f"Error al ejecutar la orden: {e}")

    defplot_candlestick(self, df: pd.DataFrame, symbol: str):
        # Generar el gráfico de velas
        fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                                            open=df['open'],
                                            high=df['high'],
                                            low=df['low'],
                                            close=df['close'])])

        fig.update_layout(
            title=f'Gráfico de velas para {symbol} (1m)',
            xaxis_title='Fecha/Hora',
            yaxis_title='Precio',
            xaxis_rangeslider_visible=False
        )

        fig.show()

asyncdefmain():
    bot = TradingBot(username, password)

    # Conexión al clienteifnotawait bot.connect():
        return# Obtener datos de mercado
    symbol = "EURUSD"
    timeframe = "1m"
    market_data = await bot.get_market_data(symbol, timeframe)

    if market_data.empty:
        print("No se recibieron datos de mercado.")
        return# Calcular indicadores
    market_data = bot.calculate_indicators(market_data)
    print(market_data.tail())

    # Mostrar gráfico de velas
    bot.plot_candlestick(market_data, symbol)

    # Estrategia de trading
    signals = bot.trading_strategy(market_data)
    for signal in signals:
        print(f"{signal['action'].capitalize()} en {signal['time']} al precio {signal['price']}")

    # Ejecutar órdenesfor signal in signals:
        await bot.place_order(signal["action"], 10, symbol, duration=2)
        await asyncio.sleep(0.5)  # Evitar bloqueos al realizar múltiples órdenesif __name__ == '__main__':
    asyncio.run(main())
