import psutil
import time
import ctypes
import pystray
from PIL import Image, ImageDraw
import threading
import subprocess
import csv
import os

def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

FILE_PATH = 'heaviest_process_FULL_log.csv'

def create_image(width, height):
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((0, 0, width, height), fill=(255, 0, 0, 255))
    return image

def on_quit(icon, item):
    icon.stop()

def open_file(icon, item):
    try:
        subprocess.Popen(['notepad.exe', FILE_PATH])  # Для Windows
    except Exception as e:
        print(f"Ошибка при открытии файла: {e}")

def clear_file(icon, item):
    try:
        with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['PID', 'Name', 'CPU Usage (%)', 'Path', 'Parent Chain'])
    except Exception as e:
        print(f"Ошибка при очистке файла: {e}")

def run_in_background():
    last_pid = 0

    # Если файл не существует, создать его с заголовками
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['PID', 'Name', 'CPU Usage (%)', 'Path', 'Parent Chain'])

    while True:
        try:
            processes = [(proc.info['pid'], proc.info['name'], proc.info['cpu_percent'], proc)
                         for proc in psutil.process_iter(['pid', 'name', 'cpu_percent'])]

            # Исключить "System Idle Process" (только для Windows)
            processes = [proc for proc in processes if proc[1] != "System Idle Process"]

            if processes:
                heaviest_process = max(processes, key=lambda x: x[2])
                pid, name, cpu_usage, proc = heaviest_process

                # Попробовать получить путь к процессу
                try:
                    exe_path = proc.exe()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    exe_path = "Недоступно"

                # Получить всю цепочку родителей до корня
                parent_chain = []
                current_proc = proc
                while True:
                    try:
                        parent_proc = current_proc.parent()
                        if not parent_proc:
                            break
                        parent_pid = parent_proc.pid
                        parent_name = parent_proc.name()
                        try:
                            parent_path = parent_proc.exe()
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            parent_path = "Недоступно"
                        parent_chain.append(f"PID: {parent_pid}, Name: {parent_name}, Path: {parent_path}")
                        current_proc = parent_proc
                    except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                        break

                parent_chain_str = " -> ".join(parent_chain) if parent_chain else "Нет данных о родителях"

                if last_pid != pid:
                    with open(FILE_PATH, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([pid, name, round(cpu_usage / 10, 2), exe_path, parent_chain_str])
                last_pid = pid
        except Exception as e:
            with open(FILE_PATH, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Ошибка', str(e)])

        time.sleep(1)

def setup(icon):
    icon.visible = True

hide_console()

icon = pystray.Icon("test_icon", create_image(64, 64), "MHP_CPU_PRO", menu=pystray.Menu(
    pystray.MenuItem("Открыть файл", open_file),
    pystray.MenuItem("Очистить файл", clear_file),
    pystray.MenuItem("Выход", on_quit)
))

threading.Thread(target=run_in_background, daemon=True).start()

icon.run(setup)
