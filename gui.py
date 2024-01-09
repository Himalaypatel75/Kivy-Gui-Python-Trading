from time import sleep
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta, time
import pandas as pd
from pya3 import *
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    filename="trading_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s - Line:%(lineno)d",
)

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
        self.start_button = tk.Button(
            self.frame, text="Start Algorithm", command=self.on_start_button_press
        )
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
            logging.info(api_key)

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
                (df["Symbol"] == "BANKNIFTY")
                & (df["Expiry Date"] >= pd.to_datetime(today))
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
            logging.info(f"Last close value from past data: {last_close_value}")

            """--------------------LIVE DATA FOR NIFTY AND INSTRUMNT--------------------------"""
            strick_selection = False
            stricked_instrument = None
            entry_order_placed = False

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
            instrument = None

            test = False
            date_format = "%Y-%m-%d %H:%M:%S"
            
            while True:
                current_time = datetime.now()
                sleep(1)

                if current_time.time() >= target_time:
                    if not strick_selection:
                        logging.info(
                            f"We are in now. as time is: {current_time.time()}"
                        )

                        current_ltp_banknifty = alice.get_scrip_info(
                            alice.get_instrument_by_token("INDICES", 26009)
                        )

                        logging.info(current_ltp_banknifty)
                        banknifty_ltp = float(current_ltp_banknifty["openPrice"])
                        logging.info(banknifty_ltp)

                        x = banknifty_ltp - banknifty_ltp % 100
                        if banknifty_ltp % 100 >= 50:
                            x = x + 100

                        float_strick = int(x)
                        logging.info(float_strick)

                        if last_close_value > banknifty_ltp:
                            option_type = "PE"
                        else:
                            option_type = "CE"

                        logging.info(final_trading_instruments)

                        stricked_instrument = final_trading_instruments[
                            (filtered_df["Strike Price"] == float_strick)
                            & (filtered_df["Option Type"] == option_type)
                        ].iloc[0]

                        logging.info(f"Instrument selected: {stricked_instrument}")

                        strick_selection = True

                    elif strick_selection and not entry_order_placed:
                        inst_data = stricked_instrument

                        size = int(inst_data["Lot Size"]) * int(quantity)
                        
                        instrument_ltp_price = alice.get_scrip_info(
                            alice.get_instrument_by_token("NFO", int(inst_data["Token"]))
                        )
                        print(instrument_ltp_price,"instrument_ltp_price")
                        if (
                            float(instrument_ltp_price["LTP"]) - 1
                            <= float(price)
                            <= float(instrument_ltp_price["LTP"]) + 1
                        ) or test:
                            logging.info(f"instrument - {instrument_ltp_price}")
                            logging.info(
                                f"instrument type - {type(instrument_ltp_price)}"
                            )
                            logging.info(
                                f"Condition met we are placing entry order: ltp {instrument_ltp_price['LTP']}"
                            )
                            logging.info(f"Triggure price: {price}")
                            logging.info(f"size - {size}")
                            # date_format = "%Y-%m-%d %H:%M:%S"
                            # instrument = Instrument(
                            #     exchange=inst_data["Exchange Segment"],
                            #     token=inst_data["Token"],
                            #     symbol=inst_data["Symbol"],
                            #     name="Instrument Name",  # Corrected the syntax here
                            #     expiry=datetime.strptime(
                            #         str(inst_data["Expiry Date"]), date_format
                            #     ).date(),
                            #     lot_size=float(inst_data["Lot Size"]),
                            # )

                            order = alice.place_order(
                                transaction_type=TransactionType.Buy,
                                instrument= alice.get_instrument_for_fno(exch="NFO",symbol=inst_data["Symbol"], expiry_date=str(datetime.strptime(str(inst_data["Expiry Date"]), date_format).date()), is_fut=False,strike=inst_data["Strike Price"], is_CE=(option_type  == "CE")),
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
                            logging.info(f"{order} : exit order")

                            price = price + price * 0.1
                            logging.info(f"Triggure setup to 10% profit: {price}")

                    elif strick_selection and entry_order_placed:
                        inst_data = stricked_instrument

                        instrument_ltp_price = alice.get_scrip_info(
                            alice.get_instrument_by_token("NFO", int(inst_data["Token"]))
                        )

                        print(instrument_ltp_price,"---")
                        if (
                            float(instrument_ltp_price["LTP"]) - 1
                            <= float(price)
                            <= float(instrument_ltp_price["LTP"]) + 1
                        ) or test:
                            logging.info(
                                f"Condition met we are placing exit order: ltp {instrument_ltp_price['LTP']}"
                            )
                            logging.info(f"Triggure price: {price}")

                            order = alice.place_order(
                                transaction_type=TransactionType.Sell,
                                instrument=alice.get_instrument_for_fno(exch="NFO",symbol=inst_data["Symbol"], expiry_date=str(datetime.strptime(str(inst_data["Expiry Date"]), date_format).date()), is_fut=False,strike=inst_data["Strike Price"], is_CE=(option_type  == "CE")),
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
                            break
                            logging.info(f"{order} : exit order")

        except Exception as e:
            import traceback
            error_message = f"An error occurred: {e}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error", error_message)
            logging.info(f"Error: {error_message}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MyAppGUI(root)
    root.mainloop()
