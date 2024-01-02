import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta, time
import pandas as pd
from pya3 import *
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

env_api_key = os.getenv("API_KEY")
env_user_id = os.getenv("USER_ID")

class MyAppGUI:
    def __init__(self, master):
        self.master = master
        master.title("My Trading App")

        # Create the main frame
        self.frame = tk.Frame(master, padx=10, pady=10)
        self.frame.pack()

        # Create labels and entry widgets for api_key, user_id, and quantity
        self.api_key_label = tk.Label(self.frame, text="Enter API Key:")
        self.api_key_label.grid(row=0, column=0, padx=5, pady=5)
        self.api_key_entry = tk.Entry(self.frame)
        self.api_key_entry.insert(0, env_api_key)
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5)

        self.user_id_label = tk.Label(self.frame, text="Enter User ID:")
        self.user_id_label.grid(row=1, column=0, padx=5, pady=5)
        self.user_id_entry = tk.Entry(self.frame)
        self.user_id_entry.insert(0, env_user_id)
        self.user_id_entry.grid(row=1, column=1, padx=5, pady=5)

        self.quantity_label = tk.Label(self.frame, text="Enter Quantity:")
        self.quantity_label.grid(row=2, column=0, padx=5, pady=5)
        self.qty_entry = tk.Entry(self.frame)
        self.qty_entry.grid(row=2, column=1, padx=5, pady=5)

        # Create a button for starting the algorithm
        self.start_button = tk.Button(self.frame, text="Start Algorithm", command=self.on_start_button_press)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Create a label to display the result
        self.result_label = tk.Label(self.frame, text="")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

    def on_start_button_press(self):
        try:
            # Get quantity from the entry widget

            quantity = int(self.qty_entry.get())
            """--------------------SESSONCREATED--------------------------"""
            api_key = self.api_key_entry.get()
            user_id = self.user_id_entry.get()
            print(api_key)
            # api_key = "5hJsnsI6JKCIz3evZh91UPkJusZbAIKUi9fYlofDunQY3IC6KpWxd5x6c3z7FxbQfLuhKqyqpLV1h3ZiYqJaroajqr0sfYdOOGJTfrB8bL3IGyfBfI2v4eLlK6NIemQ7"
            # user_id = "928750"

            alice = Aliceblue(user_id=user_id, api_key=api_key)
            sesson = alice.get_session_id()
            if "sessionID" in sesson:
                session_id = sesson["sessionID"]

            alice.get_contract_master("NFO")

            """--------------------DWNLOADNFOCSV--------------------------"""

            df = pd.read_csv("NFO.csv")
            df["Expiry Date"] = pd.to_datetime(df["Expiry Date"], format="%Y-%m-%d")

            today = datetime.now().date()
            filtered_df = df[
                (df["Symbol"] == "BANKNIFTY") & (df["Expiry Date"] >= pd.to_datetime(today))
            ]

            nearest_expiry_date = filtered_df["Expiry Date"].min()

            final_trading_instruments = filtered_df[
                filtered_df["Expiry Date"] == nearest_expiry_date
            ]

            """--------------------NIFTYBANKHISTORYDATA--------------------------"""
            instrument = alice.get_instrument_by_symbol("INDICES", "NIFTY BANK")
            from_datetime = datetime.now() - timedelta(days=5)
            to_datetime = datetime.now()
            interval = "D"
            indices = True
            history_data = alice.get_historical(
                instrument, from_datetime, to_datetime, interval, indices
            )

            df = pd.DataFrame(history_data)

            df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%m-%d %H:%M:%S")

            today = datetime.now().date()
            past_data = df[df["datetime"].dt.date < today]

            # Get the last close value from the past data
            last_close_value = past_data["close"].iloc[-1]  # LAST CLOSE FOR BANKNIFTY

            # Display the result
            print("Last close value from past data:", last_close_value)

            """--------------------LIVE DATA FOR NIFTY AND INSTRUMNT--------------------------"""
            strick_selection = False
            stricked_instrument = None
            entry_order_placed = False

            current_time = datetime.now()
            target_time = time(9, 15)

            current_day = datetime.now().weekday()
            price = 100.0
            size = 15

            if current_day == 0:  # Monday
                price = 200.0
            elif current_day == 1:  # Tuesday
                price = 150.0
            elif current_day == 2:  # Wednesday
                price = 100.0
            elif current_day == 3:  # Thursday
                price = 300.0
            elif current_day == 4:  # Friday
                price = 250.0

            while True:
                sleep(1)
                if current_time.time() >= target_time:
                    if not strick_selection:
                        print("We are in now. as time is:", current_time.time())
                        current_ltp_banknifty = alice.get_scrip_info(
                            alice.get_instrument_by_token("INDICES", 26009)
                        )
                        # print(current_ltp_banknifty, "--<<")
                        banknifty_ltp = float(current_ltp_banknifty["openPrice"])
                        # print(banknifty_ltp, "---")

                        x = banknifty_ltp - banknifty_ltp % 100
                        if banknifty_ltp % 100 >= 50:
                            x = x + 100

                        float_strick = int(x)
                        # print(float_strick)
                        # print("===")

                        if last_close_value > banknifty_ltp:
                            option_type = "PE"
                        else:
                            option_type = "CE"

                        # print(final_trading_instruments, "----final_trading_instruments")
                        stricked_instrument = final_trading_instruments[
                            (filtered_df["Strike Price"] == float_strick)
                            & (filtered_df["Option Type"] == option_type)
                        ].iloc[0]

                        print("Instrument selected:", stricked_instrument)

                        strick_selection = True
                        
                        
                    elif strick_selection and not entry_order_placed:
                        inst_data = stricked_instrument
                        
                        size = int(int(inst_data["Lot Size"]) * int(quantity))
                        instrument_ltp_price = alice.get_scrip_info(
                            alice.get_instrument_by_token("NFO", int(inst_data["Token"]))
                        )
                        
                        if float(instrument_ltp_price["LTP"]) < float(price):
                            
                            # print("-----------------")
                            # print(instrument_ltp_price)
                            # """{'optiontype': 'XX', 'SQty': 390, 
                            # 'vwapAveragePrice': '183.75', 'LTQ': '15', 
                            # 'DecimalPrecision': 2, 'openPrice': '226.85', 
                            # 'LTP': '241.25', 'Ltp': '241.25', 'BRate': '240.00', 
                            # 'defmktproval': '0', 'symbolname': 'BANKNIFTY', 
                            # 'noMktPro': '0', 'BQty': 150, 'mktpro': '0', 'LTT': '15:29:59', 
                            # 'TickSize': '0.05', 'Multiplier': 1, 'strikeprice': '48200.00', 
                            # 'TotalSell': '72758430', 'High': '299.60', 'stat': 'Ok', 'yearlyLowPrice': '0',
                            # 'yearlyHighPrice': '0', 'exchFeedTime': '15:29:59', 'BodLotQty': 15, 
                            # 'PrvClose': '0', 'Change': '00.00', 'SRate': '241.95', 'Series': 'XX', 
                            # 'TotalBuy': '72758430', 'Low': '92.65', 'UniqueKey': 'NA',
                            # 'PerChange': '00.00', 'companyname': None, 'TradeVolume': '72758430',
                            # 'TSymbl': 'BANKNIFTY03JAN24P48200', 'Exp': 'NA', 'LTD': '15:29:59'}"""
                            # print("-----------------")
                            
                            print("Condition met we are placing entry order: ltp", instrument_ltp_price["LTP"])
                            print("Triggure price:", price)
                            
                            order = alice.place_order(
                                transaction_type=TransactionType.Buy,
                                instrument=instrument_ltp_price,
                                quantity=size,
                                order_type=OrderType.Market,
                                product_type=ProductType.Delivery,
                                price=0.0,
                                trigger_price=None,
                                stop_loss=None,
                                square_off=None,
                                trailing_sl=None,
                                is_amo=False,
                                order_tag="HimalayTradeTron",
                            )
                            
                            entry_order_placed = True
                            print(order, ": exit order")
                            
                            price = price + price*0.1
                            print("Triggure setup to 10% profit:", price)
                            
                    elif strick_selection and entry_order_placed:
                        inst_data = stricked_instrument
                        
                        instrument_ltp_price = alice.get_scrip_info(
                            alice.get_instrument_by_token("NFO", int(inst_data["Token"]))
                        )
                        
                        if float(instrument_ltp_price["LTP"]) >= float(price):
                            
                            print("Condition met we are placing exit order: ltp", instrument_ltp_price["LTP"])
                            print("Triggure price:", price)
                            
                            order = alice.place_order(
                                transaction_type=TransactionType.Sell,
                                instrument=instrument_ltp_price,
                                quantity=size,
                                order_type=OrderType.Market,
                                product_type=ProductType.Delivery,
                                price=0.0,
                                trigger_price=None,
                                stop_loss=None,
                                square_off=None,
                                trailing_sl=None,
                                is_amo=False,
                                order_tag="HimalayTradeTron",
                            )
                            print(order, ": exit order")
                            self.master.destroy() #close gui after coosing to exit

        except Exception as e:
            # Display an error message if the quantity is not a valid integer
            messagebox.showerror("Error", f"Please enter a valid quantity. - {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MyAppGUI(root)
    root.mainloop()
