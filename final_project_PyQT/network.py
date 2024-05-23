import requests
from tkinter import messagebox
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

SERVER_URL = os.getenv('SERVER_URL')

def create_user(username, password):
    try:
        url = f"{SERVER_URL}/data"
        data = {"username": username, "password": password}
        response = requests.post(url, json=data)
        if response.status_code == 409:
            messagebox.showerror("Error", "Username already exists.")
            return False
        response.raise_for_status()
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            messagebox.showerror("Error", "Failed to decode server response.")
            print(f"Server response: {response.text}")
            return False
        messagebox.showinfo("Success", f"User created successfully! ID: {result.get('id')}")
        return True
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to create user: {str(e)}")
        return False

def login(username, password):
    try:
        url = f"{SERVER_URL}/login"
        data = {"username": username, "password": password}
        response = requests.post(url, json=data)
        if response.status_code == 401:
            messagebox.showerror("Error", "Username or password are incorrect.")
            return False
        response.raise_for_status()
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            messagebox.showerror("Error", "Failed to decode server response.")
            print(f"Server response: {response.text}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Login failed: {str(e)}")
        return False
