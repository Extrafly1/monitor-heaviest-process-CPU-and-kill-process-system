**Монитор CPU: отслеживание процесса с наибольшим потреблением CPU**
==================================================================================================================

**О программе**
---------------------

Эта программа представляет собой легковесный монитор процессов Windows, который отслеживает процесс с наибольшим потреблением CPU и записывает информацию в текстовый файл. Программа также предоставляет функциональность для открытия файла и очистки его содержимого.

**Функции**
--------------

* **Открытие файла**: Открывает файл с логами процесса с наибольшим потреблением CPU.
* **Очистка файла**: Очищает содержимое файла логов процесса с наибольшим потреблением CPU.
* **Выход**: Закрывает программу и убирает из системного трея.

### Преимущества

* Позволяет отслеживать использование процессорных ресурсов компьютера.
* Сохраняет данные о процессе в лог-файле, что позволяет анализировать историю использования CPU.
* Предоставляет функцию очистки лог-файла для удаления устаревших записей.

**Требования**
--------------------

* Python 3.x
* Библиотеки:
  * `psutil` для отслеживания процессов
  * `ctypes` для скрытия консоли
  * `pystray` для создания системной иконки
  * `PIL` для работы с изображениями

**Установка**
------------------

Программа уже собрана в исполняемый файл, поэтому вам не нужно ничего устанавливать. Просто скачайте файл и запустите его.

**Пользовательский интерфейс**
---------------------------------------------------

Программа представляет собой системную иконку с меню для управления функциями программы.

**Файл логов**
-------------------

Программа записывает информацию о процессе с наибольшим потреблением CPU в файл `heaviest_process_log.txt`. Файл находится в текущей папке с программой.

**Код**
------

```markdown
import psutil
import time
import ctypes
import pystray
from PIL import Image, ImageDraw
import threading
import subprocess

def hide_console():
    """Скрывает консоль."""
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

FILE_PATH = 'heaviest_process_log.txt'

def create_image(width, height):
    """Создает изображение с круглой формой и прозрачным фоном."""
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((0, 0, width, height), fill=(0, 0, 255, 255))
    return image

def on_quit(icon, item):
    """Функция вызывается при клике на пункт «Выход»."""
    icon.stop()

def open_file(icon, item):
    """Открывает файл логов процесса с наибольшим потреблением CPU."""
    try:
        subprocess.Popen(['notepad.exe', FILE_PATH])  # Для Windows
        # Для Linux: subprocess.Popen(['xdg-open', FILE_PATH])
        # Для macOS: subprocess.Popen(['open', FILE_PATH])
    except Exception as e:
        print(f"Ошибка при открытии файла: {e}")

def clear_file(icon, item):
    """Очищает содержимое файла логов процесса с наибольшим потреблением CPU."""
    try:
        with open(FILE_PATH, 'w') as f:
            f.write('')
    except Exception as e:
        print(f"Ошибка при очистке файла: {e}")

def run_in_background():
    """Запускает цикл отслеживания процессов в фоновом режиме."""
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
    """Функция вызывается при запуске программы."""
    icon.visible = True

hide_console()

icon = pystray.Icon("test_icon", create_image(64, 64), "MHP_CPU", menu=pystray.Menu(
    pystray.MenuItem("Открыть файл", open_file),
    pystray.MenuItem("Очистить файл", clear_file),
    pystray.MenuItem("Выход", on_quit)
))

threading.Thread(target=run_in_background, daemon=True).start()

icon.run(setup)
```

**Лицензия**
----------------

Этот проект распространяется под лицензией MIT.
