import pywhatkit
import time


def whatsapp(phone_number, message):
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min

    minute += 1
    pywhatkit.sendwhatmsg(phone_no=phone_number, message=message, time_hour=hour, time_min=minute)
    