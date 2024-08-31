import pywhatkit
from app.Server.LLM.prompts.prompts import get_text_from_file
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class WhatsAppBot(object):
    @staticmethod
    def send_text_private_message(phone_number, message):
        logging.info(f"Sending text message to {phone_number}")
        pywhatkit.sendwhatmsg_instantly(phone_no=phone_number, message=message)

    @staticmethod
    def send_image_private_message(phone_number, image_path):
        logging.info(f"Sending image message to {phone_number} with image {image_path}")
        pywhatkit.sendwhats_image(phone_number, image_path)

    @staticmethod
    def send_text_message_to_group(group_id, message):
        logging.info(f"Sending text message to group {group_id}")
        pywhatkit.sendwhatmsg_to_group_instantly(group_id, message)

    @staticmethod
    def get_message_template(zoom_url, contact, purpose, place, password):
        logging.info(f"Getting message template for purpose {purpose}")
        current_directory = os.path.dirname(__file__)
        parent_directory = (os.path.dirname(current_directory) + f"\\prompts\\{purpose.lower()}\\" +
                            purpose + "_invitation.txt")
        return get_text_from_file(parent_directory).format(zoom_url=zoom_url, name=contact, place=place,
                                                           password=password)
