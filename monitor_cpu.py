import psutil
import time
import ctypes
import pystray
from PIL import Image, ImageDraw
import threading
import subprocess

def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

FILE_PATH = 'heaviest_process_log.txt'
def create_image(width, height):
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((0, 0, width, height), fill=(0, 0, 255, 255))
    return image

def on_quit(icon, item):
    icon.stop()

def open_file(icon, item):
    try:
        subprocess.Popen(['notepad.exe', FILE_PATH])  # Для Windows
        # Для Linux: subprocess.Popen(['xdg-open', FILE_PATH])
        # Для macOS: subprocess.Popen(['open', FILE_PATH])
    except Exception as e:
        print(f"Ошибка при открытии файла: {e}")


def clear_file(icon, item):
    try:
        with open(FILE_PATH, 'w') as f:
            f.write('')
    except Exception as e:
        print(f"Ошибка при очистке файла: {e}")


def run_in_background():
    log_file = "heaviest_process_log.txt"
    last_pid = 0
    while True:
        processes = [(proc.info['pid'], proc.info['name'], proc.info['cpu_percent'])
                     for proc in psutil.process_iter(['pid', 'name', 'cpu_percent'])]

        processes = [proc for proc in processes if proc[1] != "System Idle Process"]

        if processes:
            heaviest_process = max(processes, key=lambda x: x[2])
            pid, name, cpu_usage = heaviest_process
            
            if last_pid != pid:
                with open(log_file, 'a') as f:
                    f.write(f"PID: {pid}, Name: {name}, CPU Usage: {round(cpu_usage/10, 2)}%\n")
            last_pid = pid
        time.sleep(1)

def setup(icon):
    icon.visible = True

hide_console()

icon = pystray.Icon("test_icon", create_image(64, 64), "MHP_CPU", menu=pystray.Menu(
    pystray.MenuItem("Открыть файл", open_file),
    pystray.MenuItem("Очистить файл", clear_file),
    pystray.MenuItem("Выход", on_quit)
))

threading.Thread(target=run_in_background, daemon=True).start()

icon.run(setup)
