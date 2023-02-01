# TradingView Webhook for Premium Indicator Alert, for comments and tips check debug_webhook_message.py inside BOTs folder
# Copy and paste the following into the TradingView Alert message box:

{
    "Account_Settings": {
        "passphrase": "8j4tr38j8jfsvdap98g",
        "max_account_risk_per_trade": 1
    },
    "Order_Settings": {
        "binance_symbol": "BTCUSDT",
        "leverage": 1,
        "cash_bet_amount": 300,
        "order_type": "limit",
        "max_orderbook_depth": 10,
        "max_orderbook_price_offset": 0.01,
        "min_orderbook_price_offset": 0,
        "limit_forced_offset": -1
    },
    "Trade_Management": {
        "position_boundaries": {
            "take_profit": 0.05,
            "stop_loss": 0.01,
        },
        "trailing_stop_loss": {
            "trailing_stop_loss_percentage": 0.0015,
            "trailing_stop_loss_activation_percentage": 0.0015
        }
    },
    "Signals": {
        "Buy": {{plot("Buy")}},
        "Minimal_Buy": {{plot("Minimal Buy")}},
        "Strong_Buy": {{plot("Strong Buy")}},
        "Minimal_Strong_Buy": {{plot("Minimal Strong Buy")}},
        "Exit_Buy": {{plot("Exit Buy")}},
        "Sell": {{plot("Sell")}},
        "Minimal_Sell": {{plot("Minimal Sell")}},
        "Strong_Sell": {{plot("Strong Sell")}},
        "Minimal_Strong_Sell": {{plot("Minimal Strong Sell")}},
        "Exit_Sell": {{plot("Exit Sell")}}
    }
}

