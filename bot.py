from aiogram import Bot, Dispatcher, executor, types
import datetime
import aiohttp
import os
import logging

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

async def fetch_price(session, date):
    date_str = date.strftime("%d-%m-%Y")
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/history?date={date_str}&localization=false"
    async with session.get(url) as response:
        if response.status != 200:
            return None
        data = await response.json()
        return data.get("market_data", {}).get("current_price", {}).get("usd")

@dp.message_handler(commands=['simulate'])
async def simulate(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Неверный формат запроса. Используй:\n/simulate ГГГГ-ММ СУММА")

        start_date_str, monthly_str = parts[1], parts[2]
        monthly_amount = float(monthly_str)
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m")

        now = datetime.datetime.utcnow()
        current = start_date
        total_btc = 0.0
        months = 0

        async with aiohttp.ClientSession() as session:
            while current <= now:
                price = await fetch_price(session, current)
                if price:
                    total_btc += monthly_amount / price
                    months += 1
                current += datetime.timedelta(days=32)
                current = current.replace(day=1)

            invested = months * monthly_amount

            async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd") as res:
                now_data = await res.json()
                now_price = now_data.get("bitcoin", {}).get("usd", 0)

            now_value = total_btc * now_price
            gain = now_value - invested
            emoji = "🟢" if gain > 0 else "🔴"

            await message.reply(
                f"📅 С {start_date_str} ты бы инвестировал {months} месяцев по ${monthly_amount:.2f}\n"
                f"💸 Всего вложено: ${invested:.2f}\n"
                f"🪙 Куплено BTC: {total_btc:.6f}\n"
                f"💰 Сейчас это: ${now_value:,.2f}\n"
                f"{emoji} {'PROFIT' if gain > 0 else 'LOSS'}: {gain:+,.2f}"
            )

    except Exception as e:
        await message.reply(f"⚠️ Ошибка: {str(e)}\nПример: /simulate 2015-01 100")

@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    await message.reply(
        "👋 Я бот, который покажет тебе, сколько ты проебал на BTC 😬\n\n"
        "🔍 Используй:\n"
        "`/simulate 2016-06 100` — если бы ты инвестировал $100 ежемесячно с июня 2016\n\n"
        "⚠️ Дата должна быть не раньше 2010-07\n",
        parse_mode="Markdown"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
