from time import sleep
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta, time
import pandas as pd
from pya3 import *
from dotenv import load_dotenv
import os
import logging
import json

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    filename="trading_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s - Line:%(lineno)d",
)

env_api_key = os.getenv("API_KEY")
env_user_id = os.getenv("USER_ID")


"""--------------------SESSONCREATED--------------------------"""
api_key = env_api_key
user_id = env_user_id
logging.info(api_key)

alice = Aliceblue(user_id=user_id, api_key=api_key)
sesson = alice.get_session_id()
if "sessionID" in sesson:
    session_id = sesson["sessionID"]

LTP = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []

def socket_open():  # Socket open callback function
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag:  # This is used to resubscribe the script when reconnect the socket.
        alice.subscribe(subscribe_list)

def socket_close():  # On Socket close this callback function will trigger
    global socket_opened, LTP
    socket_opened = False
    LTP = 0
    print("Closed")

def socket_error(message):  # Socket Error Message will receive in this callback function
    global LTP
    LTP = 0
    print("Error :", message)

def feed_data(message):  # Socket feed data will receive in this callback function
    global LTP, subscribe_flag
    feed_message = json.loads(message)
    # print(feed_message)
    if feed_message["t"] == "ck":
        print("Connection Acknowledgement status :%s (Websocket Connected)" % feed_message["s"])
        subscribe_flag = True
        print("subscribe_flag :", subscribe_flag)
        print("-------------------------------------------------------------------------------")
        pass
    elif feed_message["t"] == "tk":
        print("Token Acknowledgement status :%s " % feed_message)
        print("-------------------------------------------------------------------------------")
        pass
    else:
        print("Feed :", feed_message)
        LTP = feed_message[
            'lp'] if 'lp' in feed_message else LTP  # If LTP in the response it will store in LTP variable

# Socket Connection Request
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                    socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True,market_depth=True)

while not socket_opened:
    pass

subscribe_list = [alice.get_instrument_by_token('INDICES', 26000)]
alice.subscribe(subscribe_list)
print(datetime.now())
sleep(10)
print(datetime.now())
# unsubscribe_list = [alice.get_instrument_by_symbol("NSE", "RELIANCE")]
# alice.unsubscribe(unsubscribe_list)
# sleep(8)

# Stop the websocket
# alice.stop_websocket()
# sleep(10)
# print(datetime.now())

# Connect the socket after socket close
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                    socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)

