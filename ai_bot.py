import os
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
AI_CHANNEL_ID = 1524041767580733630  # ← замени на ID канала

# МОДЕЛЬ: выбери любую бесплатную и впиши сюда
MODEL = "poolside/laguna-xs-2.1:free"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ИИ-бот {bot.user} готов!")

@bot.command(name="ии")
@commands.cooldown(1, 5, commands.BucketType.user)
async def ask_ai(ctx, *, question: str = None):
    if ctx.channel.id != AI_CHANNEL_ID:
        return
    if not question:
        await ctx.send("Напиши вопрос после `!ии`. Например: `!ии Как дела?`")
        return

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        await ctx.send("ИИ пока не настроен. Нужен ключ OpenRouter (бесплатно).")
        return

    if len(question) > 300:
        await ctx.send("Вопрос слишком длинный. Сократи до 300 символов.")
        return

    async with ctx.typing():
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": MODEL,
                "messages": [{"role": "user", "content": question}],
                "max_tokens": 200,
                "temperature": 0.7
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            data = response.json()

            if "choices" not in data:
                error_msg = data.get("error", {}).get("message", "Неизвестная ошибка API")
                await ctx.send(f"Ошибка API: {error_msg}")
                return

            answer = data["choices"][0]["message"]["content"]
            if not answer or not answer.strip():
                await ctx.send("Нейросеть вернула пустой ответ.")
                return

            if len(answer) > 1000:
                answer = answer[:1000] + "..."
            await ctx.reply(answer, mention_author=False)

        except Exception as e:
            await ctx.send(f"Ошибка: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)
    
