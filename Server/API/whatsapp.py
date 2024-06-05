
import pyautogui
import time


def open_whatsapp():
    pyautogui.press('winleft')
    time.sleep(1)
    pyautogui.write('WhatsApp')
    time.sleep(1)
    pyautogui.press('enter')


def search_contact(contact_name):
    # Click on the search bar (Ctrl + F)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    # Type the contact name
    pyautogui.write(contact_name, interval=0.1)
    time.sleep(1)
    # Press enter to select the contact
    pyautogui.press('enter')
    time.sleep(1)
    contact_x = 300  # Adjust this value
    contact_y = 200  # Adjust this value

    # Click on the contact in the search results to open the chat
    pyautogui.click(contact_x, contact_y)
    time.sleep(2)  # Wait for the chat to open

def start_call():
    # Click on the call button (assuming the call button is in a consistent position relative to the window)
    call_button_pos = pyautogui.locateCenterOnScreen('Photos/CallButton.png')  # Use an image of the call button
    if call_button_pos:
        pyautogui.click(call_button_pos)
    else:
        print("Call button not found. Please ensure the image is correct and visible on the screen.")
    time.sleep(5)  # Wait for the call to connect


if __name__ == '__main__':
    contact_name = 'Dad'  # Replace with the actual contact name

    open_whatsapp()
    search_contact(contact_name)
    start_call()

    # Stream the audio recording