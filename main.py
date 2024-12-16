import json
import os
import paramiko
import threading
import time
import subprocess
import validators
from pyrogram import Client, filters
from pyrogram.types import Message
import telebot

# Telegram Bot API configuration
BOT_TOKEN = "7881482388:AAGp8gYPg6CJh_iXNtuGYeEin7EF0UpAOlg"
API_ID = 26323194
API_HASH = "b85b75c7631c4aabc6084a2202952f67"
admin_id = [1743096073]

# Files and constants
VPS_FILE = "vps_list.json"
tls_script = "tls.js"
proxy_file = "proxy.txt"

# Load VPS details
if not os.path.isfile(VPS_FILE):
    with open(VPS_FILE, "w") as file:
        json.dump([], file)

with open(VPS_FILE) as f:
    vps_list = json.load(f)

# Pyrogram bot instance
app = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
# Telebot instance
bot = telebot.TeleBot(BOT_TOKEN)

successful = 0
failed = 0
successful_lock = threading.Lock()
failed_lock = threading.Lock()

# Helper functions
def increment_counter(counter_type):
    global successful, failed
    if counter_type == 'success':
        with successful_lock:
            successful += 1
    elif counter_type == 'fail':
        with failed_lock:
            failed += 1

def load_vps():
    with open(VPS_FILE, "r") as file:
        return json.load(file)

def save_vps(vps_list):
    with open(VPS_FILE, "w") as file:
        json.dump(vps_list, file, indent=4)

def execute_ssh_command(host, port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()
        return output if output else error
    except Exception as e:
        return f"Error: {str(e)}"

# CPU check for Telebot
@bot.message_handler(commands=['cpu'])
def handle_cpu_command(message):
    if message.from_user.id not in admin_id:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    bot.reply_to(message, "Checking VPS...")
    results = [None] * len(vps_list)
    threads = []

    def check_cpu_on_vps(vps, results, index):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(vps['host'], port=vps['port'], username=vps['username'], password=vps['password'], timeout=5)
            stdin, stdout, stderr = ssh.exec_command(
                "top -bn1 | grep 'Cpu(s)' | sed \"s/.*, *\\([0-9.]*\\)%* id.*/\\1/\" | awk '{print 100 - $1}'")
            output = stdout.read().decode().strip()
            ssh.close()
            results[index] = f"🖥️ Server {index+1} ({vps['host']}): {output}% 🟢 Alive"
        except Exception:
            results[index] = f"🖥️ Server {index+1} ({vps['host']}): 🔴 Dead"

    for i, vps in enumerate(vps_list):
        thread = threading.Thread(target=check_cpu_on_vps, args=(vps, results, i))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    response_message = "\n".join([result for result in results if result])
    bot.send_message(message.chat.id, response_message)

# Pyrogram commands
@app.on_message(filters.command("addvps") & filters.private)
async def add_vps(client: Client, message: Message):
    try:
        _, host, port, username, password = message.text.split(maxsplit=4)
        port = int(port)
        vps_list = load_vps()
        if any(vps['host'] == host and vps['port'] == port for vps in vps_list):
            await message.reply("VPS ini sudah terdaftar.")
            return
        vps_list.append({"host": host, "port": port, "username": username, "password": password})
        save_vps(vps_list)
        await message.reply(f"VPS {host}:{port} berhasil ditambahkan!")
    except ValueError:
        await message.reply("Gunakan format: /addvps [host] [port] [username] [password]")

@app.on_message(filters.command("listvps") & filters.private)
async def list_vps(client: Client, message: Message):
    vps_list = load_vps()
    if vps_list:
        reply = "Daftar VPS yang terhubung:\n"
        for vps in vps_list:
            reply += f"- {vps['host']}:{vps['port']} (user: {vps['username']})\n"
        await message.reply(reply)
    else:
        await message.reply("Tidak ada VPS yang terdaftar.")

@app.on_message(filters.command("help") & filters.private)
async def help(client: Client, message: Message):
    helpss = (
        "<b>📜 Help Menu:</b>\n\n"
        "/addvps - Tambah VPS\n"
        "/listvps - Daftar VPS\n"
        "/delvps - Hapus VPS\n"
        "/cpu - Cek CPU VPS (Telebot)\n"
    )
    await message.reply(helpss)

if __name__ == "__main__":
    print("Bot is running...")
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run()
