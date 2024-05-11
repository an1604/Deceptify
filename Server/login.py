import tkinter as tk
from tkinter import ttk
import multiprocessing

CORRECT_PASSWORD = "1234"  # Change '1234' to your actual password
root = None


def run_flask_app():
    from app import create_app  # Import your Flask app creation function
    app = create_app()


def submit_action():
    global root
    password = password_entry.get()

    if password == CORRECT_PASSWORD:
        print("Password is correct!")
        process = multiprocessing.Process(target=run_flask_app)
        process.start()
        print("Flask app started in a new process.")
        root.destroy()  # Close the GUI
    else:
        print("Incorrect password!")


def main():
    # omer 11/5/24 added flag to allow ez debug on codespace will be removed before final merge
    flag = True
    if flag:
        run_flask_app()
        return
    global root

    root = tk.Tk()
    root.title("Deceptify")
    root.geometry("240x240")

    main_frame = tk.Frame(root)
    main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    title_label = ttk.Label(main_frame, text="Deceptify", font=("Arial", 16))
    title_label.pack(pady=(0, 10))

    password_label = ttk.Label(main_frame, text="Password:")
    password_label.pack(fill=tk.X)
    global password_entry
    password_entry = ttk.Entry(main_frame, show="*")
    password_entry.pack(fill=tk.X)

    submit_button = ttk.Button(main_frame, text="Submit", command=submit_action)
    submit_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
