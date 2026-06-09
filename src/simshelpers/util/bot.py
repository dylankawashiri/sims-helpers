import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask, request
import base64
import os
import requests
from io import BytesIO
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
    file_data = data.get("file", "")
    filename = data.get("filename", "image.png")

    print(f"/send/file called: filename={filename} file_data_type={type(file_data)} file_data_len={len(file_data) if isinstance(file_data, str) else 'N/A'}")
    bot.loop.create_task(send_file_to_discord(file_data, filename))

    return {"status": "ok"}

async def send_file_to_discord(file_data: str, filename: str):
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("Discord channel not found; check CHANNEL_ID and bot readiness.")
        return

    if not isinstance(file_data, str) or not file_data:
        print("No base64 file data provided.")
        return

    file_data = file_data.strip()
    if file_data.startswith("data:"):
        file_data = file_data.split(",", 1)[1]

    try:
        decoded = base64.b64decode(file_data)
    except (base64.binascii.Error, TypeError) as exc:
        print(f"Base64 decode failed: {exc}")
        return

    print(f"Decoded file bytes: {len(decoded)} bytes")
    file_obj = BytesIO(decoded)
    file_obj.seek(0)
    try:
        await channel.send(file=discord.File(file_obj, filename=filename))
        print("Image file sent successfully.")
    except Exception as exc:
        print(f"Failed to send decoded file to Discord: {exc}")

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
                  json={"file": file,
                        "filename": "image.png"})

if __name__ == "__main__":
    Thread(target=run, daemon=True).start()
    bot.run(TOKEN)