import psutil
import time
import csv
import os
import ctypes
from datetime import datetime
from PIL import Image, ImageDraw
import threading
import subprocess
import pystray

# Путь к файлу лога
FILE_PATH = 'terminated_process_log.csv'

def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def create_image(width, height):
    """
    Создание иконки для трея.
    """
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((0, 0, width, height), fill=(0, 255, 0, 255))
    return image

def open_file(icon, item):
    """
    Открыть лог-файл в текстовом редакторе.
    """
    try:
        subprocess.Popen(['notepad.exe', FILE_PATH])  # Для Windows
    except Exception as e:
        print(f"Ошибка при открытии файла: {e}")

def clear_file(icon, item):
    """
    Очистить лог-файл.
    """
    try:
        with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'PID', 'Name', 'Path', 'Parent Chain', 'Terminated By'])
    except Exception as e:
        print(f"Ошибка при очистке файла: {e}")

def on_quit(icon, item):
    """
    Завершение программы.
    """
    icon.stop()

def get_process_chain(proc):
    """
    Получает цепочку родительских процессов для заданного процесса.
    """
    chain = []
    try:
        while proc:
            parent_pid = proc.pid
            parent_name = proc.name()
            try:
                parent_path = proc.exe()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                parent_path = "Недоступно"
            chain.append(f"PID: {parent_pid}, Name: {parent_name}, Path: {parent_path}")
            proc = proc.parent()
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass
    return " -> ".join(chain) if chain else "Нет данных о родителях"

def monitor_terminated_processes():
    """
    Отслеживает завершение процессов и записывает данные о завершенных процессах в файл.
    """
    # Если файл не существует, создать его с заголовками
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'PID', 'Name', 'Path', 'Parent Chain', 'Terminated By'])

    # Состояние процессов на момент запуска программы
    known_processes = {proc.pid: proc for proc in psutil.process_iter(['pid', 'name', 'exe', 'ppid'])}

    while True:
        try:
            current_processes = {proc.pid: proc for proc in psutil.process_iter(['pid', 'name', 'exe', 'ppid'])}
            terminated_pids = set(known_processes.keys()) - set(current_processes.keys())

            for pid in terminated_pids:
                terminated_proc = known_processes[pid]
                name = terminated_proc.name()
                try:
                    path = terminated_proc.exe()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    path = "Недоступно"
                parent_chain = get_process_chain(terminated_proc)
                terminated_by = "Неизвестно"  # Информацию о завершившем процессе определить нельзя

                # Запись в файл
                with open(FILE_PATH, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([datetime.now(), pid, name, path, parent_chain, terminated_by])

            # Обновление состояния
            known_processes = current_processes

        except Exception as e:
            with open(FILE_PATH, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now(), 'Ошибка', str(e)])

        time.sleep(1)  # Интервал проверки

def setup(icon):
    """
    Установить иконку видимой.
    """
    icon.visible = True

if __name__ == "__main__":
    # Скрыть консоль
    hide_console()

    # Создать иконку для трея
    icon = pystray.Icon("terminated_process_monitor", create_image(64, 64), "MKP_SYS", menu=pystray.Menu(
        pystray.MenuItem("Открыть файл", open_file),
        pystray.MenuItem("Очистить файл", clear_file),
        pystray.MenuItem("Выход", on_quit)
    ))

    # Запустить мониторинг процессов в отдельном потоке
    threading.Thread(target=monitor_terminated_processes, daemon=True).start()

    # Запустить иконку в трее
    icon.run(setup)
