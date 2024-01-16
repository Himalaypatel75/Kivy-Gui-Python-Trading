import tkinter as tk
from tkinter import Label, Entry, Button

class KotakTradeClonerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kotak-Trade Cloner")

        # Parent Account Section
        parent_label = Label(root, text="Source Account", font=("Helvetica", 16, "bold"))
        parent_label.grid(row=0, column=0, columnspan=3, pady=10)

        self.create_entry("Access Token:", 1, "parent_access_token")
        self.create_entry("Consumer Key:", 2, "parent_consumer_key")
        self.create_entry("App ID:", 3, "parent_app_id")
        self.create_entry("User ID:", 4, "parent_user_id")
        self.create_entry("Password:", 5, "parent_password")
        self.create_entry("Access Code:", 6, "parent_access_code")

        # Child Account Section
        child_label = Label(root, text="End Account", font=("Helvetica", 16, "bold"))
        child_label.grid(row=7, column=0, columnspan=3, pady=10)

        self.create_entry("Access Token:", 8, "child_access_token")
        self.create_entry("Consumer Key:", 9, "child_consumer_key")
        self.create_entry("App ID:", 10, "child_app_id")
        self.create_entry("User ID:", 11, "child_user_id")
        self.create_entry("Password:", 12, "child_password")
        self.create_entry("Access Code:", 13, "child_access_code")

        # Buttons
        submit_button = Button(root, text="Submit", command=self.submit_details)
        submit_button.grid(row=14, column=0, columnspan=3, pady=10)

        save_parent_button = Button(root, text="Save Parent", command=lambda: self.save_values("parent"))
        save_parent_button.grid(row=15, column=0, columnspan=3, pady=5)

        save_child_button = Button(root, text="Save Child", command=lambda: self.save_values("child"))
        save_child_button.grid(row=16, column=0, columnspan=3, pady=5)

    def create_entry(self, label_text, row, entry_name):
        label = Label(self.root, text=label_text)
        label.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        entry = Entry(self.root, show="*") if "password" in entry_name else Entry(self.root)
        entry.grid(row=row, column=1, columnspan=2, padx=10, pady=5)
        setattr(self, entry_name, entry)

    def submit_details(self):
        # Perform actions when Submit button is clicked
        # Example: You can print the values or perform further processing
        print("Parent Access Token:", self.parent_access_token.get())
        print("Child Access Token:", self.child_access_token.get())

    def save_values(self, account_type):
        # Perform actions when Save button is clicked
        # Example: Save values to a file or database
        if account_type == "parent":
            print("Saving Source Account")
        elif account_type == "child":
            print("Saving End Account")

if __name__ == "__main__":
    root = tk.Tk()
    app = KotakTradeClonerApp(root)
    root.mainloop()
