import pandas as pd

import streamlit as st

def render_configuration_table(configuration_database_name):
    # get the list of configurations
    from dashboard_depracated.webhook_configuration.configuration_database_handler import AssetConfigurationDatabaseHandler
    asset_configurations_db_manager = AssetConfigurationDatabaseHandler(
        configuration_group_name=configuration_database_name,
        redis_host='localhost', redis_port=6379, redis_db=0, decode_responses=True
    )
    configurations = asset_configurations_db_manager.get_all_configurations()
    if len(configurations) == 0:
        st.warning("No configurations found")
    else:
        # {
        # "dfgd":"{"Account_Settings": {"passphrase": "oMuGI01ejxCKJdfvSew4", "max_account_risk_per_trade": 1.0}, "Order_Settings": {"binance_symbol": "BTCUSDT", "leverage": 1, "cash_bet_amount": 300, "order_type": "limit"}, "Trade_Management": {"position_boundaries": {"take_profit": 0.05, "stop_loss": 0.01}, "trailing_stop_loss": {"trailing_stop_loss_percentage": 0.0015, "trailing_stop_loss_activation_percentage": 0.0015}}, "Signals": {"Buy": "Buy", "Minimal_Buy": "Minimal Buy", "Strong_Buy": "Strong Buy", "Minimal_Strong_Buy": "Minimal Strong Buy", "Exit_Buy": "Exit Buy", "Sell": "Sell", "Minimal_Sell": "Minimal Sell", "Strong_Sell": "Strong Sell", "Minimal_Strong_Sell": "Minimal Strong Sell", "Exit_Sell": "Exit Sell"}}"
        # "sadad":"{"Account_Settings": {"passphrase": "vyLd9u2q38MO29B9VHY6", "max_account_risk_per_trade": 1.0}, "Order_Settings": {"binance_symbol": "BTCUSDT", "leverage": 1, "cash_bet_amount": 300, "order_type": "limit"}, "Trade_Management": {"position_boundaries": {"take_profit": 0.05, "stop_loss": 0.01}, "trailing_stop_loss": {"trailing_stop_loss_percentage": 0.0015, "trailing_stop_loss_activation_percentage": 0.0015}}, "Signals": {"Buy": "Buy", "Minimal_Buy": "Minimal Buy", "Strong_Buy": "Strong Buy", "Minimal_Strong_Buy": "Minimal Strong Buy", "Exit_Buy": "Exit Buy", "Sell": "Sell", "Minimal_Sell": "Minimal Sell", "Strong_Sell": "Strong Sell", "Minimal_Strong_Sell": "Minimal Strong Sell", "Exit_Sell": "Exit Sell"}}"
        # }
        configurations = pd.DataFrame(configurations, index=[0]).T
        configurations.columns = ["Configuration"]
        configurations.index.name = "Configuration Name"
        st.dataframe(configurations)

        # select the configuration


        # delete the configuration
        pick_asset_col, delete_asset_col = st.columns(2)
        with pick_asset_col:
            configuration_name = st.selectbox("Select Configuration", configurations.index)
        with delete_asset_col:
            if st.button("Delete Configuration"):
                asset_configurations_db_manager.delete_configuration(configuration_name)
                st.success("Configuration deleted")
                st._rerun()

