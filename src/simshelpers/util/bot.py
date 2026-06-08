import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask, request
import os
import requests
from threading import Thread
from typing import Any

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

app = Flask(__name__)

@app.route("/send", methods=["POST"])
def sndmsg():
    data = request.json
    message = data.get("message", "")

    bot.loop.create_task(send_to_discord(message))

    return {"status": "ok"}

async def send_to_discord(message: Any):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)

@app.route("/send/file", methods=["POST"])
def sndfle():
    data = request.json
    file = data.get("file", "")

    bot.loop.create_task(send_file_to_discord(file))

    return {"status": "ok"}

async def send_file_to_discord(file: str):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(file=discord.File(file))

def run():
    app.run(port=5000)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def send_msg(message: Any):
    requests.post("http://127.0.0.1:5000/send",
                  json={"message": message})
    
def send_file(file: str):
    requests.post("http://127.0.0.1:5000/send/file",
                  json={"file": file})

if __name__ == "__main__":
    Thread(target=run, daemon=True).start()
    bot.run(TOKEN)