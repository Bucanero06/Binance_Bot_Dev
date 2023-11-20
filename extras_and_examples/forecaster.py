# forcast price based on current volatility and vwap
import numpy as np
import pandas as pd


def get_forecast_price(BOT, symbol, forecast_time):
    """
    This function will return the forecasted price for the symbol based on the forecast_time.
    :param BOT:
    :param symbol:
    :param forecast_time:
    :return:
    """
    # Get current price
    current_price = BOT.exchange_client.fetch_ticker(symbol)["last"]
    # Get current volatility
    current_volatility = get_current_volatility(BOT, symbol)
    # Get current vwap
    current_vwap = get_current_vwap(BOT, symbol)
    # Get forecasted price
    forecasted_price = current_vwap + (current_volatility * forecast_time)
    # Return forecasted price
    return


def get_bet_size_from_vwap(klines=None, interval_number=5, roll=True):
    """Calculate VWAP from klines data"""

    # VWAP = ∑ (Typical Price * Volume ) / ∑ Volume
    for j in range(1, len(klines) - 1 if roll else 2):
        # for i in range(len(klines) - interval_number, len(klines)):
        # shift the interval by 1 candle
        temp_typical_price_times_volume = 0.0
        temp_volume = 0.0
        for i in range(len(klines) - interval_number - j, len(klines) - j):
            high_price = float(klines[i][2])
            low_price = float(klines[i][3])
            close_price = float(klines[i][4])


            # Typical price
            typical_price = np.mean([high_price, low_price, close_price])
            volume = float(klines[i][5])
            temp_typical_price_times_volume += close_price * volume
            temp_volume += volume

        # VWAP = ∑ (Typical Price * Volume ) / ∑ Volume
        vmap = temp_typical_price_times_volume / temp_volume
        from BOTs.Bet_Sizing.ch10_snippets import bet_size, get_w
        b_size = bet_size(
            # get_w(price_div=high_price - low_price, m_bet_size=0.95, func='sigmoid'),
            get_w(price_div=8, m_bet_size=0.95, func='sigmoid'),
            price_div=vmap - typical_price,
            func='sigmoid')
        # print(f'close_price \t typical_price \t temp_vwap \t b_size')
        # print(f'{close_price} \t {typical_price} \t {temp_vwap} \t {b_size}\n')

        next_close_price = float(klines[i +1][4])
        div_between_close_and_next_close = next_close_price - close_price

        if j == 1:
            array_df = [{'close': close_price,
                         # 'nxt_close': next_close_price,
                         # 'avg': typical_price,
                         'vmap': vmap,
                         'b_size': b_size,
                         'realized_profit': b_size * div_between_close_and_next_close,
                         'expected_profit': np.sign(b_size) * div_between_close_and_next_close,
                         'target_profDit': abs(div_between_close_and_next_close)
                         }]
        else:
            array_df.append({'close': close_price,
                             # 'nxt_close': next_close_price,
                             # 'avg': typical_price,
                             'vmap': vmap,
                             'b_size': b_size,
                             'realized_profit': b_size * div_between_close_and_next_close,
                             'expected_profit': np.sign(b_size) * div_between_close_and_next_close,
                             'target_profDit': abs(div_between_close_and_next_close)

                             })

    # print all the columns without truncating and wrapping
    pd.set_option('display.max_columns', None)

    df = pd.DataFrame(array_df)
    df['cum_realized_profit'] = df['realized_profit'].cumsum()
    df['cum_expected_profit'] = df['expected_profit'].cumsum()
    df['cum_target_profDit'] = df['target_profDit'].cumsum()
    # df['mean'] = df['target_profDit'].mean()
    print(f"{df}\n")

    return df


def test_the_forecast():
    from unicorn_binance_rest_api import BinanceRestApiManager

    # binance_api_key = BOT.exchange_client.apiKey
    # binance_api_secret = BOT.exchange_client.secret
    exchange_name = "binance.com-futures-testnet"
    ubra = BinanceRestApiManager(exchange=exchange_name)
    klines = ubra.get_historical_klines("BTCUSDT", ubra.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    # klines = ubra.get_historical_klines("BTCUSDT", ubra.KLINE_INTERVAL_1MINUTE, "30 minutes ago UTC")

    current_vwap = get_bet_size_from_vwap(klines=klines, interval_number=len(klines))
    exit()
    # current_vwap = get_vwap(klines=klines, interval_number=5)

    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                       'quote_asset_volume', 'number_of_trades',
                                       'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                       'ignore'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df['quote_asset_volume'] = df['quote_asset_volume'].astype(float)
    df['number_of_trades'] = df['number_of_trades'].astype(float)
    df['taker_buy_base_asset_volume'] = df['taker_buy_base_asset_volume'].astype(float)
    df['taker_buy_quote_asset_volume'] = df['taker_buy_quote_asset_volume'].astype(float)

    # # Get the typical price
    # typical_price = df['close'].mean()
    # print(typical_price)
    # # VWAP = ∑ (Typical Price * Volume ) / ∑ Volume
    # vwap = np.sum(typical_price * df['volume']) / np.sum(df['volume'])
    # print(vwap)
    # Get the last price of df (close)
    last_price = df['close'].iloc[-1]
    fake_market_price = df['close'].mean()
    print(f'{last_price=}')
    print(f'{fake_market_price=}')
    print(f'{current_vwap=}')
    from BOTs.Bet_Sizing.bet_sizing import bet_size_dynamic

    # :param cal_divergence: (float) The divergence to use in calibration.
    # :param cal_bet_size: (float) The bet size to use in calibration.

    # derive the calibration for divergence and bet size
    # response = bet_size_dynamic(
    #     current_pos=0,
    #     max_pos=1000,
    #     market_price=last_price,
    #     forecast_price=current_vwap, cal_divergence=3, cal_bet_size=0.95,
    #     func='sigmoid'
    # )
    # print(response)
    # exit()
    # from BOTs.Bet_Sizing.bet_sizing import bet_size_dynamic
    # try:
    #     response = bet_size_dynamic(
    #         current_pos=0,
    #         max_pos=100,
    #         market_price=fake_market_price,
    #         forecast_price=current_vwap, cal_divergence=3, cal_bet_size=0.95,
    #         func='sigmoid'
    #     )
    #     print(response)
    # except Exception as e:
    #     print(e)


test_the_forecast()
