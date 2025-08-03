import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("RENDER_URL") + WEBHOOK_PATH
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 5000))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_handler(msg: types.Message):
    await msg.answer("👋 Привет! Проверь свою упущенную прибыль в WebApp.")

@dp.message_handler()
async def group_reply(msg: types.Message):
    if msg.chat.type in ('group', 'supergroup') and "btc" in msg.text.lower():
        await msg.reply("⚠️ Хочешь узнать, сколько ты бы заработал на BTC? Жми в WebApp.")

@dp.inline_handler()
async def inline_reply(query: types.InlineQuery):
    results = [types.InlineQueryResultArticle(
        id="1",
        title="BTC Потери",
        input_message_content=types.InputTextMessageContent("🤖 Запусти WebApp и узнай, сколько бы ты поднял!"),
        description="BTC-профит симуляция"
    )]
    await bot.answer_inline_query(query.id, results)

async def on_startup(dp): await bot.set_webhook(WEBHOOK_URL)
async def on_shutdown(dp): await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )
