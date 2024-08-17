import time
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder
from app.Server.LLM.llm import Llm

load_dotenv()


class telegramBot(object):
    def __init__(self):
        # self.hospital_llm = Llm()
        # self.bank_llm = Llm()
        # self.delivery_llm = Llm()
        self.llm = Llm()

        self.bot_username = os.getenv('DECEPTIFYBOT_USERNAME')
        self.token = os.getenv('DECEPTIFYBOT_TOKEN')

        self.application = None
        self.init_application()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Hello there! \nIt's {self.bot_username} talking.")
        context.chat_data['state'] = 'started'

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("How can I help you?")

    async def choose_attack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.chat_data['state'] = 'choosing_attack'
        await update.message.reply_text(
            "Please choose the specific scenario: (Bank/Delivery/Hospital) to run the Demo on.")

    async def run_attack_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.chat_data.get('state') != 'attack_chosen':
            await update.message.reply_text("Please choose an attack type first using /type.")
            return

        user = update.message.from_user
        profile_name = user.username if user.username else f"{user.first_name} {user.last_name}".strip()

        self.llm.initialize_new_attack(attack_purpose=context.chat_data['attack_type'], profile_name=profile_name)
        time.sleep(5)
        await update.message.reply_text(self.llm.get_init_msg())
        context.chat_data['state'] = 'running_attack'

    async def end_attack_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.chat_data.get('state') == 'running_attack':
            await update.message.reply_text('Attack is finished!')
            context.chat_data['state'] = 'attack_finished'
        else:
            await update.message.reply_text('No attack is currently running.')

    def handle_response(self, text: str):
        response = self.llm.get_answer(text.lower())
        return response

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if context.chat_data.get('state') == 'choosing_attack':
            if text.lower() in ['bank', 'delivery', 'hospital']:
                context.chat_data['attack_type'] = text
                context.chat_data['state'] = 'attack_chosen'
                await update.message.reply_text(
                    f"Attack type '{text.capitalize()}' chosen. You can now run the attack with /run.")
            else:
                await update.message.reply_text("Invalid attack type. Please choose Bank, Delivery, or Hospital.")

        elif context.chat_data.get('state') == 'running_attack':
            response = self.handle_response(text)
            await update.message.reply_text(response)
            if self.llm.is_conversation_done():
                context.chat_data['state'] = 'attack_finished'
        else:
            await update.message.reply_text("Please choose an attack type using /type.")

    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"Update {update} caused error {context.error}")

    def init_application(self):
        self.application = ApplicationBuilder().token(self.token).build()
        self.application.add_handler(CommandHandler('start', self.start_command))
        self.application.add_handler(CommandHandler('help', self.help_command))
        self.application.add_handler(CommandHandler('type', self.choose_attack))
        self.application.add_handler(CommandHandler('run', self.run_attack_command))
        self.application.add_handler(CommandHandler('end', self.end_attack_command))

        self.application.add_handler(MessageHandler(filters.TEXT, self.handle_message))
        self.application.add_error_handler(self.error)

        print("BOT running...")
        self.application.run_polling(poll_interval=3)  # Checks every 3 sec for new messages


telegram_bot = telegramBot()
