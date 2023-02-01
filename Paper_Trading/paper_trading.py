import json
import uuid
import pandas as pd
import ccxt
import time
import logging
from threading import Thread
# from vectorbt import TelegramBot
# import constants as keys

# bot = TelegramBot(token=keys.API_KEY)
FORMAT = '%(asctime)s|%(funcName)s|%(levelname)s|%(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(FORMAT)
file_handler = logging.FileHandler('paper_logs.csv')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class PaperTrading:
    '''
    Simulates trades using real exchanges data.
    '''

    def __init__(self, exchange: object = ccxt.binanceusdm(),
                 initial_balance=20000, maker_fee: float = 0.02,
                 taker_fee: float = 0.04, name: str = 'test', leverage: int = 1) -> None:
        self.name = name
        self.initial_balance = initial_balance
        self.exchange = exchange
        self.maker_fee = maker_fee * .01
        self.taker_fee = taker_fee * .01
        # self.chat_id = keys.CHAT_ID
        self.leverage = leverage
        try:
            with open('paper_positions.json') as json_file:
                self._positions = json.load(json_file)
        except Exception:
            self._positions = {}
        try:
            with open('paper_orders.json') as json_file:
                self._orders = json.load(json_file)
        except Exception:
            self._orders = {}
        try:
            with open('paper_balance.json') as json_file:
                self._balance = json.load(json_file)
        except Exception:
            self._create_balance_dict()
        try:
            with open('paper_trades.json') as json_file:
                self._trades = json.load(json_file)
        except Exception:
            self._trades = {}
            self._trades[self.name] = []

        logger.info(f'{self.name}|{None}|{None}|{None}|{None}|{None}|{None}|{None}|module|restarted')
        self.thread = Thread(target=self._run_updater, name='Pending Orders Updater')
        self.thread.start()

    def _create_balance_dict(self):
        '''Create a dictionary with the initial balance'''
        self._balance = {}
        self._balance[self.name] = {
            'wallet_balance': 0,
            'available_balance': self.initial_balance,
            'initial_balance': self.initial_balance,
            'realized_profit': 0,
            'margin_balance': 0,
            'total_fees': 0,
            'total_allocated_margin': 0,
            'total_unrealized_profit': 0
        }
        self._save_balance()

    @property
    def get_maintenance_margin(self):
        '''Get real maintainance margin'''
        mmr = .005  # maintainance margin rate. .5% on Binance for most cases but depends on the notional value
        # https://www.binance.com/en/futures/trading-rules/perpetual/leverage-margin

        maint_margin = self._balance[self.name]['total_allocated_margin'] * self.leverage * mmr  #
        margin_ratio = maint_margin / self._balance[self.name]['margin_balance'] * 100
        return maint_margin, margin_ratio

    def make_deposit(self, amount: float):
        '''Add funds to the initial balance'''
        self._balance[self.name]['initial_balance'] += amount
        self._save_balance()

    @property
    def total_commission(self):
        '''Get total commission from all orders'''
        return sum([order['fees'] for order in self._orders.values()])

    def _check_available_balance(self, margin):
        '''Check if available balance is enough to execute a trade'''
        if self._balance[self.name]['available_balance'] < margin:
            raise Exception('Not enough available balance')

    def _calculate_avg_price(self, symbol, side, amount):
        '''Calculate average price based on the order book and liquidity'''
        book = self.get_order_book(symbol, side)
        filled = []
        new_amount = amount
        self._check_side(side)
        for level in book:
            if level[1] < new_amount:
                filled.append([level[0], level[1]])
                new_amount = new_amount - level[1]
                continue
            else:
                filled.append([level[0], level[1] - new_amount])
                total_contracts = sum([level[1] for level in filled])
                total_cost = sum([level[1] * level[0] for level in filled])
                avg_price = total_cost / total_contracts
                break
        else:
            return 'Size is too big, order not processed'
        return avg_price

    def create_market_order(self, symbol: str, side: str, amount: float):
        '''
        Simulate a market order using real exchange order book data.
        Log the result into a .csv file and include a unique ID into the logger message
        '''
        try:
            avg_price = self._calculate_avg_price(symbol, side, amount)
            id = self.get_unique_id()
            cost = (amount * avg_price)
            fees = self.taker_fee * cost
            timestamp = self.exchange.milliseconds()
            datetime = self.exchange.iso8601(timestamp)
            order = dict(timestamp=timestamp, datetime=datetime, id=id, symbol=symbol, side=side,
                         amount=amount, price=avg_price, type='market', status='filled',
                         fees=fees, cost=cost)
            mark_price = float(self.get_mark_price(symbol)['indexPrice'])
            margin = (amount * mark_price) / self.leverage
            self._check_available_balance(margin)
            self._update_position(order)
            logger.info(
                f'{self.name}|{id}|{symbol}|{side}|{amount}|{avg_price}|{fees}|{cost}|market|filled')  # optimise this log
            if not self.thread.is_alive():
                self.thread = Thread(target=self._run_updater, name='Pending Orders / PnL Updater')
                self.thread.start()
            return order
        except Exception as e:
            logger.warning(self.name, '- paper trade could not be processed:', e)
            # bot.send_message(self.chat_id, f'{self.name} - paper trade could not be processed: {e}')

    def create_limit_order(self, symbol: str, side: str, amount: float, price: float):
        '''Simulate a limit order and place it on record'''
        ticker = self.get_ticker(symbol)
        self._check_side(side)
        placed_on_book = True
        if (side == 'buy') & (price > ticker):
            order = self.create_market_order(symbol, side, amount)
            placed_on_book = False
            print('buy order executed at market price due to price being higher than best ask')
        elif (side == 'sell') & (price < ticker):
            order = self.create_market_order(symbol, side, amount)
            placed_on_book = False
            print('sell order executed at market price due to price being lower than best bid')
        if placed_on_book:
            try:
                self._check_available_balance(amount)
                id = self.get_unique_id()
                cost = (amount * price)
                margin = cost / self.leverage
                fees = 0
                timestamp = self.exchange.milliseconds()
                datetime = self.exchange.iso8601(timestamp)
                order = dict(timestamp=timestamp, datetime=datetime, id=id, symbol=symbol, side=side,
                             amount=amount, price=price, type='limit', status='open',
                             cost=cost, fees=fees
                             )
                self._update_order(order)
                logger.info(f'{self.name}|{id}|{symbol}|{side}|{amount}|{price}|{fees}|{cost}|limit|open')
                if not self.thread.is_alive():
                    self.thread = Thread(target=self._run_updater, name='Pending Orders / PnL Updater')
                    self.thread.start()
                return order
            except Exception as e:
                logger.warning(self.name, '- paper trade could not be processed:', e)
                # bot.send_message(self.chat_id, f'{self.name} - paper trade could not be processed: {e}')

    def _save_positions(self):
        '''Save positions to a .json file'''
        with open("paper_positions.json", "w") as write_file:
            json.dump(self._positions, write_file, indent=4)

    def _save_orders(self):
        '''Save orders to a .json file'''
        with open("paper_orders.json", "w") as write_file:
            json.dump(self._orders, write_file, indent=4)

    def _save_balance(self):
        '''Save balance to a .json file'''
        with open("paper_balance.json", "w") as write_file:
            json.dump(self._balance, write_file, indent=4)

    def _save_trades(self):
        '''Save trades to a .json file'''
        with open("paper_trades.json", "w") as write_file:
            json.dump(self._trades, write_file, indent=4)

    def _update_pnl(self):
        '''Update pnl for all positions using self._calculate_unrealized_pnl'''
        print(f'                                                         ', end='\r')
        print(f'Updating PnL', end='\r')
        for symbol in self._positions[self.name].copy():
            position = self._positions[self.name][symbol]
            amount = position['contracts']
            if amount == 0:
                del self._positions[self.name][symbol]
                self._save_positions()
                continue
            ticker = self.get_ticker(symbol)
            price = position['av_entry_price']
            position['mark_price'] = float(self.get_mark_price(symbol)['indexPrice'])
            position['margin'] = (amount * position['mark_price']) / self.leverage
            pnl = self._calculate_unrealized_pnl(amount, price, ticker)
            position['size'] = amount * ticker
            position['pnl'] = round(pnl, 3)
            # position['perc_pnl'] = round(perc_pnl, 3)
        self._save_positions()

    def _update_unrealized_profit(self):
        '''Update total unrealized_profit in self._balance'''
        unrealized_profit = []
        allocated_margin = []
        for position in self._positions[self.name].values():
            unrealized_profit.append(position['pnl'])
            allocated_margin.append(position['margin'])
        self._balance[self.name]['total_unrealized_profit'] = sum(unrealized_profit)
        self._balance[self.name]['total_allocated_margin'] = sum(allocated_margin)
        self._balance[self.name]['wallet_balance'] = self._balance[self.name]['initial_balance'] + \
                                                     self._balance[self.name]['realized_profit'] - \
                                                     self._balance[self.name]['total_fees']
        self._balance[self.name]['margin_balance'] = self._balance[self.name]['wallet_balance'] + sum(unrealized_profit)
        self._balance[self.name]['available_balance'] = self._balance[self.name]['margin_balance'] - sum(
            allocated_margin)
        self._balance[self.name]['maintainance_margin'] = self.get_maintenance_margin[0]
        self._balance[self.name]['margin_ratio'] = self.get_maintenance_margin[1]
        self._save_balance()

    def _calculate_unrealized_pnl(self, amount, price, ticker):
        '''Calculate unrealized pnl for a position'''
        if amount > 0:
            pnl = (ticker - price) * amount
        elif amount < 0:
            pnl = - (price - ticker) * amount
        # perc_pnl = (pnl / (amount * price)) * 100
        return pnl

    # doesn't fit Binance results when there slippage
    def _calculate_average_entry_price(self, prev_amount, prev_price, amount, price):
        '''
        Calculates the  average entry price using the previous average
        entry price and the amount and price of the new order
        '''
        if prev_amount + amount == 0:
            return 0
        if (prev_amount > 0) & (amount < 0) | (prev_amount < 0) & (amount > 0):
            return (amount * price) / (amount)
        return (prev_amount * prev_price + amount * price) / (prev_amount + amount)

    def _update_position(self, order):
        self._update_order(order)
        '''Update self._positions and self._balance after an order is filled'''
        # create dict if positions are empty
        if self.name not in self._positions:
            self._positions[self.name] = {}
        # create dict if symbol is not in positions
        if order['symbol'] not in self._positions[self.name]:
            self._positions[self.name][order['symbol']] = {'contracts': 0, 'size': 0, 'av_entry_price': 0,
                                                           'mark_price': 0, 'pnl': 0, 'margin': 0}
        prev_amount = self._positions[self.name][order['symbol']]['contracts']
        prev_price = self._positions[self.name][order['symbol']]['av_entry_price']
        # convert amount to negative value if side is 'sell'
        amount = order['amount']
        if order['side'] == 'sell':
            amount = -amount
        # update position amount
        self._positions[self.name][order['symbol']]['contracts'] += amount
        # update fees
        self._balance[self.name]['total_fees'] += order['fees']
        # update average entry price if order is not a reduce order
        is_reduce = (prev_amount > 0 and amount < 0) or (prev_amount < 0 and amount > 0)
        if not is_reduce:
            self._positions[self.name][order['symbol']]['av_entry_price'] = self._calculate_average_entry_price(
                prev_amount, prev_price, amount, order['price'])
        elif is_reduce:
            profit = self._calculate_unrealized_pnl(amount, prev_price, order['price'])
            self._balance[self.name]['realized_profit'] += profit
        trade = dict(timestamp=order['timestamp'], datetime=order['datetime'], id=order['id'], symbol=order['symbol'],
                     side=order['side'],
                     amount=order['amount'], price=order['price'], type=order['type'], cost=order['cost'],
                     fees=order['fees'], profit=profit if is_reduce else 0
                     )
        self._trades[self.name].append(trade)
        self._save_positions()
        self._save_balance()
        self._save_trades()

    def _update_order(self, order):
        '''Update self._orders with symbol, side, amount and price'''
        symbol = order['symbol']
        if self.name not in self._orders:
            self._orders[self.name] = {}
        if symbol not in self._orders[self.name]:
            self._orders[self.name][symbol] = []
        self._orders[self.name][symbol].append(order)
        self._save_orders()

    @property
    def read_log(self):
        """Read log file as pandas DataFrame"""
        df = pd.read_csv('paper_logs.csv', sep='|', header=None)
        df.columns = ['timestamp', 'function', 'level', 'strat_name', 'id', 'symbol', 'side', 'amount', 'avg_price',
                      'fees', 'cost', 'type', 'status']
        return df

    def get_unique_id(self):
        return str(uuid.uuid4().fields[-1])

    def get_ticker(self, symbol):
        '''Get the last ticker price'''
        return self.exchange.fetch_ticker(symbol)['last']

    def get_mark_price(self, symbol):
        '''Get Mark Price from Binance Futures'''
        symbol = symbol.replace('/', '')
        binance = ccxt.binanceusdm()
        mark_price = binance.fapiPublicGetPremiumIndex({
            'symbol': symbol
        })
        return mark_price

    def get_order_book(self, symbol, side):
        '''Fetch order book data from real exchange'''
        book = self.exchange.fetch_order_book(symbol)
        if side == 'buy':
            asks = book['asks']
            return asks
        elif side == 'sell':
            bids = book['bids']
            return bids

    @property
    def has_open_orders(self):
        '''Return True if there are any open orders'''
        try:
            for symbol in self._orders[self.name]:
                for order in self._orders[self.name][symbol]:
                    if order['status'] == 'open':
                        return True
        except KeyError:
            return False

    @property
    def has_open_positions(self):
        '''Return True if there are any open positions'''
        try:
            if self._positions[self.name]:
                return True
        except KeyError:
            return False

    def _update_open_orders(self):
        '''Update open limit orders using real exchange data'''
        for symbol in self._orders[self.name]:
            try:
                if self._orders[self.name][symbol]:
                    ticker = self.get_ticker(symbol)
                    print(f'                                                         ', end='\r')
                    print(f'Updating open orders for {symbol} at {ticker}', end='\r')
                    for order in self._orders[self.name][symbol]:
                        if order['status'] == 'open':
                            id = order['id']
                            side = order['side']
                            amount = order['amount']
                            price = order['price']
                            cost = (amount * price)
                            margin = cost / self.leverage
                            order['timestamp'] = self.exchange.milliseconds()
                            order['datetime'] = self.exchange.iso8601(order['timestamp'])
                            self._check_available_balance(margin)
                            order['fees'] = self.maker_fee * cost
                            fees = order['fees']
                            if side == 'buy':
                                if ticker <= price:
                                    order['status'] = 'filled'
                                    self._update_position(order)
                                    logger.info(
                                        f'{self.name}|{id}|{symbol}|{side}|{amount}|{price}|{fees}|{cost}|limit|filled')
                                    print(
                                        f'Order filled: {self.name}|{id}|{symbol}|{side}|{amount}|{price}|{fees}|{cost}|limit|filled')
                                    self._save_orders()
                            elif side == 'sell':
                                if ticker >= price:
                                    order['status'] = 'filled'
                                    self._update_position(order)
                                    logger.info(
                                        f'{self.name}|{id}|{symbol}|{side}|{amount}|{price}|{fees}|{cost}|limit|filled')
                                    print(
                                        f'Order filled: {self.name}|{id}|{symbol}|{side}|{amount}|{price}|{fees}|{cost}|limit|filled')
                                    self._save_orders()
            except Exception as e:
                logger.warning(self.name, '- paper trade could not be processed:', e)
                # bot.send_message(self.chat_id, f'{self.name} - paper trade could not be processed: {e}')
                self.cancel_order(id)
                continue

    def _run_updater(self):
        '''Run pnl and open orders updater'''
        while (self.has_open_orders or self.has_open_positions):
            if self.has_open_positions:
                self._update_pnl()
                self._update_unrealized_profit()
            if self.has_open_orders:
                self._update_open_orders()
            time.sleep(1)

    def _check_side(self, side):
        '''Validate side'''
        if side != None and side not in ['buy', 'sell']:
            raise ValueError(f'side must be either "buy" or "sell"')

    def cancel_order(self, id: int):
        '''Cancel order corresponding to id'''
        for symbol in self._orders[self.name]:
            for i in self._orders[self.name][symbol]:
                if i['id'] == id:
                    self._orders[self.name][symbol].remove(i)
                    self._save_orders()
                    return True

    def cancel_orders(self, id: list):
        '''Cancel orders corresponding to ids'''
        for symbol in self._orders[self.name]:
            for i in self._orders[self.name][symbol]:
                if i['id'] in id:
                    self._orders[self.name][symbol].remove(i)
                    self._save_orders()
                    return True

    def cancel_all_orders(self, symbol=None):
        '''Cancel all open orders if symbol not specified.
        Cancel all open orders for specified symbol
        '''
        if symbol == None:
            self._orders[self.name] = {}
            self._save_orders()
            return True
        else:
            self._orders[self.name][symbol] = []
            self._save_orders()
            return True

    def edit_order(self, id, symbol: str = None, side: str = None,
                   amount: float = None, price: float = None,
                   type: str = None):
        '''Edit values of order corresponding to id'''
        self._check_side(side)
        for symbol in self._orders[self.name]:
            for i in self._orders[self.name][symbol]:
                if i['id'] == id:
                    if symbol != None:
                        i['symbol'] = symbol
                    if side != None:
                        i['side'] = side
                    if amount != None:
                        i['amount'] = amount
                    if price != None:
                        i['price'] = price
                    if type != None:
                        i['type'] = type
                    self._save_orders()
                    return True

binance_api_key = "316ee06e009b0ec07b92d15328bed7f0a92c7e1ddb2ce8a755273a6d4f91c802"
binance_api_secret = "e56b5fbc30dee0b4eb951933b39bc6eb4864a7ae2b60768a6697960b3ff5e838"

exchange = getattr(ccxt, "binance")({
                'apiKey': binance_api_key,
                'secret': binance_api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': "future"
                },
            })
exchange.set_sandbox_mode(True)

ex = PaperTrading(exchange=exchange)
# ex.create_market_order('BTC/USDT', 'buy', 0.5)
# ex.create_limit_order('LTC/USDT', 'buy', 2, 50)
# # # # print(ex._positions.values())
# # # print(ex.total_unrealized_profit)