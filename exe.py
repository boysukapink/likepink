import json
import paramiko
import telebot
import time
import threading

# Load VPS details from server.json
with open('likepink/vps_list.json') as f:
    vps_list = json.load(f)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot('7881482388:AAGp8gYPg6CJh_iXNtuGYeEin7EF0UpAOlg')
admin_id = [1743096073]  # Replace with your admin IDs

successful = 0
failed = 0
successful_lock = threading.Lock()
failed_lock = threading.Lock()

def increment_counter(counter_type):
    global successful, failed
    if counter_type == 'success':
        with successful_lock:
            successful += 1
    elif counter_type == 'fail':
        with failed_lock:
            failed += 1

@bot.message_handler(commands=['cpu'])
def handle_cpu_command(message):
    if message.from_user.id not in admin_id:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    bot.reply_to(message, "Checking VPS...")

    results = [None] * len(vps_list)
    threads = []

    for i, vps in enumerate(vps_list):
        thread = threading.Thread(target=check_cpu_on_vps, args=(vps, results, i))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    response_message = "\n".join([result for result in results if result])
    bot.send_message(message.chat.id, response_message)

def check_cpu_on_vps(vps, results, index):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps['IP'], port=vps['port'], username=vps['username'], password=vps['password'], timeout=5)
        
        # Execute CPU usage command with a timeout
        stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'Cpu(s)' | sed \"s/.*, *\\([0-9.]*\\)%* id.*/\\1/\" | awk '{print 100 - $1}'", timeout=5)
        output = stdout.read().decode().strip()
        
        if output:
            status_cpu = output
            status = "🟢 Alive"
        else:
            status_cpu = "N/A"
            status = "🔴 Dead"
        
        ssh.close()
        results[index] = f"🖥️ Server {index+1} ({vps['IP']}): {status_cpu}% {status}"
    except Exception:
        results[index] = f"🖥️ Server {index+1} ({vps['IP']}): 🔴 Dead"

@bot.message_handler(commands=['exe'])
def handle_exe_command(message):
    if message.from_user.id not in admin_id:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    command = message.text[5:]  # Get the command part after "/exe "
    if not command:
        bot.reply_to(message, "Please provide a command to execute.")
        return

    results = [None] * len(vps_list)
    threads = []

    global successful, failed
    successful = 0
    failed = 0

    for i, vps in enumerate(vps_list):
        thread = threading.Thread(target=execute_command_on_vps, args=(vps, command, results, i))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    response_message = f"Berhasil: {successful}\nGagal: {failed}"
    bot.reply_to(message, response_message)

def execute_command_on_vps(vps, command, results, index):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps['IP'], port=vps['port'], username=vps['username'], password=vps['password'], timeout=5)
        stdin, stdout, stderr = ssh.exec_command(command, timeout=5)
        stdout.read().decode()  # Read stdout to ensure command completion
        stderr.read().decode()  # Read stderr to ensure command completion
        ssh.close()
        increment_counter('success')
    except Exception:
        increment_counter('fail')

# Start the bot
while True:
    try:
        print("Bot Is Running ...")
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(5)
