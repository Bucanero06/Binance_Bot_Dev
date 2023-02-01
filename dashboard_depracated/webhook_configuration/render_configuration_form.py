import json
import pandas as pd
import streamlit as st
from streamlit.components.v1 import components

from dashboard_depracated.webhook_configuration.configuration_utils import get_random_string


def add_limit_order_options(parent_object, parent_object_dict):
    parent_object_dict["max_orderbook_depth"] = parent_object.slider("Max Orderbook Depth", 1, 100, 10)
    parent_object_dict["max_orderbook_price_offset"] = parent_object.slider("Max Orderbook Price Offset", 0.0, 1.0,
                                                                            0.01, 0.01)
    parent_object_dict["min_orderbook_price_offset"] = parent_object.slider("Min Orderbook Price Offset", 0.0, 1.0, 0.0,
                                                                            0.01)
    # from dashboard_depracated.webhook_configuration.configuration_getters import get_limit_forced_offset
    # form_dict["limit_forced_offset"] = get_limit_forced_offset(parent_object=form)

    on_off_switch_col, limit_forced_offset_col = parent_object.columns(2)
    on_off_switch = on_off_switch_col.checkbox("Limit Forced Offset")

    limit_forced_offset = limit_forced_offset_col.slider("Limit Forced Offset", min_value=0., max_value=1.0,
                                                         value=0., step=0.01)
    if on_off_switch:
        parent_object_dict["limit_forced_offset"] = limit_forced_offset
    else:
        parent_object_dict["limit_forced_offset"] = -1

    return parent_object_dict


def render_binance_bot_configuration_form(configuration_database_name):
    st.title("Configuration of incoming webhooks from tradingview")

    # define the form type
    configuration_name = st.text_input("Configuration Name")
    order_type = st.selectbox("Order Type", ["limit", "market"])

    # define the fields
    form = st.form(key="binance_bot_configuration_form", clear_on_submit=True)
    form_dict = {}
    # define the form fields
    form.header("Account Settings")
    form_dict["binance_symbol"] = form.text_input("Binance Symbol", "BTCUSDT")
    form_dict["passphrase"] = form.text_input("Webhook Identifier", get_random_string(20))
    form_dict["max_account_risk_per_trade"] = form.slider("Max Account Risk Per Trade", 0.0, 1.0, 1.0, 0.01)
    form.subheader("Order Settings")
    form_dict["leverage"] = form.slider("Leverage", 1, 125, 1)
    form_dict["cash_bet_amount"] = form.slider("Cash Bet Amount", 0, 1000, 300)
    form_dict["order_type"] = order_type

    if form_dict["order_type"] == "limit":
        form_dict = add_limit_order_options(parent_object=form, parent_object_dict=form_dict)

    form_dict["take_profit"] = form.slider("Take Profit", 0.0, 1.0, 0.05, 0.01)
    form_dict["stop_loss"] = form.slider("Stop Loss", 0.0, 1.0, 0.01, 0.01)
    form_dict["trailing_stop_loss_percentage"] = form.slider("Trailing Stop Loss Percentage", 0.0, 1.0, 0.0015, 0.0001)
    form_dict["trailing_stop_loss_activation_percentage"] = form.slider("Trailing Stop Loss Activation Percentage", 0.0,
                                                                        1.0, 0.0015, 0.0001)

    # custom signals code beginning from defaults and adding to them if the user adds new signals etc...
    possible_actions = ["Buy", "Minimal Buy", "Strong Buy", "Minimal Strong Buy", "Exit Buy", "Sell", "Minimal Sell",
                        "Strong Sell", "Minimal Strong Sell", "Exit Sell"]
    # The default signals
    signals = dict(zip(possible_actions, possible_actions))
    for key, value in signals.items():
        signals[key] = form.selectbox(key, possible_actions, index=possible_actions.index(value))

    form_dict["signals"] = signals

    # submit the form
    submit_button = form.form_submit_button(label="Submit")

    # format the form_dict into the correct format
    configuration = {
        "Account_Settings": {
            "passphrase": form_dict["passphrase"],
            "max_account_risk_per_trade": form_dict["max_account_risk_per_trade"]
        },
        "Order_Settings": {
            "binance_symbol": form_dict["binance_symbol"],
            "leverage": form_dict["leverage"],
            "cash_bet_amount": form_dict["cash_bet_amount"],
            "order_type": form_dict["order_type"]
        },
        "Trade_Management": {
            "position_boundaries": {
                "take_profit": form_dict["take_profit"],
                "stop_loss": form_dict["stop_loss"]
            },
            "trailing_stop_loss": {
                "trailing_stop_loss_percentage": form_dict["trailing_stop_loss_percentage"],
                "trailing_stop_loss_activation_percentage": form_dict["trailing_stop_loss_activation_percentage"]
            }
        },
        "Signals": {
            "Buy": form_dict["signals"]["Buy"],
            "Minimal_Buy": form_dict["signals"]["Minimal Buy"],
            "Strong_Buy": form_dict["signals"]["Strong Buy"],
            "Minimal_Strong_Buy": form_dict["signals"]["Minimal Strong Buy"],
            "Exit_Buy": form_dict["signals"]["Exit Buy"],
            "Sell": form_dict["signals"]["Sell"],
            "Minimal_Sell": form_dict["signals"]["Minimal Sell"],
            "Strong_Sell": form_dict["signals"]["Strong Sell"],
            "Minimal_Strong_Sell": form_dict["signals"]["Minimal Strong Sell"],
            "Exit_Sell": form_dict["signals"]["Exit Sell"]
        }
    }

    if submit_button:
        # save the form data
        from dashboard_depracated.webhook_configuration.configuration_database_handler import AssetConfigurationDatabaseHandler
        asset_configurations_db_manager = AssetConfigurationDatabaseHandler(
            configuration_group_name=configuration_database_name,
            redis_host='localhost', redis_port=6379, redis_db=0, decode_responses=True
        )
        asset_configurations_db_manager.set_configuration(configuration_name, configuration)
        st.write("Configuration saved!")
        st.balloons()

        return configuration

    #
    # return configuration
