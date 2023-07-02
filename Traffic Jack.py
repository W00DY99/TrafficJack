import os
import re
import sys
import ast
import csv
import time
import math
import json
import queue
import atexit
import shutil
import psutil
import ctypes
import base64
import socket
import hashlib
import zipfile
import tempfile
import requests
import platform
import win32api
import traceback
import pyperclip
import threading
import ipaddress
import webbrowser
import subprocess
import tldextract
import tkinter as tk
import urllib.request
from PIL import Image
import geoip2.database
from tkinter import ttk
from pathlib import Path
import prettytable as pt
import concurrent.futures
from fuzzywuzzy import fuzz
from subprocess import Popen
from datetime import datetime
from tkinter import Scrollbar
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from tkinter import filedialog
from urllib.parse import urljoin
from tkinter import colorchooser
import tkinter.messagebox as mbox
from prettytable import PrettyTable
import tkinter.simpledialog as simpledialog

global dev_mode
global version
dev_mode = True
version = '1.0.1'

# DEV

if dev_mode:
    hide_console = False
else:
    hide_console = True

# CLEAN UP

def perform_cleanup():
    # PORT SCAN KILL
    global port_scan_status
    if port_scan_status:
        try:
            port_on_close()
        except tk.TclError:
            pass
    # SHUTDOWN CAPTURE
    subprocess.call(f"taskkill /f /im CAPTURE.exe", creationflags=subprocess.CREATE_NO_WINDOW)
    # TRACERT KILL
    tracert_close_window()
    # DELETE _MEI FOLDERS
    temp_dir = os.environ.get('TEMP')
    if temp_dir:
        for root, dirs, files in os.walk(temp_dir):
            for dir_name in dirs:
                if dir_name.startswith('_MEI'):
                    dir_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(dir_path)
                    except:
                        pass

atexit.register(perform_cleanup)

if hide_console:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# OPEN CHECK

global uptime_file
uptime_file = os.path.join(tempfile.gettempdir(), 'uptime_trafficjack.txt')

def open_check():
    if not dev_mode:
        if os.path.exists(uptime_file):
            try:
                with open(uptime_file, 'r') as file:
                    file_contents = file.read()
                
                current_time = datetime.now().time()
                formatted_time = current_time.strftime("%H%M%S")
                time_diff = int(formatted_time) - int(file_contents)
                
                if not abs(time_diff) > 3:
                    icon_file_path = os.path.join(tempfile.gettempdir(), 'TrafficJack.ico')
                    if os.path.exists(icon_file_path):
                        root = tk.Tk()
                        root.withdraw()
                        root.iconbitmap(default=icon_file_path)
                    mbox.showinfo("Traffic Jack", "Traffic Jack is Already Running!")
                    os._exit(0)
            except:
                pass

open_check()

# CORE FILES

capture_code_file = os.path.join(tempfile.gettempdir(), 'CAPTURE.exe')
temp_country_path = os.path.join(tempfile.gettempdir(), 'GeoLite2-Country.mmdb')
temp_city_path = os.path.join(tempfile.gettempdir(), 'GeoLite2-City.mmdb')
temp_asn_path = os.path.join(tempfile.gettempdir(), 'GeoLite2-ASN.mmdb')
icon_file_path = os.path.join(tempfile.gettempdir(), 'TrafficJack.ico')
icon_png_file_path = os.path.join(tempfile.gettempdir(), 'TrafficJack.png')
npcap_exe = os.path.join(tempfile.gettempdir(), 'npcap-1.75.exe')

# DEL CHECKBOX VALUES
file_path = os.path.join(tempfile.gettempdir(), 'checkbox_values_trafficjack.txt')
if os.path.exists(file_path):
    os.remove(file_path)

# DEL ERROR LOG
if os.path.exists(error_file):
    os.remove(error_file)

# ICO & PNG LOGO

if not os.path.exists(icon_png_file_path):
    try:
        urllib.request.urlretrieve("https://trafficjack.org/PROGRAM/TrafficJack.png", icon_png_file_path)
    except Exception as e:
        mbox.showerror("Error", "Unable to Install!\nBad Download Links or No Internet!")
        root.destroy()
        os._exit(0)

# UPDATE

update_trafficjack = False
def get_first_line_from_url(version_url):
    try:
        response = urllib.request.urlopen(version_url)
        first_line = response.readline().decode('utf-8').strip()
        return first_line
    except Exception as e:
        mbox.showerror("Error", "No Internet!\nPlease Connect to the Internet and Try Again. ")
        os._exit(0)
version_url = "https://trafficjack.org/PROGRAM/version.txt"
global fetched_version
fetched_version = get_first_line_from_url(version_url)
if not (version == fetched_version):
    if os.path.exists(icon_file_path):
        boot = tk.Tk()
        boot.iconbitmap(default=icon_file_path)
        boot.destroy() 
    result = mbox.askquestion("Update", "There's a New Version of TrafficJack!\nWould You Like to Update?")
    if result == "yes":
        update_trafficjack = True

if update_trafficjack:
    webbrowser.open('https://trafficjack.org/download')

if update_trafficjack:
    os._exit(0)

# INSTALL

if not (os.path.exists(capture_code_file) and os.path.exists("C:\\Program Files\\Npcap\\CheckStatus.bat") and os.path.exists(temp_country_path) and os.path.exists(temp_city_path) and os.path.exists(temp_asn_path) and os.path.exists(icon_file_path)):
    
    unzip_install = False
    missing_files = []
    
    if not os.path.exists("C:\\Program Files\\Npcap\\CheckStatus.bat"):
        missing_files.append("https://trafficjack.org/PROGRAM/npcap-1.75.exe")
    if not os.path.exists(capture_code_file):
        missing_files.append("https://trafficjack.org/PROGRAM/CAPTURE.exe")
    if not os.path.exists(icon_file_path):
        missing_files.append("https://trafficjack.org/PROGRAM/TrafficJack.ico")
    if not os.path.exists(temp_country_path):
        missing_files.append("https://trafficjack.org/PROGRAM/GeoLite2-Country.mmdb")
    if not os.path.exists(temp_city_path):
        missing_files.append("https://trafficjack.org/PROGRAM/GeoLite2-City.mmdb")
    if not os.path.exists(temp_asn_path):
        missing_files.append("https://trafficjack.org/PROGRAM/GeoLite2-ASN.mmdb")

    total_files = len(missing_files)
    
    if total_files >= 5:
        missing_files = []
        unzip_install = True
        zip_file_path = os.path.join(tempfile.gettempdir(), 'Install.zip')
        if os.path.exists(zip_file_path):
            os.system(f"DEL {zip_file_path}")
        missing_files.append("https://trafficjack.org/PROGRAM/Install.zip")
        total_files = 1
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    def unzip_file(zip_file_path):
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                shutil.move(file_path, tempfile.gettempdir())
        shutil.rmtree(temp_dir)

    def download_file(url):
        global install_dwn_error
        filename = url.split("/")[-1]
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        installed_npcap = False
        try:
            request = urllib.request.Request(url, headers={'User-Agent': user_agent})
            urllib.request.urlretrieve(url, file_path)
        except (urllib.error.URLError, urllib.error.HTTPError):
            mbox.showerror("Error", "Unable to Install!\nBad Download Links or No Internet!")
            installer.destroy()
            sys.exit()
            quit()
        progress_bar["value"] += 1
        if progress_bar["value"] >= total_files:
            if unzip_install:
                zip_file_path = os.path.join(tempfile.gettempdir(), 'Install.zip')
                unzip_file(zip_file_path)
                os.system(f"DEL {zip_file_path}")
            if not os.path.exists("C:\\Program Files\\Npcap\\CheckStatus.bat"):
                status_label.config(text="Installing Npcap...")
                installer.update()
                npcap_exe = os.path.join(tempfile.gettempdir(), 'npcap-1.75.exe')
                subprocess.Popen(f'"{npcap_exe}"', shell=True)              
                while not os.path.exists("C:\\Program Files\\Npcap\\CheckStatus.bat"):
                    installed_npcap = True
                    time.sleep(1)
            if not installed_npcap:
                status_label.config(text="Update Complete")
            else:
                status_label.config(text="Installation Complete")
            installer.update()
            icon_file_path = os.path.join(tempfile.gettempdir(), 'TrafficJack.ico')
            installer.iconbitmap(default=icon_file_path)
            time.sleep(2)
            installer.destroy()
            quit()

    def start_download():
        threads = []
        for link in missing_files:
            thread = threading.Thread(target=download_file, args=(link,))
            threads.append(thread)
            thread.start()

    def on_installer_close():
        sys.exit()
        installer.quit()
        installer.destroy()
        quit()

    installer = tk.Tk()
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    if os.path.exists("C:\\Program Files\\Npcap\\CheckStatus.bat"):
        installer.title("Traffic Jack Update")
    else:
        installer.title("Traffic Jack Installer")
    screen_width = installer.winfo_screenwidth()
    screen_height = installer.winfo_screenheight()
    window_width = 300
    window_height = 270
    x = math.floor((screen_width - window_width) / 2)
    y = math.floor((screen_height - window_height) / 2)
    installer.geometry(f"{window_width}x{window_height}+{x}+{y}")
    installer.configure(bg="black")
    installer.overrideredirect(True)
    image_path = icon_png_file_path
    original_image = Image.open(image_path)
    resized_image = original_image.resize((170, 170))
    tk_image = ImageTk.PhotoImage(resized_image)
    image_label = tk.Label(installer, image=tk_image, bg="black", borderwidth=0, highlightthickness=0)
    image_label.pack(padx=10, pady=10) 
    if os.path.exists("C:\\Program Files\\Npcap\\CheckStatus.bat"):
        label_text = "Updating Traffic Jack..."
    else:
        label_text = "Installing Traffic Jack..."
    status_label = ttk.Label(installer, text=label_text, foreground="white", background="black", font=("Consolas", 14, "bold"))
    status_label.pack(pady=0)
    progress_bar = ttk.Progressbar(installer, length=260, mode="determinate")
    progress_bar.pack(pady=5)
    progress_bar["maximum"] = total_files
    installer.protocol("WM_DELETE_WINDOW", on_installer_close)
    start_download()
    progress_bar["value"] += 0.25
    installer.mainloop()

open_check()

# TRAFFIC JACK

update_interval = 500
s_filter = "NULL"
row_count = "Yes"
active_connections = ''
data_dict = {}
start_time = datetime.now().time()
start_time = start_time.strftime("%H%M%S")
welcome_message = False
table = PrettyTable()
table.field_names = ['IP ADDRESS', 'PORT', 'APPLICATION', 'PID', 'SENT', 'RECEIVED', 'CITY', 'COUNTRY', 'ASN', 'HOST', 'NIC', 'USER']
ignored_ips = ['0.0.0.0', '127.0.0.1', '::', '::1']
global root_font_size
global font_color
global font_color_2
global bg_color

root_button_width = 10
button_size = 13

# POSITIONS

stop_button_x = -345
clear_button_x = -235
static_button_x = -110
active_button_x = 0
local_button_x = 110
kill_button_x = 235
track_button_x = 345
settings_button_x = 322
save_button_x = 367
filter_frame_x = -39

stop_button_y = -88
clear_button_y = -88
active_button_y = -88
static_button_y = -88
track_button_y = -88
kill_button_y = -88
local_button_y = -88
settings_button_y = -48
save_button_y = -48
filter_frame_y = -42

# GUI

icon_file_path = os.path.join(tempfile.gettempdir(), 'TrafficJack.ico')

root = tk.Tk()
root.title(f"Traffic Jack")
root.configure(background='black')
root.iconbitmap(default=icon_file_path)

def on_root_close():
    root.destroy()
    perform_cleanup()

root.protocol("WM_DELETE_WINDOW", on_root_close)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

if screen_width < 1350:
    root.geometry(f"{screen_width}x620")
    window_width = screen_width
    root.minsize(screen_width, 300)
else:
    root.geometry('1350x620')
    window_width = 1350
    root.minsize(1000, 300)

root.resizable(True, True)
window_height = 620
x = math.floor((screen_width - window_width) / 2)
y = math.floor((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
frame = tk.Frame(root)
frame.pack(fill='both', expand=True, padx=0, pady=0)
frame.pack_propagate(0)

scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_y.config(highlightbackground='black', troughcolor='black')

scrollbar_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
scrollbar_x.config(highlightbackground='black', troughcolor='black')

def copy_table():
    try:
        selected_text = table_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
        pyperclip.copy(selected_text)
    except tk.TclError:
        pass
    table_widget.tag_remove(tk.SEL, "1.0", tk.END) # UNSELECT TEXT

def paste_text(event):
    clipboard = root.clipboard_get()
    event.widget.insert(tk.INSERT, clipboard)

# RIGHT CLICK MENU

def ttb(option):
    global port_dict
    global enable_local_status

    ttb_safe = False
    selected_text = table_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
    selected_text = selected_text.strip()
    table_widget.tag_remove(tk.SEL, "1.0", tk.END) # UNSELECT TEXT
        
    def ttb_is_valid_ip(selected_text):
        try:
            ipaddress.ip_address(selected_text)
            return True
        except ValueError:
            return False

    def ttb_is_valid_domain(selected_text):
        pattern = r"^(?!-)(?:[A-Za-z0-9-]{0,62}[A-Za-z0-9]\.)+[A-Za-z]{2,}$"
        return re.match(pattern, selected_text)

    def ttb_is_valid_app(selected_text):
        pattern = r'^[\w.-]+(?:\.exe|\.py|\.jar|\.dmg|\.txt)$'
        return re.match(pattern, selected_text)

    # IP
    if ttb_is_valid_ip(selected_text):
        if not enable_local_status:
            if option == 'Track' or option == 'Trace':
                mbox.showerror("Error", f"Cannot {option} IP Address in Local Mode!")
                return
        #print("IP")
        if option == 'Track':
            retrieve_ip_info(selected_text)
        if option == 'Trace':
            tracert(selected_text)
        if option == 'Block':
            kill_by_ip(selected_text)
        ttb_safe = True
        return

    # APPLICATION
    elif ttb_is_valid_app(selected_text):
        #print("APP")
        if option == 'Track':
            retrieve_app_info(selected_text)
        if option == 'Trace':
            mbox.showerror("Error", f"Cannot {option} Application")
        if option == 'Block':
            kill_by_app(selected_text)
        ttb_safe = True
        return
    
    # HOST
    elif ttb_is_valid_domain(selected_text):
        #print("HOST")
        if option == 'Track':
            retrieve_domain_info(selected_text)
        if option == 'Trace':
            tracert(selected_text)
        if option == 'Block':
            kill_by_host(selected_text)
        ttb_safe = True
        return

    # PID
    try:
        if not int(selected_text) in port_dict:
            #print("PID")
            if option == 'Track':
                retrieve_app_info(selected_text)
            if option == 'Trace':
                mbox.showerror("Error", f"Cannot {option} PID")
            if option == 'Block':
                kill_by_pid(selected_text)
            ttb_safe = True
            return
    except ValueError:
        ttb_safe = False

    # PORT
    try:
        int(selected_text) < 65535
    except ValueError:
        ttb_safe = False
    else:
        #print("PORT")
        if option == 'Track':
            mbox.showerror("Error", f"Cannot {option} Port")
        if option == 'Trace':
            mbox.showerror("Error", f"Cannot {option} Port")
        if option == 'Block':
            kill_by_port(selected_text)
        ttb_safe = True
        return

    if not ttb_safe:
        mbox.showerror("Error", f"Cannot {option} \n{selected_text}")

# TABLE WIDGET

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
bg_color = "black"
font_color = "#a5ee80"
font_color_2 = "#00ff0d"
font_size = int(min(screen_width, screen_height) / 105)
root_font_size = font_size
table_widget = tk.Text(frame, fg=font_color, bg=bg_color, font=('Consolas', root_font_size, 'bold'), exportselection=1, wrap=tk.NONE)
table_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 0), padx=(15, 0))

# RIGHT CLICK MENU

table_menu = tk.Menu(table_widget, tearoff=0)
table_menu.add_command(label='Copy', command=copy_table)
table_menu.add_command(label='Track', command=lambda: ttb('Track'))
table_menu.add_command(label='Trace', command=lambda: ttb('Trace'))
table_menu.add_command(label='Block', command=lambda: ttb('Block'))

def show_table_menu(event):
    table_menu.post(event.x_root, event.y_root)

table_widget.bind('<Button-3>', show_table_menu)

# STOP SCRIPT IF USER SELECTS TEXT IN TABLE

def selection_start_callback(value):
    try:
        selected_text = table_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        table_widget.tag_remove(tk.SEL, "1.0", tk.END) # UNSELECT TEXT
        return
    if not stop_button.cget("text") == "START":
        stop_button.invoke()
    pass
    
table_widget.bind("<<Selection>>", selection_start_callback)

# STOP SCRIPT IF USER SCROLLS

def scroll_start_callback(event):
    global row_count
    if row_count >= 15:
        if not stop_button.cget("text") == "START":
            stop_button.invoke()
    pass

table_widget.bind("<MouseWheel>", scroll_start_callback)

# SCROLLBAR

scrollbar_y.config(command=table_widget.yview)
table_widget.config(yscrollcommand=scrollbar_y.set)

scrollbar_x.config(command=table_widget.xview)
table_widget.config(xscrollcommand=scrollbar_x.set)

root.focus_force()

# BUTTON BAR

global black_bar_color
black_bar_color = '#0d0d0d'

black_bar = tk.Canvas(root, bg='#F0F0F0', height=135, highlightthickness=0)
black_bar.pack(side=tk.BOTTOM, fill=tk.X, anchor='s')

thickness = 15.7
connected_lines = black_bar.create_polygon(
    0, 0, thickness, 0, thickness, black_bar.winfo_height() - thickness, black_bar.winfo_width() - thickness, black_bar.winfo_height() - thickness,
    black_bar.winfo_width() - thickness, 0, fill=black_bar_color)
bottom_line = black_bar.create_line(
    thickness, black_bar.winfo_height() - thickness, black_bar.winfo_width() - thickness, black_bar.winfo_height() - thickness, fill='#F0F0F0', width=1)

def update_black_bar_position(event):
    height = black_bar.winfo_height()
    width = black_bar.winfo_width()

    black_bar.coords(
        connected_lines,
        0, 0, thickness, 0, thickness, height - thickness, width - thickness, height - thickness,
        width - thickness, 0
    )
    black_bar.coords(
        bottom_line,
        thickness, height - thickness, width - thickness, height - thickness
    )
    black_bar.pack_configure(side=tk.BOTTOM, fill=tk.X, anchor='s')

root.bind('<Configure>', update_black_bar_position)

# FOOTER

def open_link(link):
    webbrowser.open(link)
version_frame = tk.Frame(root, bg=black_bar_color)
version_frame.place(relx=0.50, rely=1, anchor=tk.S, y=-21) # POSITION
hyperlink_frame = tk.Frame(version_frame, bg=black_bar_color)
hyperlink_frame.pack(side="right")
help_hyperlink_label = tk.Label(hyperlink_frame, text="HELP", bg=black_bar_color, fg="yellow", cursor="hand2")
help_hyperlink_label.pack(side="left")
help_hyperlink_label.bind("<Button-1>", lambda event: open_link("http://trafficjack.org/help"))
help_hyperlink_label.config(font=("Consolas", 9, 'bold'))
help_hyperlink_label.bind("<Enter>", lambda event: help_hyperlink_label.config(fg="#00ff0d"))
help_hyperlink_label.bind("<Leave>", lambda event: help_hyperlink_label.config(fg="yellow"))
spacer_label = tk.Label(hyperlink_frame, text="|", bg=black_bar_color, fg='white', font=("Consolas", 9, 'bold'))
spacer_label.pack(side="left")
hyperlink_label = tk.Label(hyperlink_frame, text="Buy Me a Coffee \u2665", bg=black_bar_color, fg="#f24c2e", cursor="hand2")
hyperlink_label.pack(side="left")
hyperlink_label.bind("<Button-1>", lambda event: open_link("http://trafficjack.org/donate"))
hyperlink_label.config(font=("Consolas", 9, 'bold'))
hyperlink_label.bind("<Enter>", lambda event: hyperlink_label.config(fg="#00ff0d"))
hyperlink_label.bind("<Leave>", lambda event: hyperlink_label.config(fg="#f24c2e"))
trafficjack_label = tk.Label(version_frame, text=f"Traffic Jack {version}", bg=black_bar_color, fg='#00ff0d', font=("Consolas", 9, 'bold'))
trafficjack_label2 = tk.Label(version_frame, text=f"| By: W00DY |", bg=black_bar_color, fg='white', font=("Consolas", 9, 'bold'))
trafficjack_label.pack(side="left")
trafficjack_label2.pack(side="left")

table_stop = True

# HOTKEYS

def handle_key_event(event):
    root.after(100, process_key_event, event)

def process_key_event(event):
    toggle_update_pressed(event)
    clear_button_pressed(event)
    remove_button_pressed(event)
    local_button_pressed(event)
    page_up_button_pressed(event)
    page_down_button_pressed(event)
    active_button_pressed(event)
    static_button_pressed(event)
    toggle_fullscreen(event)

def toggle_update_pressed(event):
    if event.char == " " and not isinstance(event.widget, tk.Entry):
        stop_button.invoke()

def clear_button_pressed(event):
    if event.keysym == "Delete" and not isinstance(event.widget, tk.Entry):
        if not stop_button.cget("text") == "START":
            stop_button.invoke()
        clear_button.invoke()

def remove_button_pressed(event):
    if event.keysym == "backslash" and not isinstance(event.widget, tk.Entry):       
        if not filter_entry.focus_set():
            remove_button.invoke()
        else:
            filter_entry.focus_set()

def local_button_pressed(event):
    if event.keysym == "End" and not isinstance(event.widget, tk.Entry):
        local_button.invoke()

def page_up_button_pressed(event):
    if event.keysym == "Prior" and not isinstance(event.widget, tk.Entry):
        global root_font_size
        root_font_size += 1
        table_widget.configure(font=('Consolas', root_font_size, 'bold'))

def page_down_button_pressed(event):
    if event.keysym == "Next" and not isinstance(event.widget, tk.Entry):
        global root_font_size
        if root_font_size > 1:
            root_font_size -= 1
            table_widget.configure(font=('Consolas', root_font_size, 'bold'))

def active_button_pressed(event):
    if event.keysym == "Home" and not isinstance(event.widget, tk.Entry):
        active_button.invoke()

def static_button_pressed(event):
    if event.keysym == "Insert" and not isinstance(event.widget, tk.Entry):
        static_button.invoke()

def toggle_fullscreen(event):
    if event.keysym == "F11" and not isinstance(event.widget, tk.Entry):
        if root.attributes('-fullscreen'):
            root.attributes('-fullscreen', False)
        else:
            root.attributes('-fullscreen', True)

root.bind("<Key>", handle_key_event)

def toggle_update():
    global table_stop
    if stop_button.cget("text") == "START":
        table_stop = False
        stop_button.config(text="STOP", bg="#f24c2e", fg="white", state="normal")
        clear_button.config(state="disabled", bg="#bfbfbf", cursor="X_cursor")
        update_table()
    else:
        table_stop = True
        stop_button.config(text="START", bg="yellow", fg="black", state="normal")
        clear_button.config(state="normal", bg="#f24c2e", fg="white", cursor="hand2")

stop_button = tk.Button(root, text="START", command=toggle_update, bg="yellow", fg="black", width=root_button_width, font=("Consolas", button_size, "bold"), cursor="hand2")
stop_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=stop_button_x, y=stop_button_y)

def active_filter():
    if not stop_button["text"] == "START":
        stop_button.invoke()
    if active_button.cget("text") == "ALL":
        global active_connections
        active_connections = True
        active_button.config(text="ACTIVE", bg="#f24c2e", fg="white")
        if stop_button["text"] == "START":
            stop_button.invoke()
    else:
        active_connections = False
        active_button.config(text="ALL", bg="green", fg="white")
        active_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=active_button_x, y=active_button_y)
        if stop_button["text"] == "START":
            stop_button.invoke()

active_button = tk.Button(root, text="ALL", command=active_filter, bg="green", fg="white", width=root_button_width, font=("Consolas", button_size, "bold"), cursor="hand2")
active_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=active_button_x, y=active_button_y)

def slash_n_count():
    global slash_n
    if slash_n_mod:
        slash_n = "\n" * (27 - min(20, 23))
    else:
        slash_n = "\n" * (27 - min(root_font_size, 23))
    return slash_n

def clear_table():
    table_widget.configure(font=('Consolas', 20, 'bold'))
    global slash_n_mod
    global start_time
    start_time = datetime.now().time()
    start_time = start_time.strftime("%H%M%S")
    slash_n_mod = True
    table_widget.config(state=tk.NORMAL)
    table.clear_rows()
    data_dict.clear()
    reset_file = os.path.join(tempfile.gettempdir(), 'reset_trafficjack.txt')
    with open(reset_file, 'w') as file:
        file.write("")
    ip_addresses_csv = os.path.join(tempfile.gettempdir(), 'ip_addresses.csv')
    active_ip_addresses_csv = os.path.join(tempfile.gettempdir(), 'active_ip_addresses.csv')
    with open(ip_addresses_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["127.0.0.1"])
    with open(active_ip_addresses_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["127.0.0.1"])
    data_usage_csv = os.path.join(tempfile.gettempdir(), 'data_usage.csv')
    with open(data_usage_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([])
    table_widget.delete('1.0', tk.END)
    table_widget.tag_configure('center', justify='center')
    slash_n_count()
    table_widget.insert(tk.END, f"{slash_n} # CONNECTIONS CLEARED # ", 'center')
    table_widget.insert(tk.END, "\n\n\n\n\n")
    table_widget.config(state=tk.DISABLED)
    stop_button.config(text="START", bg="yellow", fg="black")
    clear_button.config(bg="#f24c2e", fg="white", state="normal")

clear_button = tk.Button(root, text="CLEAR", command=clear_table, bg="#f24c2e", fg="white", width=root_button_width, font=("Consolas", button_size, "bold"), cursor="hand2")
clear_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=clear_button_x, y=clear_button_y)

enable_local_status = True

def enable_local():
    if not stop_button["text"] == "START":
        stop_button.invoke()
    global enable_local_status, total_received_bytes, total_sent_bytes, column_window
    global ip_column, application_column, pid_column, sent_column, received_column, city_column, country_column, asn_column, host_column, interface_column, user_column
    global city_column_s, country_column_s, asn_column_s, host_column_s
    if enable_local_status == False:
        enable_local_status = True
        total_received_bytes = 0
        total_sent_bytes = 0
        if city_column_s:
            add_column('CITY')
            city_column = True
        if country_column_s:
            add_column('COUNTRY')
            country_column = True
        if asn_column_s:
            add_column('ASN')
            asn_column = True
        if host_column_s:
            add_column('HOST')
            host_column = True
        checkbox_file = os.path.join(tempfile.gettempdir(), 'checkbox_values_trafficjack.txt')
        checkbox_values = {
            "IP ADDRESS": ip_column,
            "PORT": port_column,
            "APPLICATION": application_column,
            "PID": pid_column,
            "SENT": sent_column,
            "RECEIVED": received_column,
            "CITY": city_column,
            "COUNTRY": country_column,
            "ASN": asn_column,
            "HOST": host_column,
            "NIC": interface_column,
            "USER": user_column
        }
        with open(checkbox_file, "w") as file:
            for word, value in checkbox_values.items():
                file.write(f"{word}:{int(value)}\n")
        local_button.config(text="PUBLIC", bg="green", fg="white")
    else:
        enable_local_status = False
        total_received_bytes = 0
        total_sent_bytes = 0
        
        if not ip_column:
            if not port_column:
                if not application_column:
                    if not pid_column:
                        if not sent_column:
                            if not received_column:
                                if not interface_column:
                                    if not user_column:
                                        ip_column = True
        
        checkbox_file = os.path.join(tempfile.gettempdir(), 'checkbox_values_trafficjack.txt')
        checkbox_values = {
            "IP ADDRESS": ip_column,
            "PORT": port_column,
            "APPLICATION": application_column,
            "PID": pid_column,
            "SENT": sent_column,
            "RECEIVED": received_column,
            "CITY": city_column,
            "COUNTRY": country_column,
            "ASN": asn_column,
            "HOST": host_column,
            "NIC": interface_column,
            "USER": user_column
        }

        with open(checkbox_file, "w") as file:
            for word, value in checkbox_values.items():
                file.write(f"{word}:{int(value)}\n")
        
        if not city_column:
            city_column_s = False
        else:
            city_column_s = True  
        if not country_column:
            country_column_s = False
        else:
            country_column_s = True
        if not asn_column:
            asn_column_s = False
        else:
            asn_column_s = True
        if not host_column:
            host_column_s = False
        else:
            host_column_s = True
        remove_column('CITY')
        city_column = False
        remove_column('COUNTRY')
        country_column = False
        remove_column('ASN')
        asn_column = False
        remove_column('HOST')
        host_column = False
        local_button.config(text="LOCAL", bg="#f24c2e", fg="white")
    if column_window is not None and column_window.winfo_exists():
        column_window.destroy()
    if stop_button["text"] == "START":
        stop_button.invoke()
    return enable_local_status
    return total_received_bytes
    return total_sent_bytes

local_button = tk.Button(root, text="PUBLIC", command=enable_local, bg="green", fg="white", width=root_button_width, font=("Consolas", button_size, "bold"), cursor="hand2")
local_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=local_button_x, y=local_button_y)

static_mode = False

def enable_static():
    global static_mode
    if not static_mode:
        static_mode = True
        data_dict.clear()
        static_button.config(text="STATIC", bg="#f24c2e", fg="white")
        if stop_button["text"] == "START":
            stop_button.invoke()
    else:
        static_mode = False
        data_dict.clear()
        static_button.config(text="DYNAMIC", bg="green", fg="white")
        if stop_button["text"] == "START":
            stop_button.invoke()
    return static_mode

static_button = tk.Button(root, text="DYNAMIC", command=enable_static, bg="green", fg="white", width=root_button_width, font=("Consolas", button_size, "bold"), cursor="hand2")
static_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=static_button_x, y=static_button_y)

track_button = tk.Button(root, text="TRACK", command=lambda: create_track_window(root), bg="blue", fg="white", width=root_button_width, font=("Consolas", button_size, "bold"), cursor="hand2")
track_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=track_button_x, y=track_button_y)

# TRACERT

global trace_window
global trace_status
trace_status = False
track_window = None
trace_window = None

def tracert_close_window():
    global trace_window
    global process
    global tracert_thread
    global trace_status
    trace_status = False
    if trace_window is None:
        return
    pid = process.pid
    kill_cmd = f"TASKKILL /F /PID {pid} /T"
    subprocess.Popen(kill_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
    tracert_thread.join()
    try:
        trace_window.destroy()
    except:
        pass

def copy_selected_text(text):
    selected_text = text.get(tk.SEL_FIRST, tk.SEL_LAST)
    pyperclip.copy(selected_text)

def tracert(trace_target):
    global trace_status
    global trace_window
    global process
    global tracert_thread

    if trace_status:
        mbox.showerror("Error", f"Trace Scan Already in Progress!")
        trace_window.lift()
        trace_window.focus_force()
        return

    if trace_window is not None and trace_window.winfo_exists():
        tracert_close_window()

    def run_tracert(ip):
        global trace_window
        global process
        global tracert_thread
        global trace_status
        cmd = f"tracert {ip}"
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        line_count = 0

        def update_output():
            nonlocal line_count
            while True:
                output = process.stdout.readline().decode('utf-8')
                if output:
                    line_count += 1
                    if line_count > 3:
                        output_queue.put((output, line_count))
                else:
                    break

        tracert_thread = threading.Thread(target=update_output)
        tracert_thread.start()
        trace_status = True
        
        def process_queue():
            global trace_status
            try:
                while True:
                    output, count = output_queue.get(block=False)
                    tag = "gray" if count % 2 == 0 else "green"
                    lines = output.split("\n")
                    non_empty_lines = [line for line in lines if line.strip()]
                    output = "\n".join(non_empty_lines)
                    text.config(state=tk.NORMAL)
                    for line in non_empty_lines:
                        if "Trace complete." in line.rstrip():
                            line = '\n  # Trace COMPLETE #'
                            trace_status = False
                            tag = 'gray'
                        text.insert(tk.END, line.rstrip(), (tag,))
                        text.insert(tk.END, "\n")
                    text.config(state=tk.DISABLED)
                    text.see(tk.END)
                    output_queue.task_done()
            except queue.Empty:
                trace_window.after(10, process_queue)

        output_queue = queue.Queue()
        trace_window.after(10, process_queue)

        trace_window.protocol("WM_DELETE_WINDOW", tracert_close_window)

    def check_ping(trace_target):
        command = ['ping', '-n', '1', trace_target]
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except subprocess.CalledProcessError:
            return False

    if not check_ping(trace_target):
        mbox.showerror("Error", f"{trace_target} is Offline or Not Responding!")
        return

    trace_window = tk.Toplevel(root)
    trace_window.title(f"TRACE - {trace_target}")
    trace_window.geometry("800x300")
    trace_window.configure(bg="#0d0d0d")
    text = tk.Text(trace_window, bg="#0d0d0d", fg="white", font=("Consolas", 12, 'bold'), highlightthickness=1)
    text.pack(fill='both', expand=True)

    # Create the Scrollbar
    scrollbar = tk.Scrollbar(text, command=text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the Text widget to use the Scrollbar
    text.configure(yscrollcommand=scrollbar.set)

    # Adjust the Scrollbar when the Text widget is scrolled
    text.bind("<Configure>", lambda e: text.yview_moveto(1))

    parent_width = root.winfo_width()
    parent_height = root.winfo_height()
    x = root.winfo_rootx() + (parent_width // 2) - (820 // 2)
    y = root.winfo_rooty() + (parent_height // 2) - (490  // 2)
    trace_window.geometry("+{}+{}".format(x, y))

    text.tag_configure("gray", foreground="#00ff0d")
    text.tag_configure("green", foreground="#a5ee80")
    run_tracert(trace_target)

    text.bind("<Button-3>", lambda event: show_copy_button(event, text))
    
    text.config(state=tk.NORMAL)
    tracert_message = f'\n  # Tracing {trace_target} #\n\n'
    text.insert(tk.END, tracert_message, ('gray',))
    text.config(state=tk.DISABLED)
    
    trace_window.mainloop()

def show_copy_button(event, text):
    menu = tk.Menu(trace_window, tearoff=0)
    menu.add_command(label="Copy", command=lambda: copy_selected_text(text))
    menu.post(event.x_root, event.y_root)

def go_back_track():
    global track_window
    track_window.destroy()
    create_track_window(root)

def create_track_window(parent):
    global track_window
    
    if stop_button.cget("text") == "STOP":
        stop_button.invoke()
        global table_stop
        table_stop = True
    
    if track_window is not None and track_window.winfo_exists():
        track_window.lift()
        track_window.focus_force()
        return

    def create_ip_window():
        ip_button.destroy()
        track_label.destroy()
        domain_button.destroy()
        app_button.destroy()
        pid_button.destroy()

        label = tk.Label(track_window, text="Enter IP Address", bg="#0d0d0d", fg="white", font=("Consolas", 12, "bold"))
        label.place(relx=0.5, rely=0.28, anchor=tk.CENTER)

        global ip_address_track
        ip_address_track = tk.StringVar(track_window)

        def invalid_ip():
            submit_button.place_forget()
            trace_button.place_forget()
            go_back_button.place_forget()
            invalid_ip_label = tk.Label(track_window, bg="#0d0d0d", fg="#f24c2e", font=("Consolas", 9, "bold"), anchor=tk.CENTER)
            invalid_ip_label.place(relx=0.5, rely=0.50, anchor=tk.CENTER)
            invalid_ip_label.configure(text="Invalid IP address")
            submit_button_2 = tk.Button(track_window, text="TRACK", command=submit_ip, bg="blue", fg="white", width=7, font=("Consolas", 12, "bold"), cursor="hand2")
            submit_button_2.place(relx=0.38, rely=0.61, anchor=tk.CENTER)
            trace_button_2 = tk.Button(track_window, text="TRACE", command=trace_ip, bg="yellow", fg="black", width=7, font=("Consolas", 12, "bold"), cursor="hand2")
            trace_button_2.place(relx=0.62, rely=0.61, anchor=tk.CENTER)
            go_back_button_2 = tk.Button(track_window, text="GO BACK", command=go_back_track, bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
            go_back_button_2.place(relx=0.5, rely=0.762, anchor=tk.CENTER)

        def is_valid_ip(ip):
            try:
                ipaddress.ip_address(ip)
                return True
            except ValueError:
                return False

        def trace_ip():
            ip = ip_address_track.get()
            ip = ip.replace(" ", "")
            if is_valid_ip(ip):
                if trace_window is not None and trace_window.winfo_exists():
                    tracert_close_window()
                track_window.destroy()
                tracert(ip)
            else:
                invalid_ip()
            
        def submit_ip():
            ip = ip_address_track.get()
            ip = ip.replace(" ", "")
            if not ip:
                return
            if is_valid_ip(ip):
                retrieve_ip_info(ip)
                track_window.destroy()
            else:
                invalid_ip()

        text_box = tk.Entry(track_window, font=("Consolas", 12, "bold"), textvariable=ip_address_track)
        text_box.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        text_box.bind("<Button-3>", paste_text)
        text_box.focus()
        text_box.bind("<Return>", lambda event: submit_ip())
        submit_button = tk.Button(track_window, text="TRACK", command=submit_ip, bg="blue", fg="white", width=7, font=("Consolas", 12, "bold"), cursor="hand2")
        submit_button.place(relx=0.38, rely=0.56, anchor=tk.CENTER)
        
        trace_button = tk.Button(track_window, text="TRACE", command=trace_ip, bg="yellow", fg="black", width=7, font=("Consolas", 12, "bold"), cursor="hand2")
        trace_button.place(relx=0.62, rely=0.56, anchor=tk.CENTER)
        
        go_back_button = tk.Button(track_window, text="GO BACK", command=go_back_track, bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        go_back_button.place(relx=0.5, rely=0.712, anchor=tk.CENTER)

    def create_domain_window():
        ip_button.destroy()
        track_label.destroy()
        domain_button.destroy()
        app_button.destroy()
        pid_button.destroy()

        label = tk.Label(track_window, text="Enter Host", bg="#0d0d0d", fg="white", font=("Consolas", 12, "bold"))
        label.place(relx=0.5, rely=0.28, anchor=tk.CENTER)

        global domain_track
        domain_track = tk.StringVar(track_window)

        def invalid_host():
            submit_button.place_forget()
            trace_button.place_forget()
            go_back_button.place_forget()
            invalid_domain_label = tk.Label(track_window, bg="#0d0d0d", fg="#f24c2e", font=("Consolas", 9, "bold"), anchor=tk.CENTER)
            invalid_domain_label.place(relx=0.5, rely=0.50, anchor=tk.CENTER)
            invalid_domain_label.configure(text="Invalid Host")
            submit_button_2 = tk.Button(track_window, text="TRACK", command=submit_domain, bg="blue", fg="white", width=7, font=("Consolas", 12, "bold"), cursor="hand2")
            submit_button_2.place(relx=0.38, rely=0.61, anchor=tk.CENTER)
            trace_button_2 = tk.Button(track_window, text="TRACE", command=trace_host, bg="yellow", fg="black", width=7, font=("Consolas", 12, "bold"), cursor="hand2")
            trace_button_2.place(relx=0.62, rely=0.61, anchor=tk.CENTER)
            go_back_button_2 = tk.Button(track_window, text="GO BACK", command=go_back_track, bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
            go_back_button_2.place(relx=0.5, rely=0.762, anchor=tk.CENTER)

        def is_valid_domain(domain):
            pattern = r"^(?!-)(?:[A-Za-z0-9-]{0,62}[A-Za-z0-9]\.)+[A-Za-z]{2,}$"
            return re.match(pattern, domain)

        def trace_host():
            domain = domain_track.get()
            domain = domain.strip()
            if is_valid_domain(domain):
                if trace_window is not None and trace_window.winfo_exists():
                    tracert_close_window()
                track_window.destroy()
                tracert(domain)
            else:
                invalid_host()

        def submit_domain():
            global domain
            domain = domain_track.get()
            domain = domain.strip()
            if not domain:
                return
            if is_valid_domain(domain):
                track_window.destroy()
                retrieve_domain_info(domain)
            else:
                invalid_host()

        text_box = tk.Entry(track_window, font=("Consolas", 12, "bold"), textvariable=domain_track)
        text_box.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        text_box.bind("<Button-3>", paste_text)
        text_box.focus()
        text_box.bind("<Return>", lambda event: submit_domain())
        submit_button = tk.Button(track_window, text="TRACK", command=submit_domain, bg="blue", fg="white", width=7, font=("Consolas", 12, "bold"), cursor="hand2")
        submit_button.place(relx=0.38, rely=0.56, anchor=tk.CENTER)
        trace_button = tk.Button(track_window, text="TRACE", command=trace_host, bg="yellow", fg="black", width=7, font=("Consolas", 12, "bold"), cursor="hand2")
        trace_button.place(relx=0.62, rely=0.56, anchor=tk.CENTER)
        go_back_button = tk.Button(track_window, text="GO BACK", command=go_back_track, bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        go_back_button.place(relx=0.5, rely=0.712, anchor=tk.CENTER)

    def create_application_window():
        ip_button.destroy()
        track_label.destroy()
        domain_button.destroy()
        app_button.destroy()
        pid_button.destroy()

        label = tk.Label(track_window, text="Enter Application", bg="#0d0d0d", fg="white", font=("Consolas", 12, "bold"))
        label.place(relx=0.5, rely=0.28, anchor=tk.CENTER)

        global app_track
        app_track = tk.StringVar(track_window)

        def invalid_app():
            submit_button.place_forget()
            go_back_button.place_forget()
            invalid_app_label = tk.Label(track_window, bg="#0d0d0d", fg="#f24c2e", font=("Consolas", 9, "bold"), anchor=tk.CENTER)
            invalid_app_label.place(relx=0.5, rely=0.50, anchor=tk.CENTER)
            invalid_app_label.configure(text="Invalid Application")
            submit_button_2 = tk.Button(track_window, text="TRACK", command=submit_app, bg="blue", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
            submit_button_2.place(relx=0.50, rely=0.61, anchor=tk.CENTER)
            go_back_button_2 = tk.Button(track_window, text="GO BACK", command=go_back_track, bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
            go_back_button_2.place(relx=0.5, rely=0.762, anchor=tk.CENTER)

        def is_valid_app(app):
            pattern = r'^[\w.-]+(?:\.exe|\.py|\.jar|\.dmg|\.txt)$'
            return re.match(pattern, app)

        def submit_app():
            global domain
            app = app_track.get()
            app = app.strip()
            if not app:
                return
            if is_valid_app(app):
                track_window.destroy()
                retrieve_app_info(app)
            else:
                invalid_app()

        text_box = tk.Entry(track_window, font=("Consolas", 12, "bold"), textvariable=app_track)
        text_box.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        text_box.bind("<Button-3>", paste_text)
        text_box.focus()
        text_box.bind("<Return>", lambda event: submit_app())
        submit_button = tk.Button(track_window, text="TRACK", command=submit_app, bg="blue", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        submit_button.place(relx=0.50, rely=0.56, anchor=tk.CENTER)
        go_back_button = tk.Button(track_window, text="GO BACK", command=go_back_track, bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        go_back_button.place(relx=0.5, rely=0.712, anchor=tk.CENTER)

    def create_pid_window():
        ip_button.destroy()
        track_label.destroy()
        domain_button.destroy()
        app_button.destroy()
        pid_button.destroy()

        label = tk.Label(track_window, text="Enter PID", bg="#0d0d0d", fg="white", font=("Consolas", 12, "bold"))
        label.place(relx=0.5, rely=0.28, anchor=tk.CENTER)

        global pid_track
        pid_track = tk.StringVar(track_window)

        def invalid_pid():
            submit_button.place_forget()
            go_back_button.place_forget()
            invalid_pid_label = tk.Label(track_window, bg="#0d0d0d", fg="#f24c2e", font=("Consolas", 9, "bold"), anchor=tk.CENTER)
            invalid_pid_label.place(relx=0.5, rely=0.50, anchor=tk.CENTER)
            invalid_pid_label.configure(text="Invalid PID")
            submit_button_2 = tk.Button(track_window, text="TRACK", command=submit_app, bg="blue", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
            submit_button_2.place(relx=0.50, rely=0.61, anchor=tk.CENTER)
            go_back_button_2 = tk.Button(track_window, text="GO BACK", command=go_back_track, bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
            go_back_button_2.place(relx=0.5, rely=0.762, anchor=tk.CENTER)

        def is_valid_pid(pid):
            pattern = r'^\d+$'
            return re.match(pattern, pid)

        def submit_app():
            global domain
            pid = pid_track.get()
            pid = pid.strip()
            if not pid:
                return
            if is_valid_pid(pid):
                track_window.destroy()
                retrieve_app_info(pid)
            else:
                invalid_pid()

        text_box = tk.Entry(track_window, font=("Consolas", 12, "bold"), textvariable=pid_track)
        text_box.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        text_box.bind("<Button-3>", paste_text)
        text_box.focus()
        text_box.bind("<Return>", lambda event: submit_app())
        submit_button = tk.Button(track_window, text="TRACK", command=submit_app, bg="blue", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        submit_button.place(relx=0.50, rely=0.56, anchor=tk.CENTER)
        go_back_button = tk.Button(track_window, text="GO BACK", command=go_back_track, bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        go_back_button.place(relx=0.5, rely=0.712, anchor=tk.CENTER)

    track_window = tk.Toplevel(parent)
    track_window.geometry("300x250")
    track_window.title("TRACK")
    track_window.configure(bg="#0d0d0d")
    track_window.attributes('-alpha', 1)
    track_window.maxsize(300, 250)
    track_window.minsize(300, 250)

    # WHITE BORDER
    canvas = tk.Canvas(track_window, bg="#0d0d0d", width=300, height=250)
    canvas.pack()
    canvas.create_rectangle(1, 1, 300, 300, outline="white", width=1)

    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    x = parent.winfo_rootx() + (parent_width // 2) - (325 // 2)
    y = parent.winfo_rooty() + (parent_height // 2) - (420 // 2)
    track_window.geometry("+{}+{}".format(x, y))

    global track_label
    track_label = tk.Label(track_window, text="《 TRACK 》", bg="#0d0d0d", fg="yellow", font=("Consolas", 15, "bold"))
    track_label.place(relx=0.5, rely=0.14, anchor=tk.CENTER)

    ip_button = tk.Button(track_window, text="IP ADDRESS", command=create_ip_window, bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), cursor="hand2")
    ip_button.place(relx=0.5, rely=0.33, anchor=tk.CENTER)

    domain_button = tk.Button(track_window, text="HOST", command=create_domain_window, bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), cursor="hand2")
    domain_button.place(relx=0.5, rely=0.50, anchor=tk.CENTER)

    app_button = tk.Button(track_window, text="APPLICATION", command=create_application_window, bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), cursor="hand2")
    app_button.place(relx=0.5, rely=0.67, anchor=tk.CENTER)

    pid_button = tk.Button(track_window, text="PID", command=create_pid_window, bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), cursor="hand2")
    pid_button.place(relx=0.5, rely=0.84, anchor=tk.CENTER)

    # DISABLE IP & HOST BUTTONS IF LOCAL MODE
    
    if not enable_local_status:
        ip_button.config(state="disabled", bg="#bfbfbf", cursor="X_cursor")
        domain_button.config(state="disabled", bg="#bfbfbf", cursor="X_cursor")
    else:
        ip_button.config(state="normal", bg="blue", fg="white", cursor="hand2")
        domain_button.config(state="normal", bg="blue", fg="white", cursor="hand2")

# RETRIEVE HOST INFO

def retrieve_domain_info(domain):
    
    def is_valid_domain(domain):
        pattern = r"^(?!-)(?:[A-Za-z0-9-]{0,62}[A-Za-z0-9]\.)+[A-Za-z]{2,}$"
        return re.match(pattern, domain)
    
    if not is_valid_domain(domain):
        mbox.showerror("Error", f"Cannot Track Host {domain}\nInvalid Host!")
        return
    
    if stop_button.cget("text") == "STOP":
        stop_button.invoke()
        global table_stop
        table_stop = True
    table_widget.config(state=tk.NORMAL)
    table.clear_rows()
    table_widget.delete('1.0', tk.END)
    table_widget.tag_configure('center', justify='center')
    table_widget.configure(font=('Consolas', 20, 'bold'))
    global slash_n_mod
    global root_font_size
    slash_n_mod = True
    slash_n_count()
    table_widget.insert(tk.END, f"{slash_n} SEARCHING . . . ", 'center')
    table_widget.insert(tk.END, "\n\n\n\n\n")
    table_widget.config(state=tk.DISABLED)
    table_widget.update()

    # SUB DOMAIN CLEAN
    parts = domain.split('.')
    domain = '.'.join(parts[-2:])

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect(("whois.iana.org", 43))
        except (socket.timeout, socket.gaierror, ConnectionRefusedError):
            whois_failed()
        s.send((domain + "\r\n").encode())
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        response = response.decode()
        whois_server = ""
        lines = response.split("\n")
        for line in lines:
            if line.startswith("whois:"):
                whois_server = line.split(":")[1].strip()
                break
        if not whois_server:
            whois_failed()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((whois_server, 43))
            s.send((domain + "\r\n").encode())
            response = b""
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response += data
        except OSError:
            whois_404()
            return
        response = response.decode()
        response_lines = response.split("\n")
        cleaned_response_lines = []
        for line in response_lines:
            if "URL of the ICANN Whois Inaccuracy Complaint Form" in line:
                break
            cleaned_response_lines.append(line.strip())
        cleaned_response = "\n".join(cleaned_response_lines)
        s.close()
        if not stop_button.cget("text") == "START":
            stop_button.invoke()
        table_widget.config(state=tk.NORMAL)
        table.clear_rows()
        if 'Domain Name' not in cleaned_response:
            whois_404()
            return
        data = {}
        lines = cleaned_response.split('\n')
        for line in lines:
            if line.strip():
                try:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()[:80] + '...' if len(value.strip()) > 80 else value.strip()
                except ValueError:
                    pass
        response_json = json.dumps(data, indent=4)
        table_widget.configure(font=('Consolas', root_font_size, 'bold'))
        slash_n_mod = False
        whois = PrettyTable()
        whois.field_names = ['Property', 'Value']
        for key, value in data.items():
            whois.add_row([key, value])
        table_widget.tag_configure('center', justify='center')
        table_widget.delete('1.0', tk.END)
        # COLORIZE
        rows = whois.get_string().split("\n")
        for i, row in enumerate(rows):
            if i % 2 != 0:
                table_widget.insert(tk.END, row + "\n", "odd")
            else:
                table_widget.insert(tk.END, row + "\n")
            table_widget.tag_configure("odd", background=bg_color, foreground=font_color_2, selectbackground="blue", selectforeground="white")
            table_widget.tag_configure('center', justify='center')
            table_widget.tag_add('center', f"{i+1}.0", f"{i+1}.end")
        table_widget.insert(tk.END, "\n\n\n\n\n\n")
        table_widget.config(state=tk.DISABLED)
    except (socket.timeout, socket.gaierror, ConnectionRefusedError):
        whois_failed()

def whois_failed():
    table_widget.config(state=tk.NORMAL)
    table.clear_rows()
    table_widget.delete('1.0', tk.END)
    table_widget.tag_configure('center', justify='center')
    slash_n_count()
    table_widget.insert(tk.END, f"{slash_n} DOMAIN LOOKUP FAILED!\n" + "'" + domain + "'", 'center')
    table_widget.insert(tk.END, "\n\n\n\n\n")
    table_widget.config(state=tk.DISABLED)
    table_widget.update()

def whois_404():
    table_widget.config(state=tk.NORMAL)
    table.clear_rows()
    table_widget.delete('1.0', tk.END)
    table_widget.tag_configure('center', justify='center')
    slash_n_count()
    table_widget.insert(tk.END, f"{slash_n} DOMAIN DOES NOT EXIST!\n" + "'" + domain + "'", 'center')
    table_widget.insert(tk.END, "\n\n\n\n\n")
    table_widget.config(state=tk.DISABLED)
    table_widget.update()

# PORT SCAN

global port_scan_status
global port_scan
port_scan = None
port_scan_status = False
thread_pool_executor = None
stop_event = None

def port_on_close():
    global port_scan_status
    global thread_pool_executor
    global stop_event
    global port_scan
    port_scan_status = False
    stop_event.set()
    if thread_pool_executor:
        thread_pool_executor.shutdown(wait=False)
    port_scan.destroy()

def port_scan_start(ip_address):
    global port_scan_status
    global thread_pool_executor
    global stop_event
    global port_scan

    if port_scan_status:
        mbox.showerror("Error", f"Port Scan Already in Progress!")
        port_scan.lift()
        port_scan.focus_force()
        return

    if port_scan is not None and port_scan.winfo_exists():
        port_on_close()

    stop_event = threading.Event()

    def scan_port(port, stop_event):
        if stop_event.is_set():
            return

        try:
            # IPv6
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.settimeout(0.9)
            result = sock.connect_ex((ip_address, port))
            if result == 0:
                try:
                    protocol = socket.getservbyport(port)
                except OSError:
                    protocol = '???'
                capitalized_protocol = protocol.upper()
                result_queue.put("  Port {}: Open/{}\n".format(port, capitalized_protocol))
            return
        except socket.error:
            pass

        # IPv4
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.9)
        result = sock.connect_ex((ip_address, port))
        if result == 0:
            try:
                protocol = socket.getservbyport(port)
            except OSError:
                protocol = '???'
            capitalized_protocol = protocol.upper()
            result_queue.put("  Port {}: Open/{}\n".format(port, capitalized_protocol))

    def scan_ports(stop_event):
        global port_scan_status
        global thread_pool_executor
        port_scan_status = True
        try:
            result_queue.put("\n  # Port Scanning {} #\n\n".format(ip_address))
            with concurrent.futures.ThreadPoolExecutor(max_workers=1500) as executor:
                thread_pool_executor = executor
                futures = [executor.submit(scan_port, port, stop_event) for port in range(1, 65536)]
                concurrent.futures.wait(futures)

            result_queue.put("\n  # Port Scan COMPLETE #\n")
            port_scan_status = False
        except Exception:
            pass

    def update_results():
        while not result_queue.empty():
            result = result_queue.get()
            tag_name = "even" if int(results.index(tk.END).split('.')[0]) % 2 == 0 else "odd"
            results.config(state=tk.NORMAL)
            results.insert(tk.END, result, tag_name)
            results.config(state=tk.DISABLED)
            results.see(tk.END)

        if not stop_event.is_set():
            port_scan.after(100, update_results)

    port_scan = tk.Toplevel(root)
    port_scan.title("PORT SCAN - {}".format(ip_address))
    port_scan_w = len(ip_address) * 4.5 + 375
    port_scan_ww = int(port_scan_w) + 25
    port_scan.geometry(f"{int(port_scan_w)}x300")
    port_scan.configure(bg="#0d0d0d")
    port_scan.protocol("WM_DELETE_WINDOW", port_on_close)
    parent_width = root.winfo_width()
    parent_height = root.winfo_height()
    x = root.winfo_rootx() + (parent_width // 2) - (int(port_scan_ww) // 2)
    y = root.winfo_rooty() + (parent_height // 2) - (485 // 2)
    port_scan.geometry("+{}+{}".format(x, y))
    results = tk.Text(port_scan, bg="#0d0d0d", fg="white", font=("Consolas", 12, 'bold'), highlightthickness=1)
    results.pack(fill=tk.BOTH, expand=True)
    results.tag_configure("even", foreground="#00ff0d")
    results.tag_configure("odd", foreground="#a5ee80")
    scrollbar = tk.Scrollbar(results, command=results.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    results.configure(yscrollcommand=scrollbar.set)
    results.bind("<Configure>", lambda e: results.yview_moveto(1))

    def copy_port_scan_text():
        selected_text = results.get("sel.first", "sel.last")
        if selected_text:
            pyperclip.copy(selected_text)

    text_box_port_scan_menu = tk.Menu(results, tearoff=0)
    text_box_port_scan_menu.add_command(label='Copy', command=copy_port_scan_text)
    results.bind("<Button-3>", lambda event: text_box_port_scan_menu.post(event.x_root, event.y_root))
    result_queue = queue.Queue()
    scan_thread = threading.Thread(target=scan_ports, args=(stop_event,))
    scan_thread.start()
    update_results()

# RETRIEVE IP INFO

global ip_window
ip_window = None

def retrieve_ip_info(ip_address_track):
    global ip_isp_dict
    global ip_window
    
    if ip_window is not None and ip_window.winfo_exists():
        ip_window.destroy()

    def is_valid_ip(ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    if not is_valid_ip(ip_address_track):
        mbox.showerror("Error", f"Cannot Track IP {ip_address_track}\nInvalid IP")
        return

    isp_host = 'N/A'
    
    # Get the IP information using the API
    response = requests.get(f"https://ipinfo.io/{ip_address_track}/json")
    if response.status_code == 200:
        try:
            ip_info = json.loads(response.text)
        except json.JSONDecodeError:
            print("Error decoding JSON data")
    else:
        print(f"Error retrieving IP information: {response.status_code}")
        ip_info = {'ip': 'Not Found'}

    isp_host = ip_info.get('hostname', 'N/A')

    # See if IPv6 Address Host Exists
    for ip, isp in ip_isp_dict.items():
        if ip == ip_address_track:
            isp_host = isp

    ip_window = tk.Toplevel(root)
    ip_window.title("IP RESULTS")
    ip_window.configure(bg="#0d0d0d")
    ip_window.configure(highlightthickness=1.5, highlightbackground="white")
    
    # ADJUST IP RESULTS WINDOW BASED UPON HOST & ASN SIZE
    pre_asn = ip_info.get('org')
    pre_asn = len(pre_asn)
    pre_isp = len(isp_host)
    if int(pre_asn) >= int(pre_isp):
        ip_w_target = int(pre_asn)
    else:
        ip_w_target = int(pre_isp)
    ip_window_w = int(ip_w_target) * 3 + 500
    ip_window_ww = int(ip_window_w) + 25
    ip_window.geometry(f"{int(ip_window_w)}x238")
    ip_window.minsize(int(ip_window_w), 238)
    ip_window.maxsize(2000, 238)
    parent_width = root.winfo_width()
    parent_height = root.winfo_height()
    x = root.winfo_rootx() + (parent_width // 2) - (int(ip_window_ww) // 2)
    y = root.winfo_rooty() + (parent_height // 2) - (410 // 2)
    ip_window.geometry("+{}+{}".format(x, y))

    # Create the text box to display the IP information
    text_box = tk.Text(ip_window, font=("Consolas", 12, "bold"), fg="#a5ee80", bg="#0d0d0d", insertbackground="green", state=tk.DISABLED)
    text_box.pack(fill=tk.BOTH, expand=True)
    text_box.configure(state=tk.NORMAL)

    def ip_info_port_scan():
        ip = ip_info['ip']
        ip_window.destroy()
        port_scan_start(ip)
        pass

    def ip_info_trace_ip():
        ip = ip_info['ip']
        ip_window.destroy()
        tracert(ip)
    
    def ip_info_block_ip():
        ip = ip_info['ip']
        ip_window.destroy()
        kill_by_ip(ip)

    button_frame = tk.Frame(text_box, bg="#0d0d0d")
    button_frame.place(relx=0.5, rely=0.885, anchor=tk.CENTER)

    port_scan_button = tk.Button(button_frame, text="PORT SCAN", command=ip_info_port_scan, bg="green",
                                 fg="white", width=12, font=("Consolas", 12, "bold"), cursor="hand2")
    port_scan_button.pack(side=tk.LEFT, padx=(10, 5))

    track_host_button = tk.Button(button_frame, text="TRACE IP", command=ip_info_trace_ip,
                                  bg="yellow", fg="black", width=12, font=("Consolas", 12, "bold"),
                                  cursor="hand2")
    track_host_button.pack(side=tk.LEFT, padx=5)

    block_button = tk.Button(button_frame, text="BLOCK IP", command=ip_info_block_ip,
                             bg="#f24c2e", fg="white", width=12, font=("Consolas", 12, "bold"),
                             cursor="hand2")
    block_button.pack(side=tk.LEFT, padx=(5, 10))

    # EASTER EGG
    if ip_address_track == '69.69.69.69':
        mbox.showinfo("Traffic Jack", "Aren't You Just a Little Comedian ;)")
        ip_window.lift()

    # Define a function to handle the copy action
    def copy_text():
        selected_text = text_box.get("sel.first", "sel.last")
        if selected_text:
            pyperclip.copy(selected_text)

    # Create a context menu for the text_box
    text_box_menu = tk.Menu(text_box, tearoff=0)
    text_box_menu.add_command(label='Copy', command=copy_text)

    # Bind the context menu to the text_box
    text_box.bind("<Button-3>", lambda event: text_box_menu.post(event.x_root, event.y_root))

    # Display the IP address in the middle of the text box
    ip_label = tk.Label(text_box, text=ip_info['ip'], font=("Consolas", 16, "bold"), fg="#00ff0d", bg="#0d0d0d")
    ip_label.place(relx=0.5, rely=0.07, anchor=tk.CENTER)

    # Check if the API returns only two variables, "ip" and "bogon"
    if len(ip_info) == 2 and 'ip' in ip_info and 'bogon' in ip_info:
        error_label = tk.Label(text_box, text="IP Address Not Found", font=("Consolas", 16, "bold"), fg="#f24c2e", bg="#0d0d0d")
        error_label.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
    else:
        # Display the IP information in the text box
        text_box.insert(tk.END, f"\n\n")
        text_box.insert(tk.END, f"  HOST: {isp_host}  \n")
        text_box.insert(tk.END, f"  ASN: {ip_info.get('org', 'N/A')}  \n")
        text_box.insert(tk.END, f"  CITY: {ip_info.get('city', 'N/A')}  \n")
        text_box.insert(tk.END, f"  POSTAL: {ip_info.get('postal', 'N/A')}  \n")
        text_box.insert(tk.END, f"  REGION: {ip_info.get('region', 'N/A')}  \n")
        text_box.insert(tk.END, f"  COUNTRY: {ip_info.get('country', 'N/A')}  \n")
        text_box.insert(tk.END, f"  LOCATION: {ip_info.get('loc', 'N/A')}  \n")

    # Apply colors to specific sections of the text
    text_box.tag_config("variable", foreground="#00ff0d")
    text_box.tag_add("header", "2.0", "2.end")
    text_box.tag_add("variable", "3.7", "3.end")
    text_box.tag_add("variable", "4.7", "4.end")
    text_box.tag_add("variable", "5.8", "5.end")
    text_box.tag_add("variable", "6.10", "6.end")
    text_box.tag_add("variable", "7.10", "7.end")
    text_box.tag_add("variable", "8.10", "8.end")
    text_box.tag_add("variable", "9.11", "9.end")
    text_box.configure(state=tk.DISABLED)

# RETRIEVE APP INFO

global app_window
app_window = None

def retrieve_app_info(app):
    global app_window
    global app_window_close
    app_window_close = False

    if app_window is not None and app_window.winfo_exists():
        app_window.destroy()

    def is_numeric(string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    if is_numeric(app):
        app_type = 'PID'
    else:
        app_type = 'APP'

    app_window = tk.Toplevel(root)
    app_window.title(f"{app_type} RESULTS")
    app_window.configure(bg="#0d0d0d")
    app_window.minsize(550, 238)
    app_window.configure(highlightthickness=1.5, highlightbackground="white")

    parent_width = root.winfo_width()
    parent_height = root.winfo_height()
    x = root.winfo_rootx() + (parent_width // 2) - (820 // 2)
    y = root.winfo_rooty() + (parent_height // 2) - (420 // 2)
    app_window.geometry("+{}+{}".format(x, y))

    text_box = tk.Text(app_window, font=("Consolas", 12, "bold"), fg="#a5ee80", bg="#0d0d0d", insertbackground="green",
                       state=tk.DISABLED)
    text_box.pack(fill=tk.BOTH, expand=True)
    text_box.configure(state=tk.NORMAL)

    def copy_text():
        selected_text = text_box.get("sel.first", "sel.last")
        if selected_text:
            pyperclip.copy(selected_text)

    text_box_menu = tk.Menu(text_box, tearoff=0)
    text_box_menu.add_command(label='Copy', command=copy_text)
    text_box.bind("<Button-3>", lambda event: text_box_menu.post(event.x_root, event.y_root))

    if app_type == 'PID':
        app_label = tk.Label(text_box, text=f'PID {app}', font=("Consolas", 16, "bold"), fg="#00ff0d", bg="#0d0d0d")
    else:
        app_label = tk.Label(text_box, text=app, font=("Consolas", 16, "bold"), fg="#00ff0d", bg="#0d0d0d")
    app_label.place(relx=0.5, rely=0.07, anchor=tk.CENTER)

    def convert_size(size_bytes):
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]
        base = 1024
        size_bytes = int(size_bytes)
        unit_index = 0
        while size_bytes >= base and unit_index < len(units) - 1:
            size_bytes /= base
            unit_index += 1
        return f"{size_bytes:.2f} {units[unit_index]}"

    def get_file_info(file_path):
        global file_name
        global file_size
        global creation_time
        global modification_time
        global access_time
        global file_hash
        global exe_path_m
        file_name = os.path.basename(file_path)
        file_size = convert_size(os.path.getsize(file_path))
        file_creation_time = os.path.getctime(file_path)
        file_modification_time = os.path.getmtime(file_path)
        file_access_time = os.path.getatime(file_path)

        if len(exe_path) > 65:
            exe_path_m = exe_path[:62] + "..."
        else:
            exe_path_m = exe_path

        creation_time = datetime.fromtimestamp(file_creation_time).strftime('%I:%M:%S %p | %m-%d-%Y')
        modification_time = datetime.fromtimestamp(file_modification_time).strftime('%I:%M:%S %p | %m-%d-%Y')
        access_time = datetime.fromtimestamp(file_access_time).strftime('%I:%M:%S %p | %m-%d-%Y')

        hash_object = hashlib.sha256()
        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_object.update(chunk)
        file_hash = hash_object.hexdigest()

    def track_application(process_identifier):
        global pid
        global exe_path
        global process
        global app_window_close
        global exe_path_e
        pid = None
        exe_path_exists = False
        exe_path_e = False
        for process in psutil.process_iter(['pid', 'name', 'exe']):
            if process.info['name'] == process_identifier or str(process.info['pid']) == process_identifier:
                pid = process.info['pid']
                exe_path = process.info['exe']
                try:
                    with open(exe_path, 'r'):
                        pass
                    get_file_info(exe_path)
                    exe_path_exists = True
                except IOError:
                    exe_path_exists = False
                    exe_path_e = True
                break
        if not exe_path_exists:
            app_window_close = True
            return

    track_application(app)
    
    if app_window_close:
        app_window.destroy()
        if exe_path_e:
            if app_type == 'PID':
                mbox.showerror("Error", f"File Path for PID {app} was Not Found!")
            else:
                mbox.showerror("Error", f"File Path for Application {app} was Not Found!")
            return
        else:
            if app_type == 'PID':
                mbox.showerror("Error", f"Cannot Track PID {app}\nPID is Not Active!")
                return
            else:
                mbox.showerror("Error", f"Cannot Track Application {app}\nApplication is Not Active!")
                return
    
    if pid is not None:
        text_box.insert(tk.END, f"\n\n ")
        if app_type == 'APP':
            text_box.insert(tk.END, f" PID: {pid}  \n")
        else:
            text_box.insert(tk.END, f" FILE: {file_name}  \n")
        text_box.insert(tk.END, f"  PATH: {exe_path_m}  \n")
        text_box.insert(tk.END, f"  SIZE: {file_size}  \n")
        text_box.insert(tk.END, f"  CREATION: {creation_time}  \n")
        text_box.insert(tk.END, f"  MODIFIED: {modification_time}  \n")
        text_box.insert(tk.END, f"  ACCESSED: {access_time }  \n")
        text_box.insert(tk.END, f"  FILE HASH: {file_hash}  \n")

        text_box.tag_config("variable", foreground="#00ff0d")
        text_box.tag_add("header", "2.0", "2.end")
        text_box.tag_add("variable", "3.7", "3.end")
        text_box.tag_add("variable", "4.7", "4.end")
        text_box.tag_add("variable", "5.8", "5.end")
        text_box.tag_add("variable", "6.11", "6.end")
        text_box.tag_add("variable", "7.11", "7.end")
        text_box.tag_add("variable", "8.11", "8.end")
        text_box.tag_add("variable", "9.12", "9.end")
        text_box.configure(state=tk.DISABLED)

        longest_line = max(text_box.get(1.0, "end-1c").split("\n"), key=len)
        text_width = len(longest_line)

        app_window.update_idletasks()
        min_width = app_label.winfo_width() + 50
        app_window.minsize(max(min_width, text_width * 8), 238)
        app_window_width_math = max(min_width, text_width * 10)
        app_window.maxsize(int(app_window_width_math), 238)
        app_window.geometry(f"{int(app_window_width_math)}x230")

        def open_file_location():
            file_folder = Path(exe_path).parent
            os.startfile(file_folder)

        def open_virus_total():
            url = f"https://www.virustotal.com/gui/file/{file_hash}"
            webbrowser.open(url)
    
        def pre_kill_by_app():
            kill_by_app(file_name)

        def pre_kill_by_pid():
            kill_by_pid(pid)
            
        open_location_button = tk.Button(app_window, text="OPEN FILE LOCATION", command=open_file_location,
                                         bg="yellow", fg="black", width=19, font=("Consolas", 12, "bold"),
                                         cursor="hand2")
        open_location_button.place(relx=0.50, rely=0.88, anchor=tk.CENTER)

        virus_total_button = tk.Button(app_window, text="OPEN VIRUS TOTAL", command=open_virus_total, bg="green",
                                       fg="white", width=19, font=("Consolas", 12, "bold"), cursor="hand2")
        virus_total_button.place(relx=0.257, rely=0.88, anchor=tk.CENTER)

        if app_type == 'APP':
            block_button = tk.Button(app_window, text="BLOCK APPLICATION", command=pre_kill_by_app, bg="#f24c2e",
                                           fg="white", width=19, font=("Consolas", 12, "bold"), cursor="hand2")
            block_button.place(relx=0.743, rely=0.88, anchor=tk.CENTER)
        
        if app_type == 'PID':
            block_button = tk.Button(app_window, text="BLOCK PID", command=pre_kill_by_pid, bg="#f24c2e",
                                           fg="white", width=19, font=("Consolas", 12, "bold"), cursor="hand2")
            block_button.place(relx=0.74, rely=0.88, anchor=tk.CENTER)

kill_button = tk.Button(root, text="BLOCK", command=lambda: create_kill_window(root, options), bg="blue", fg="white", width=root_button_width, font=("Consolas", button_size, "bold"), cursor="hand2")
kill_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=kill_button_x, y=kill_button_y)

# BLOCK HOST

def kill_by_host(value):
    m_value = value
    global kill_ip_dict
    def get_ip_addresses(value):
        try:
            ip_addresses = socket.gethostbyname_ex(value)[2]
            return ip_addresses
        except socket.gaierror as e:
            return []

    def get_subdomains(url):
        domains = tldextract.extract(url).registered_domain
        subdomains = set()
        
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return subdomains
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(url, href)
                if domains in absolute_url:
                    subdomain = tldextract.extract(absolute_url).subdomain
                    if subdomain and subdomain != 'www':
                        subdomains.add(subdomain)
        
        return list(subdomains)

    def is_valid_domain_block(value):
        pattern = r"^(?!-)(?:[A-Za-z0-9-]{0,62}[A-Za-z0-9]\.)+[A-Za-z]{2,}$"
        return re.match(pattern, value)

    def check_ping(value):
        command = ['ping', '-n', '1', value]
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except subprocess.CalledProcessError:
            return False
    
    if not check_ping(value):
        mbox.showerror("Error", f"{value} is Offline or Not Responding!")
        return
        
    if is_valid_domain_block(value):
        subdomains = get_subdomains(f"http://{value}")
        ip_addresses = get_ip_addresses(value)
        host_ips = []

        for subdomain in subdomains:
            subdomain_ip_addresses = get_ip_addresses(f"{subdomain}.{value}")
            if subdomain_ip_addresses:
                for ip in subdomain_ip_addresses:
                    host_ips.append(ip)
                    kill_ip_dict[ip] = True

        if ip_addresses:
            for ip in ip_addresses:
                host_ips.append(ip)

        # Remove duplicate IP addresses
        host_ips = list(set(host_ips))

        def host_block_fail():
            mbox.showerror("Error", f"Cannot Block Host {m_value}\nAdministrative Rights Required!")

        def host_block_success():
            mbox.showinfo("Success", f"Successfully Blocked Host {m_value}")

        # Block IP addresses
        host_success_status = True  # Track the success status

        for value in host_ips:
            try:
                subprocess.run(f"netsh advfirewall firewall add rule name=\"Block {value}\" dir=in action=block remoteip={value}", shell=True, check=True)
                subprocess.run(f"netsh advfirewall firewall add rule name=\"Block {value}\" dir=out action=block remoteip={value}", shell=True, check=True)
            except subprocess.CalledProcessError:
                host_success_status = False  # Set success status to False if there's an error
                host_block_fail()
                break

        if host_success_status:
            host_block_success()
    else:
        mbox.showerror("Error", f"Cannot Block Host {m_value}\nInvalid Host!")

# BLOCK IP ADDRESS

kill_ip_dict = {}

def kill_by_ip(value):
    m_value = value
    global kill_ip_dict
    def is_valid_ip_block(value):
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False
    if is_valid_ip_block(value):
        def ip_block_fail():
            mbox.showerror("Error", f"Cannot Block IP {m_value}\nAdministrative Rights Required!")
        def ip_block_success():
            mbox.showinfo("Success", f"Successfully Blocked IP {m_value}")
            kill_ip_dict[value] = True
        try:
            subprocess.run(f"netsh advfirewall firewall add rule name=\"Block {value}\" dir=in action=block remoteip={value}", shell=True, check=True)
            subprocess.run(f"netsh advfirewall firewall add rule name=\"Block {value}\" dir=out action=block remoteip={value}", shell=True, check=True)
        except subprocess.CalledProcessError:
            ip_block_fail()
        else:
            ip_block_success()
    else:
        mbox.showerror("Error", f"Cannot Block IP {m_value}\nInvalid IP Address!")

# BLOCK PORT

kill_port_dict = {}

def kill_by_port(value):
    m_value = value
    global kill_port_dict
    port = None
    try:
        port = int(value)
        if port < 65535:
            def port_block_fail():
                mbox.showerror("Error", f"Cannot Block Port {port}\nAdministrative Rights Required!")
            def port_block_success():
                mbox.showinfo("Success", f"Successfully Blocked Port {port}")
                kill_port_dict[port] = True
            try:
                add_rule_in = subprocess.run(f"netsh advfirewall firewall add rule name=\"Block Port {port}\" dir=in action=block protocol=TCP localport={port}", shell=True, capture_output=True, text=True)
                add_rule_out = subprocess.run(f"netsh advfirewall firewall add rule name=\"Block Port {port}\" dir=out action=block protocol=TCP localport={port}", shell=True, capture_output=True, text=True)
                if "The requested operation requires elevation" in add_rule_in.stdout or "The requested operation requires elevation" in add_rule_out.stdout:
                    raise PermissionError("Elevation Required")
                port_block_success()
            except PermissionError:
                port_block_fail()
            except subprocess.CalledProcessError:
                port_block_fail()
        else:
            mbox.showerror("Error", f"Cannot Block Port {port}\nInvalid Port!")
    except ValueError:
        mbox.showerror("Error", f"Cannot Block Port \nInvalid Port")

# BLOCK APPLICATION

global kill_app_dict
kill_app_dict = []

def kill_by_app(value):
    global kill_app_dict
    print(f"Killing by Application: {value}")
    try:
        output = subprocess.check_output(f"taskkill /f /im {value}", stderr=subprocess.STDOUT, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        mbox.showinfo("Success", f"Successfully Blocked Application {value}")
        kill_app_dict.append(value)
        return
    except subprocess.CalledProcessError as e:
        error_output = e.output.decode().strip()
        if "Access is denied" in error_output:
            mbox.showerror("Error", f"Cannot Block Application {value}\nAdministrative Rights Required!")
        else:
            mbox.showerror("Error", f"An Error Occurred Blocking Application {value}!")

# BLOCK PID

global kill_pid_dict
kill_pid_dict = []

def kill_by_pid(value):
    global kill_pid_dict
    print(f"Killing by PID: {value}")
    try:
        output = subprocess.check_output(f"taskkill /f /pid {value}", stderr=subprocess.STDOUT, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        mbox.showinfo("Success", f"Successfully Blocked PID {value}")
        kill_pid_dict.append(int(value))
        return
    except subprocess.CalledProcessError as e:
        error_output = e.output.decode().strip()
        if "Access is denied" in error_output:
            mbox.showerror("Error", f"Cannot Block PID {value}\nAdministrative Rights Required!")
        else:
            mbox.showerror("Error", f"An Error Occurred Blocking PID {value}!")

# KILL WINDOW

options = ["IP Address", "Host", "Port", "Application", "PID"]

kill_window = None

# Function to create the new window
def create_kill_window(parent, options):
    global kill_window
    if kill_window is not None and kill_window.winfo_exists():
        kill_window.lift()
        kill_window.focus_force()
        return
    stop_button_text = stop_button.cget("text")
    if stop_button_text == "STOP":
        stop_button.invoke()
        global table_stop
        table_stop = True
    # Create the new window
    kill_window = tk.Toplevel(parent)
    kill_window.geometry("300x250")
    kill_window.title("BLOCK")
    kill_window.configure(bg="#0d0d0d")
    kill_window.attributes('-alpha', 1)  # Set transparency to 90%
    kill_window.maxsize(300, 300)
    kill_window.minsize(300, 300)

    # WHITE BORDER
    canvas = tk.Canvas(kill_window, bg="#0d0d0d", width=300, height=300)
    canvas.pack()
    canvas.create_rectangle(1, 1, 300, 300, outline="white", width=1)

    # Center the window on the parent
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    x = parent.winfo_rootx() + (parent_width // 2) - (325 // 2)
    y = parent.winfo_rooty() + (parent_height // 2) - (470 // 2)
    kill_window.geometry("+{}+{}".format(x, y))

    global kill_label
    kill_label = tk.Label(kill_window, text="《 BLOCK 》", bg="#0d0d0d", fg="#f24c2e", font=("Consolas", 15, "bold"))
    kill_label.place(relx=0.5, rely=0.13, anchor=tk.CENTER)

    ip_button = tk.Button(kill_window, text="IP ADDRESS", command=lambda: create_text_box(kill_window, "IP Address"), bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), cursor="hand2")
    ip_button.place(relx=0.5, rely=0.29, anchor=tk.CENTER)

    host_button = tk.Button(kill_window, text="HOST", command=lambda: create_text_box(kill_window, "Host"), bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), cursor="hand2")
    host_button.place(relx=0.5, rely=0.43, anchor=tk.CENTER)

    port_button = tk.Button(kill_window, text="PORT", command=lambda: create_text_box(kill_window, "Port"), bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), cursor="hand2")
    port_button.place(relx=0.5, rely=0.57, anchor=tk.CENTER)

    app_button = tk.Button(kill_window, text="APPLICATION", command=lambda: create_text_box(kill_window, "Application"), bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), cursor="hand2")
    app_button.place(relx=0.5, rely=0.71, anchor=tk.CENTER)

    pid_button = tk.Button(kill_window, text="PID", command=lambda: create_text_box(kill_window, "PID"), bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), cursor="hand2")
    pid_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

def kill_window_closed():
    global kill_window
    kill_window = None

# Function to create the text box and submit button
def create_text_box(parent, option):
    global admin_text
    global submit_button
    global back_button
    
    # Remove all the buttons
    for child in parent.winfo_children():
        if isinstance(child, tk.Button):
            child.destroy()
    
    kill_label.destroy()

    # Create the centered text above the text box
    title_label = tk.Label(parent, text=f"Enter {option}", bg="#0d0d0d", fg="white", font=("Consolas", 12, "bold"))
    title_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

    # Create the 40 character long text box and make it pre-selected
    value_entry = tk.Entry(parent, width=20, font=("Consolas", 12, "bold"))
    value_entry.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    value_entry.bind("<Button-3>", paste_text)
    value_entry.focus()
    
    # Add red text for IP Address or Port option
    if option == "IP Address" or option == "Port" or option == "Host":
        admin_text = tk.Label(parent, text="Admin Rights Required! \n Permanent Changes to Firewall!\n", bg="#0d0d0d", fg="#f24c2e", font=("Consolas", 9, "bold"))
        admin_text.place(relx=0.5, rely=0.54, anchor=tk.CENTER)
        
    # Add red text for IP Address or Port option
    if option == "Application":
        admin_text = tk.Label(parent, text="Case Sensitive\n", bg="#0d0d0d", fg="#f24c2e", font=("Consolas", 9, "bold"))
        admin_text.place(relx=0.5, rely=0.51, anchor=tk.CENTER)

    # Bind the <Return> event to the submit_value function
    value_entry.bind('<Return>', lambda event: submit_value(parent, option, value_entry.get()))

    # Create the submit button
    if option == "IP Address" or option == "Port" or option == "Host":
        submit_button = tk.Button(parent, text="BLOCK", command=lambda: submit_value(parent, option, value_entry.get()), bg="blue", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        submit_button.place(relx=0.5, rely=0.64, anchor=tk.CENTER)
    elif option == "Application":
        submit_button = tk.Button(parent, text="BLOCK", command=lambda: submit_value(parent, option, value_entry.get()), bg="blue", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        submit_button.place(relx=0.5, rely=0.58, anchor=tk.CENTER)  
    else: 
        submit_button = tk.Button(parent, text="BLOCK", command=lambda: submit_value(parent, option, value_entry.get()), bg="blue", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        submit_button.place(relx=0.5, rely=0.54, anchor=tk.CENTER)

    # Create the go back button
    if option == "IP Address" or option == "Port" or option == "Host":
        back_button = tk.Button(parent, text="GO BACK", command=lambda: go_back(parent, options), bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        back_button.place(relx=0.5, rely=0.765, anchor=tk.CENTER)
    elif option == "Application":
        back_button = tk.Button(parent, text="GO BACK", command=lambda: go_back(parent, options), bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        back_button.place(relx=0.5, rely=0.705, anchor=tk.CENTER)
    else:
        back_button = tk.Button(parent, text="GO BACK", command=lambda: go_back(parent, options), bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
        back_button.place(relx=0.5, rely=0.665, anchor=tk.CENTER)

def go_back(parent, options):
    parent.destroy()
    create_kill_window(root, options)
    create_kill_window(parent, options)

def submit_value(parent, option, value):
    if not value:
        return
    
    if option == "IP Address" or option == "Port" or option == "Host":       
        
        def block_apply_submit_goback():
            global admin_text
            global submit_button
            global back_button
            admin_text.place_forget()
            submit_button.place_forget()
            back_button.place_forget()
            admin_text = tk.Label(parent, text=f"Invalid {option}", bg="#0d0d0d", fg="#f24c2e", font=("Consolas", 9, "bold"))
            admin_text.place(relx=0.5, rely=0.49, anchor=tk.CENTER)
            submit_button = tk.Button(parent, text="BLOCK", command=lambda: submit_value(parent, option, value_entry.get()), bg="blue", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
            submit_button.place(relx=0.5, rely=0.585, anchor=tk.CENTER)
            back_button = tk.Button(parent, text="GO BACK", command=lambda: go_back(parent, options), bg="#f24c2e", fg="white", width=15, font=("Consolas", 12, "bold"), cursor="hand2")
            back_button.place(relx=0.5, rely=0.71, anchor=tk.CENTER)

        def pre_valid_ip_block(value):
            try:
                ipaddress.ip_address(value)
                return True
            except ValueError:
                return False

        def pre_valid_domain_block(value):
            pattern = r"^(?!-)(?:[A-Za-z0-9-]{0,62}[A-Za-z0-9]\.)+[A-Za-z]{2,}$"
            return re.match(pattern, value)

        if option == "IP Address":
            if not pre_valid_ip_block(value):
                block_apply_submit_goback()
                return

        if option == "Port":
            try: 
                if not int(value) < 65535:
                    block_apply_submit_goback()
                    return
            except ValueError:
                block_apply_submit_goback()
                return

        if option == "Host":
            if not pre_valid_domain_block(value):
                block_apply_submit_goback()
                return  
    
    {
        "IP Address": kill_by_ip,
        "Host": kill_by_host,
        "Port": kill_by_port,
        "Application": kill_by_app,
        "PID": kill_by_pid,
    }[option](value)
    parent.destroy()
    if stop_button["text"] == "START":
        toggle_update()

filter_frame = tk.Frame(root, bg=black_bar_color)
filter_frame.pack(fill="x")

filter_label = tk.Label(filter_frame, text="FILTER:", bg=black_bar_color, fg="white", font=("Consolas", button_size, "bold"))
filter_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

def apply_filter(event=None):
    table_widget.focus_set()
    if not stop_button["text"] == "START":
        stop_button.invoke()
    global s_filter
    if not filter_entry.get() == "":
        s_filter = filter_entry.get()
    if stop_button["text"] == "START":
        stop_button.invoke()

filter_entry = tk.Entry(filter_frame, bg="white", width=40, font=("Consolas", 13, "bold"))
filter_entry.grid(row=0, column=1, padx=(0, 4.5), pady=0, sticky="w")
filter_entry.bind("<Button-3>", paste_text)
filter_entry.bind("<Return>", apply_filter)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
filter_frame.place(relx=0.5, rely=1.0, anchor="s", y=filter_frame_y, x=filter_frame_x)

filter_button = tk.Button(filter_frame, text=" FILTER ", command=apply_filter, bg="yellow", fg="black", width=10, font=("Consolas", 11, "bold"), pady=-1, cursor="hand2")
filter_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

def remove_filter():
    if not stop_button["text"] == "START":
        stop_button.invoke()
    global s_filter
    s_filter = "NULL"
    filter_entry.delete(0, tk.END)
    if stop_button["text"] == "START":
        toggle_update()

filter_entry.bind("<Delete>", lambda event: remove_filter())

remove_button = tk.Button(filter_frame, text=" REMOVE ", command=remove_filter, bg="#f24c2e", fg="white", width=10, font=("Consolas", 11, "bold"), pady=-1, cursor="hand2")
remove_button.grid(row=0, column=3, padx=5, pady=5, sticky="e")

# SETTINGS

settings_window_open = None

def open_settings(parent, options):
    global settings_window_open
    global root_font_size

    if settings_window_open is not None and settings_window_open.winfo_exists():
        settings_window_open.lift()
        settings_window_open.focus_force()
        return

    settings_window_open = tk.Toplevel(parent)
    settings_window_open.geometry("300x250")
    settings_window_open.title("SETTINGS")
    settings_window_open.configure(bg="#0d0d0d")
    settings_window_open.attributes('-alpha', 1)
    settings_window_open.maxsize(300, 340)
    settings_window_open.minsize(300, 340)
    
    # WHITE BORDER
    canvas = tk.Canvas(settings_window_open, bg="#0d0d0d", width=300, height=340)
    canvas.pack()
    canvas.create_rectangle(1, 1, 340, 340, outline="white", width=1)

    settings_window_open.focus_set()

    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    x = parent.winfo_rootx() + (parent_width // 2) - (325 // 2)
    y = parent.winfo_rooty() + (parent_height // 2) - (520 // 2)
    settings_window_open.geometry("+{}+{}".format(x, y))

    def close_settings():
        global settings_window_open
        settings_window_open.destroy()
        settings_window_open = None

    def select_background_color():
        global bg_color
        color = colorchooser.askcolor(parent=settings_window_open)
        if color[1]:
            parent.configure(bg=color[1])
            table_widget.configure(bg=color[1])
            bg_color = color[1]
            save_settings()

    def select_font_color():
        global font_color

        color = colorchooser.askcolor(parent=settings_window_open)
        if color[1]:
            font_color = color[1]
            apply_font_color()

    def apply_font_color():
        if font_color:
            table_widget.config(fg=font_color)
            save_settings()

    def select_font_color_2():
        global font_color_2
        color = colorchooser.askcolor(parent=settings_window_open)
        if color[1]:
            font_color_2 = color[1]
        save_settings()

    def increase_font_size():
        global root_font_size
        root_font_size += 1
        apply_font_size()
        font_size_value_label.config(text=root_font_size)
        if root_font_size > 1:
            decrease_font_button.config(state="normal")
        else:
            decrease_font_button.config(state="disabled")
        save_settings()

    def decrease_font_size():
        global root_font_size
        root_font_size -= 1
        apply_font_size()
        font_size_value_label.config(text=root_font_size)
        if root_font_size > 1:
            decrease_font_button.config(state="normal")
        else:
            decrease_font_button.config(state="disabled")
        save_settings()

    def save_settings():
        if stop_button["text"] == "START":
            stop_button.invoke()
        settings = {
            "bg_color": bg_color,
            "font_color": font_color,
            "font_color_2": font_color_2,
            "root_font_size": root_font_size
        }
        temp_dir = tempfile.gettempdir()
        settings_file_path = os.path.join(temp_dir, "settings_trafficjack.json")
        with open(settings_file_path, "w") as file:
            json.dump(settings, file)

    def reset_settings():
        if not stop_button["text"] == "START":
            stop_button.invoke()
        global root_font_size
        global bg_color
        global font_color
        global font_color_2
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        font_size = int(min(screen_width, screen_height) / 100)
        bg_color = "black"
        font_color = "#a5ee80"
        font_color_2 = "#00ff0d"
        root_font_size = font_size
        table_widget.configure(font=('Consolas', root_font_size, 'bold'))
        table_widget.configure(bg=bg_color)
        table_widget.config(fg=font_color)
        font_size_value_label.config(text=root_font_size)
        save_settings()
        if stop_button["text"] == "START":
            stop_button.invoke()

    def apply_font_size():
        table_widget.configure(font=('Consolas', root_font_size, 'bold'))

    settings_label = tk.Label(settings_window_open, text="《 SETTINGS 》", bg="#0d0d0d", fg="lime", font=("Consolas", 15, "bold"))
    settings_label.place(relx=0.5, rely=0.12, anchor=tk.CENTER)

    font_size_label = tk.Label(settings_window_open, text="FONT SIZE", bg="#0d0d0d", fg="white", font=("Consolas", 13, "bold"))
    font_size_label.place(relx=0.5, rely=0.24, anchor=tk.CENTER)

    decrease_font_button = tk.Button(settings_window_open, text=" - ", bg="blue", fg="white", font=("Consolas", 13, "bold"), command=decrease_font_size, cursor="hand2")
    decrease_font_button.place(relx=0.25, rely=0.27, anchor=tk.CENTER)

    font_size_value_label = tk.Label(settings_window_open, text=root_font_size, bg="#0d0d0d", fg="white", font=("Consolas", 13, "bold"))
    font_size_value_label.place(relx=0.5, rely=0.30, anchor=tk.CENTER)

    increase_font_button = tk.Button(settings_window_open, text=" + ", bg="blue", fg="white", font=("Consolas", 13, "bold"), command=increase_font_size, cursor="hand2")
    increase_font_button.place(relx=0.745, rely=0.27, anchor=tk.CENTER)

    bg_color_button = tk.Button(settings_window_open, text="BACKGROUND COLOR", bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), command=select_background_color, cursor="hand2")
    bg_color_button.place(relx=0.5, rely=0.39, anchor=tk.CENTER)

    font_color_button = tk.Button(settings_window_open, text="MAIN FONT COLOR", bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), command=select_font_color_2, cursor="hand2")
    font_color_button.place(relx=0.5, rely=0.51, anchor=tk.CENTER)

    font_color_button_2 = tk.Button(settings_window_open, text="SUB FONT COLOR", bg="blue", fg="white", width=20, font=("Consolas", 13, "bold"), command=select_font_color, cursor="hand2")
    font_color_button_2.place(relx=0.5, rely=0.63, anchor=tk.CENTER)
    
    modify_columns = tk.Button(settings_window_open, text="EDIT COLUMNS", bg="yellow", fg="black", width=20, font=("Consolas", 13, "bold"), command=lambda: create_columns_window(root, options), cursor="hand2")
    modify_columns.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

    reset_button = tk.Button(settings_window_open, text="RESET SETTINGS", bg="#f24c2e", fg="white", width=20, font=("Consolas", 13, "bold"), command=reset_settings, cursor="hand2")
    reset_button.place(relx=0.5, rely=0.87, anchor=tk.CENTER)

    settings_window_open.protocol("WM_DELETE_WINDOW", close_settings)

settings_button = tk.Button(root, text="\u2699", command=lambda: open_settings(root, options), bg="#808080", fg="black", width=3, font=("Consolas", 12), pady=-1, cursor="hand2")
settings_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=settings_button_x, y=settings_button_y)

# EDIT COLUMNS

column_window = None
column_variables = {}
ip_column = port_column = application_column = pid_column = sent_column = received_column = city_column = country_column = asn_column = host_column = interface_column = user_column = True

checkbox_file = os.path.join(tempfile.gettempdir(), 'checkbox_values_trafficjack.txt')

def save_checkbox_values():

    checkbox_values = {
        "IP ADDRESS": ip_column,
        "PORT": port_column,
        "APPLICATION": application_column,
        "PID": pid_column,
        "SENT": sent_column,
        "RECEIVED": received_column,
        "CITY": city_column,
        "COUNTRY": country_column,
        "ASN": asn_column,
        "HOST": host_column,
        "NIC": interface_column, 
        "USER": user_column
    }

    with open(checkbox_file, "w") as file:
        for word, value in checkbox_values.items():
            file.write(f"{word}:{int(value)}\n")

def load_checkbox_values():
    
    if not os.path.exists(checkbox_file):
        return

    with open(checkbox_file, "r") as file:
        lines = file.readlines()

    for line in lines:
        word, value = line.strip().split(":")
        column_variables[word].set(bool(int(value)))

        if word == "IP ADDRESS":
            ip_column = bool(int(value))
        if word == "PORT":
            port_column = bool(int(value))
        elif word == "APPLICATION":
            application_column = bool(int(value))
        elif word == "PID":
            pid_column = bool(int(value))
        elif word == "SENT":
            sent_column = bool(int(value))
        elif word == "RECEIVED":
            received_column = bool(int(value))
        elif word == "CITY":
            city_column = bool(int(value))
        elif word == "COUNTRY":
            country_column = bool(int(value))
        elif word == "ASN":
            asn_column = bool(int(value))
        elif word == "HOST":
            host_column = bool(int(value))
        elif word == "NIC":
            interface_column = bool(int(value))
        elif word == "USER":
            user_column = bool(int(value))

def create_columns_window(parent, options):
    global column_window, column_variables, ip_column, port_column, application_column, pid_column, sent_column, received_column, city_column, country_column, asn_column, host_column, interface_column, user_column, enable_local_status
    
    settings_window_open.destroy()

    if column_window is not None and column_window.winfo_exists():
        column_window.lift()
        column_window.focus_force()
        return

    column_window = tk.Toplevel(parent)
    column_window.title("EDIT COLUMNS")
    column_window.configure(bg="#0d0d0d")
    column_window.attributes('-alpha', 1)
    column_window.maxsize(450, 300)
    column_window.minsize(450, 300)

    checkbox_values = {
        "IP ADDRESS": 1,
        "PORT": 1,
        "APPLICATION": 1,
        "PID": 1,
        "SENT": 1,
        "RECEIVED": 1,
        "CITY": 1,
        "COUNTRY": 1,
        "ASN": 1,
        "HOST": 1,
        "NIC": 1, 
        "USER": 1
    }

    with open(checkbox_file, "w") as file:
        for word, value in checkbox_values.items():
            file.write(f"{word}:{int(value)}\n")

    # WHITE BORDER
    canvas = tk.Canvas(column_window, bg="#0d0d0d", width=450, height=300)
    canvas.pack()
    canvas.create_rectangle(1, 1, 450, 450, outline="white", width=1)

    column_window.focus_set()

    parent_width = root.winfo_width()
    parent_height = root.winfo_height()
    x = root.winfo_rootx() + (parent_width // 2) - (500 // 2)
    y = root.winfo_rooty() + (parent_height // 2) - (480 // 2)
    column_window.geometry("+{}+{}".format(x, y))

    def on_checkbox_click(word):
        global column_variables, ip_column, port_column, application_column, pid_column, sent_column, received_column, city_column, country_column, asn_column, host_column, interface_column, user_column
        num_checked = sum(column_variables[word].get() for word in column_variables)
        
        if enable_local_status:
            check_box_min = 0
        else:
            check_box_min = 4
        
        if not num_checked <= int(check_box_min):
            if column_variables[word].get() == 0:
                column_variables[word].set(False)
                if word == "IP ADDRESS":
                    ip_column = False
                if word == "PORT":
                    port_column = False
                elif word == "APPLICATION":
                    application_column = False
                elif word == "PID":
                    pid_column = False
                elif word == "SENT":
                    sent_column = False
                elif word == "RECEIVED":
                    received_column = False
                elif word == "CITY":
                    city_column = False
                elif word == "COUNTRY":
                    country_column = False
                elif word == "ASN":
                    asn_column = False
                elif word == "HOST":
                    host_column = False
                elif word == "NIC":
                    interface_column = False
                elif word == "USER":
                    user_column = False
            else:
                column_variables[word].set(True)
                if word == "IP ADDRESS":
                    ip_column = True
                    add_column('IP ADDRESS')
                if word == "PORT":
                    port_column = True
                    add_column('PORT')
                elif word == "APPLICATION":
                    application_column = True
                    add_column('APPLICATION')
                elif word == "PID":
                    pid_column = True
                    add_column('PID')
                elif word == "SENT":
                    sent_column = True
                    add_column('SENT')
                elif word == "RECEIVED":
                    received_column = True
                    add_column('RECEIVED')
                elif word == "CITY":
                    city_column = True
                    add_column('CITY')
                elif word == "COUNTRY":
                    country_column = True
                    add_column('COUNTRY')
                elif word == "ASN":
                    asn_column = True
                    add_column('ASN')               
                elif word == "HOST":
                    host_column = True
                    add_column('HOST')
                elif word == "NIC":
                    interface_column = True
                    add_column('NIC')
                elif word == "USER":
                    user_column = True
                    add_column('USER')

        if not num_checked <= int(check_box_min):
            if column_variables[word].get() == 1:
                column_variables[word].set(1)
        else:
            if column_variables[word].get() == 0:
                column_variables[word].set(1)
            else:
                column_variables[word].set(0)

    def close_columns_window():
        global column_window
        save_checkbox_values()
        column_window.destroy()
        column_window = None

    words = ["IP ADDRESS", "PORT", "APPLICATION", "PID", "SENT", "RECEIVED", "CITY", "COUNTRY", "ASN", "HOST", "NIC", "USER"]
    checkbox_frame = tk.Frame(column_window, bg="#0d0d0d")
    checkbox_frame.place(relx=0.56, rely=0.55, anchor="center")
    column_label = tk.Label(column_window, text="《 EDIT COLUMNS 》", bg="#0d0d0d", fg="yellow", font=("Consolas", 15, "bold"))
    column_label.place(relx=0.5, rely=0.13, anchor=tk.CENTER)
    words_per_column = len(words) // 2
    longest_word_length = max(len(word) for word in words)

    for i, word in enumerate(words):
        column_variables[word] = tk.BooleanVar(column_window, value=True)
        checkbox_width = longest_word_length + 3
        checkbox = tk.Checkbutton(
            checkbox_frame,
            text=word,
            variable=column_variables[word],
            command=lambda w=word: on_checkbox_click(w),
            bg="#0d0d0d",
            fg="white",
            font=("Consolas", 12, "bold"),
            anchor="w",
            selectcolor="#0d0d0d",
            width=checkbox_width,
            activebackground="#0d0d0d",
            activeforeground="white"
        )
        checkbox.select()

        if not enable_local_status:
            if word in ["CITY", "COUNTRY", "ASN", "HOST"]:
                checkbox.configure(state="disabled")

        if i < words_per_column:
            checkbox.grid(row=i, column=0, sticky="w", pady=2)
        else:
            checkbox.grid(row=i - words_per_column, column=1, sticky="w", pady=2)

    column_window.protocol("WM_DELETE_WINDOW", close_columns_window)
    load_checkbox_values()
    
    if not enable_local_status:
        column_variables['CITY'].set(True)
        column_variables['COUNTRY'].set(True)
        column_variables['ASN'].set(True)
        column_variables['HOST'].set(True)
    else:
        if city_column:
            column_variables['CITY'].set(True)
        else:
            column_variables['CITY'].set(False)
        if country_column:
            column_variables['COUNTRY'].set(True)
        else:
            column_variables['COUNTRY'].set(False)
        if asn_column:
            column_variables['ASN'].set(True)
        else:
            column_variables['ASN'].set(False)
        if host_column:
            column_variables['HOST'].set(True)
        else:
            column_variables['HOST'].set(False)
        if interface_column:
            column_variables['NIC'].set(True)
        else:
            column_variables['NIC'].set(False)
        if user_column:
            column_variables['USER'].set(True)
        else:
            column_variables['USER'].set(False)

# SAVE

def table_save():
    table_content = table_widget.get("1.0", "end-1c")
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(table_content)
        except IOError as e:
            pass

save_button = tk.Button(root, text="\u2B07", command=table_save, bg="#808080", fg="black", width=3, font=("Consolas", 12), pady=-1, cursor="hand2")
save_button.place(relx=0.5, rely=1.0, anchor=tk.S, x=save_button_x, y=save_button_y)

def disable_buttons():
    stop_button.config(state="disabled")
    clear_button.config(state="disabled")
    filter_entry.config(state="disabled")
    filter_button.config(state="disabled")
    remove_button.config(state="disabled")
    kill_button.config(state="disabled")
    local_button.config(state="disabled")
    track_button.config(state="disabled")
    active_button.config(state="disabled")
    static_button.config(state="disabled")
    settings_button.config(state="disabled")
    save_button.config(state="disabled")

def enable_buttons():
    stop_button.config(state="normal")
    clear_button.config(state="normal")
    filter_entry.config(state="normal")
    filter_button.config(state="normal")
    remove_button.config(state="normal")
    kill_button.config(state="normal")
    local_button.config(state="normal")
    track_button.config(state="normal")
    active_button.config(state="normal")
    static_button.config(state="normal")
    settings_button.config(state="normal")
    save_button.config(state="normal")

# WELCOME MESSAGE

def show_welcome_message():
    if not welcome_message:
        if not dev_mode:
            disable_buttons()
            table_widget.config(state=tk.NORMAL)
            table.clear_rows()
            table_widget.delete('1.0', tk.END)
            table_widget.tag_configure('center', justify='center')
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            font_size = int(min(screen_width, screen_height) / 90)
            bg_color = "black"
            font_color = "#00ff0d"
            root_font_size = font_size
            table_widget.configure(font=('Consolas', root_font_size, 'bold'))
            table_widget.configure(bg=bg_color)
            table_widget.config(fg=font_color)
            # Insert the text with the desired font size
            table_widget.insert(tk.END, '''\n\n\n\n\n\n\n\n
████████╗██████╗  █████╗ ███████╗███████╗██╗ ██████╗         ██╗ █████╗  ██████╗██╗  ██╗
╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██║██╔════╝         ██║██╔══██╗██╔════╝██║ ██╔╝
   ██║   ██████╔╝███████║█████╗  █████╗  ██║██║              ██║███████║██║     █████╔╝ 
   ██║   ██╔══██╗██╔══██║██╔══╝  ██╔══╝  ██║██║         ██   ██║██╔══██║██║     ██╔═██╗ 
   ██║   ██║  ██║██║  ██║██║     ██║     ██║╚██████╗    ╚█████╔╝██║  ██║╚██████╗██║  ██╗
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═╝ ╚═════╝     ╚════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
\nCreated By:\nW00DY
            ''', 'center')
            # Change the font size for the existing text
            table_widget.tag_add("font", "1.0", "end")
            table_widget.tag_configure("font", font=("Consolas", font_size))
            table_widget.insert(tk.END, "\n\n\n\n\n")
            table_widget.config(state=tk.DISABLED)
            font_size = int(min(screen_width, screen_height) / 100)
            table_widget.configure(font=("Consolas", font_size, 'bold'))
            table_widget.update()

if not dev_mode:
    show_welcome_message()
    welcome_time = time.time()
    while time.time() - welcome_time < 3:
        table_widget.update()
        threading.Event().wait(0.01)
    enable_buttons()

# LOAD SETTINGS
temp_dir = tempfile.gettempdir()
settings_file_path = os.path.join(temp_dir, "settings_trafficjack.json")
if os.path.exists(settings_file_path):
    with open(settings_file_path, "r") as file:
        settings = json.load(file)
        bg_color = settings["bg_color"]
        font_color = settings["font_color"]
        font_color_2 = settings["font_color_2"]
        root_font_size = settings["root_font_size"]
        table_widget.configure(font=('Consolas', root_font_size, 'bold'))
        table_widget.configure(bg=bg_color)
        table_widget.config(fg=font_color)
else:
    bg_color = "black"
    font_color = "#a5ee80"
    font_color_2 = "#00ff0d"
    root_font_size = font_size
    table_widget.configure(font=('Consolas', root_font_size, 'bold'))
    table_widget.configure(bg=bg_color)
    table_widget.config(fg=font_color)
    settings = {
        "bg_color": bg_color,
        "font_color": font_color,
        "font_color_2": font_color_2,
        "root_font_size": root_font_size
    }
    temp_dir = tempfile.gettempdir()
    settings_file_path = os.path.join(temp_dir, "settings_trafficjack.json")
    with open(settings_file_path, "w") as file:
        json.dump(settings, file)

# CSV

active_ip_addresses_csv = os.path.join(tempfile.gettempdir(), 'active_ip_addresses.csv')

with open(active_ip_addresses_csv, 'w') as file:
    file.write("")

# OPEN CHECK

open_check()

current_time = datetime.now().time()
formatted_time = current_time.strftime("%H%M%S")

with open(uptime_file, 'w') as file:
    file.write(formatted_time)

# LAUNCHING CAPTURE

capture_code_file = os.path.join(tempfile.gettempdir(), 'CAPTURE.exe')
if os.path.exists(capture_code_file):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.run('taskkill /f /im CAPTURE.exe', shell=True, startupinfo=startupinfo)
    subprocess.Popen([capture_code_file], startupinfo=startupinfo)

# PREPARING MMDB FILES

temp_country_path = os.path.join(tempfile.gettempdir(), 'GeoLite2-Country.mmdb')
temp_city_path = os.path.join(tempfile.gettempdir(), 'GeoLite2-City.mmdb')
temp_asn_path = os.path.join(tempfile.gettempdir(), 'GeoLite2-ASN.mmdb')
reader = geoip2.database.Reader(tempfile.gettempdir() + '/GeoLite2-Country.mmdb')
reader2 = geoip2.database.Reader(tempfile.gettempdir() + '/GeoLite2-City.mmdb')
reader3 = geoip2.database.Reader(tempfile.gettempdir() + '/GeoLite2-ASN.mmdb')

# CORE FUNCTIONS

def convert_size(size_bytes):
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]
    base = 1024
    size_bytes = int(size_bytes)
    unit_index = 0
    while size_bytes >= base and unit_index < len(units) - 1:
        size_bytes /= base
        unit_index += 1
    return f"{size_bytes:.2f} {units[unit_index]}"

def reverse_convert_size(size_string):
    if not size_string == "???":
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]
        base = 1024
        parts = size_string.split()
        if len(parts) == 2:
            value, unit = parts
        elif len(parts) == 1:
            value = parts[0]
            unit = "B"
        else:
            raise ValueError("Invalid size string format")
        size_value = float(value)
        unit_index = units.index(unit)
        for _ in range(unit_index):
            size_value *= base
        return int(size_value)
    if size_string == "???":
        return 0

def calculate_time_difference(timestamp1, timestamp2):
    global total_uptime
    time_format = "%H%M%S"
    datetime1 = datetime.strptime(timestamp1, time_format)
    datetime2 = datetime.strptime(timestamp2, time_format)
    time_diff = datetime2 - datetime1
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_diff = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    total_uptime = formatted_diff
    return total_uptime

def get_interface_for_ip(ip_address):
    connections = psutil.net_connections('all')
    for conn in connections:
        if conn.status == 'ESTABLISHED':
            try:
                remote_ip = socket.getaddrinfo(conn.raddr[0], None)[0][4][0]
                if remote_ip == ip_address:
                    local_addr = conn.laddr[0]
                    interfaces = psutil.net_if_addrs()
                    for interface_name, interface_addresses in interfaces.items():
                        for addr in interface_addresses:
                            if addr.address == local_addr:
                                return interface_name
            except socket.gaierror:
                pass

    return None

def get_username_from_pid(pid):
    try:
        process = psutil.Process(pid)
        username = process.username()
        if username.startswith("NT AUTHORITY\\"):
            username = username.replace("NT AUTHORITY\\", "")
        return username
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

# CORE DATABASE

def add_data(ip_address, port, connection_type, protocol, application, process_id, received_bytes, sent_bytes, city, country, asn, isp_host, interface, username):
    global data_dict
    key = (ip_address, port)
    
    if key in data_dict:
        data_dict[key]['process_id'] = process_id
        data_dict[key]['received_bytes'] = received_bytes
        data_dict[key]['sent_bytes'] = sent_bytes
        data_dict[key]['isp_host'] = isp_host
        data_dict[key]['application'] = application
    else:
        data_dict[key] = {
            'connection_type': connection_type,
            'protocol': protocol,
            'application': application,
            'process_id': process_id,
            'received_bytes': received_bytes,
            'sent_bytes': sent_bytes,
            'city': city,
            'country': country,
            'asn': asn,
            'isp_host': isp_host,
            'interface': interface,
            'username': username
        }

# EDIT COLUMNS

def remove_column(column):
    pattern = re.compile(r"\b{}\b".format(column.strip()), re.IGNORECASE)
    index = None
    for i, field in enumerate(table.field_names):
        if pattern.search(field.strip()):
            index = i
            break
    if index is not None:
        for row in table._rows:
            del row[index]
        del table.field_names[index]

def add_column(column):
    if column not in table.field_names:
        empty_column = [''] * len(table._rows)
        table.add_column(column, empty_column)

# INITIATING HOSTS THREAD

def HOSTS_script(ip_isp_dict_lock):
    global ip_isp_dict
    global hosts_ip_dict
    
    def is_lan_ip(ip_address):
        lan_ips = ['0.0.0.0', '127.0.0.1', '::', '::1']
        return ip_address in lan_ips or ip_address.startswith('192.168.') or ip_address.startswith('10.') or ip_address.startswith('172.')

    def get_isp(ip_address):
        if is_lan_ip(ip_address):
            return "LAN or Localhost"
        try:
            host = socket.gethostbyaddr(ip_address)
            isp = host[0]
            return isp
        except socket.herror:
            return "N/A"

    while True:
        ip_addresses = []
        for item in hosts_ip_dict:
            ip_addresses.append(item)
        ip_addresses = list(set(ip_addresses))
        filtered_ip_addresses = [ip for ip in ip_addresses if not is_lan_ip(ip)]
        filtered_ip_addresses = [ip for ip in filtered_ip_addresses if ip not in existing_ips]
        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            results = executor.map(get_isp, filtered_ip_addresses)
        with ip_isp_dict_lock:
            for ip, isp in zip(filtered_ip_addresses, results):
                ip_isp_dict[ip] = isp
        existing_ips.update(filtered_ip_addresses)
        time.sleep(0.5)

global ip_isp_dict
global ip_isp_dict_lock
existing_ips = set()
ip_isp_dict_lock = threading.Lock()
ip_isp_dict = {}
hosts_ip_dict = []
thread_hosts = threading.Thread(target=HOSTS_script, args=(ip_isp_dict_lock,))
thread_hosts.daemon = True
thread_hosts.start()

# INITIATING CAPTURE DATA SOCKET THREAD

data_usage = {}
data_usage_lock = threading.Lock() 

def receive_data_usage():
    global data_usage
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', 54321))
        except OSError:
            return

        s.listen(1)
        conn = None
        try:
            conn, addr = s.accept()
            with conn:
                received_data = b''
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    received_data += data

                received_dict = ast.literal_eval(received_data.decode())

                with data_usage_lock:
                    data_usage = received_dict
        except socket.timeout:
            pass
        finally:
            if conn:
                conn.close()

def thread_receive_data_usage():
    thread = threading.Thread(target=receive_data_usage)
    thread.daemon = True
    thread.start()
    return data_usage

# INITIATING BLOCK THREAD

def BLOCK_script():
    global kill_app_dict
    global kill_pid_dict
    
    def kill_process(process_id):
        try:
            output = subprocess.check_output(f"taskkill /f /pid {int(process_id)}", stderr=subprocess.STDOUT, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.CalledProcessError as e:
            error_output = e.output.decode().strip()
            if "Access is denied" in error_output:
                mbox.showerror("Error", f"Cannot Block PID {int(process_id)}\nAdministrative Rights Required!")
                kill_pid_dict.remove(int(process_id))

    def kill_application(application_name):
        try:
            output = subprocess.check_output(f"taskkill /f /im {application_name}", stderr=subprocess.STDOUT, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.CalledProcessError as e:
            error_output = e.output.decode().strip()
            if "Access is denied" in error_output:
                mbox.showerror("Error", f"Cannot Block Application {application_name}\nAdministrative Rights Required!")
                kill_app_dict.remove(application_name)

    def check_and_kill_processes(merged_list):
        for process in merged_list:
            if isinstance(process, int):
                if is_process_running(str(process)):
                    kill_process(process)
            elif isinstance(process, str):
                if is_application_running(process):
                    kill_application(process)

    def is_process_running(process_id):
        result = subprocess.run(['tasklist', '/FI', f"PID eq {process_id}"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return process_id in result.stdout

    def is_application_running(application_name):
        result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {application_name}'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return application_name.lower() in result.stdout.lower()

    while True:
        merged_list = None
        merged_list = kill_app_dict + kill_pid_dict
        check_and_kill_processes(merged_list)
        time.sleep(0.5)

thread_block = threading.Thread(target=BLOCK_script)
thread_block.daemon = True
thread_block.start()

# MAIN FUNCTION

def update_table():
    try:
        global table_stop
        ip_column_previous = port_column_previous = application_column_previous = pid_column_previous = sent_column_previous = received_column_previous = city_column_previous = country_column_previous = asn_column_previous = host_column_previous = interface_column_previous = user_column_previous = False
        while not table_stop:
            global column_window, column_variables, ip_column, port_column, application_column, pid_column, sent_column, received_column, city_column, country_column, asn_column, host_column, interface_column, user_column, data_dict
            global data_usage
            global hosts_ip_dict
            global ip_isp_dict
            global ip_isp_dict_lock
            global port_dict
            global row_count
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            if not ip_column:
                if 'IP ADDRESS' in table.field_names:
                    remove_column('IP ADDRESS')

            if not port_column:
                if 'PORT' in table.field_names:
                    remove_column('PORT')

            if not application_column:
                if 'APPLICATION' in table.field_names:
                    remove_column('APPLICATION')

            if not pid_column:
                if 'PID' in table.field_names:
                    remove_column('PID')

            if not sent_column:
                if 'SENT' in table.field_names:
                    remove_column('SENT')

            if not received_column:
                if 'RECEIVED' in table.field_names:
                    remove_column('RECEIVED')

            if not city_column:
                if 'CITY' in table.field_names:
                    remove_column('CITY')

            if not country_column:
                if 'COUNTRY' in table.field_names:
                    remove_column('COUNTRY')
           
            if not asn_column:
                if 'ASN' in table.field_names:
                    remove_column('ASN')
                    
            if not host_column:
                if 'HOST' in table.field_names:
                    remove_column('HOST')

            if not interface_column:
                if 'NIC' in table.field_names:
                    remove_column('NIC')

            if not user_column:
                if 'USER' in table.field_names:
                    remove_column('USER')

            # RESETTING DICTIONARIES

            table.clear_rows()
            
            hosts_ip_dict = []
            port_dict = []
            connections_dict = {}
            ip_addresses_dict = {}
            total_byte_count_ip_dict = {}
            rows = []
            t_rows = []
            row_count = 0
            pre_total_received_bytes = 0
            pre_total_sent_bytes = 0
            total_received_bytes = 0
            total_sent_bytes = 0
            
            with data_usage_lock:
                data_usage = thread_receive_data_usage()
            
            all_connections = psutil.net_connections('all')

            # UPTIME
            timestamp1 = str(start_time)
            timestamp2 = datetime.now().time()
            timestamp2 = str(timestamp2.strftime("%H%M%S"))
            calculate_time_difference(timestamp1, timestamp2)
           
            for connection in all_connections:
                if (enable_local_status and connection.status == 'ESTABLISHED') or (not enable_local_status and connection.status in ['LISTEN', 'ESTABLISHED']):
                    if connection.raddr:        # INBOUND CONNECTION
                        connection_type = '>>'
                        ip_address = connection.raddr.ip
                        if enable_local_status:
                            ip_obj = ipaddress.ip_address(ip_address)
                            if ip_obj.is_private:
                                continue
                        else:
                            ip_obj = ipaddress.ip_address(ip_address)
                            if not ip_obj.is_private:
                                continue
                        port = connection.raddr.port
                        if connection.type == socket.SOCK_STREAM:
                            protocol = 'TCP'
                        elif connection.type == socket.SOCK_DGRAM:
                            protocol = 'UDP'
                        else:
                            protocol = '???'
                    else:                       # OUTBOUND CONNECTION
                        connection_type = '<'
                        ip_address = connection.laddr.ip
                        if enable_local_status:
                            ip_obj = ipaddress.ip_address(ip_address)
                            if ip_obj.is_private:
                                continue
                        else:
                            ip_obj = ipaddress.ip_address(ip_address)
                            if not ip_obj.is_private:
                                continue
                        port = connection.laddr.port
                        if connection.type == socket.SOCK_STREAM:
                            protocol = 'TCP'
                        elif connection.type == socket.SOCK_DGRAM:
                            protocol = 'UDP'
                        else:
                            protocol = '???'

                    key = (ip_address, port)
                    
                    # SUBMIT IP TO HOST THREAD

                    if not static_mode:
                        if not ip_address in hosts_ip_dict:
                            hosts_ip_dict.append(ip_address)
                                       
                    # PROCESS ID & APPLICATION
                    
                    process_id = '???'
                    application = '???'
                    try:
                        if key in data_dict:
                                process_id = connection.pid
                                application = data_dict[key]['application']
                        else:
                            process = psutil.Process(connection.pid)
                            application = os.path.splitext(process.name())[0]
                            application = process.name()
                            process_id = connection.pid
                    except:
                        application = '???'
                        process_id = '???'

                    # NIC
                   
                    interface = None
                    try:
                        if key in data_dict:
                            interface = data_dict[key]['interface']
                            if interface == None:
                                interface = get_interface_for_ip(ip_address)
                        else:
                            interface = get_interface_for_ip(ip_address)
                    except:
                        interface = None

                    # USERNAME
                   
                    username = '???'
                    if user_column:
                        try:
                            if key in data_dict:
                                username = data_dict[key]['username']
                                if username == '???':
                                    if not process_id == '???':
                                        username = get_username_from_pid(process_id)
                                        if not username:
                                            username = 'SYSTEM'
                            else:
                                if not process_id == '???':
                                    username = get_username_from_pid(process_id)
                                    if not username:
                                        username = 'SYSTEM'
                        except:
                            username = '???'

                    # CITY, COUNTRY, & ASN
                    
                    city = '???'
                    country = '???'
                    asn = '???'
                    if enable_local_status:
                        if key in data_dict:
                                country = data_dict[key]['country']
                                city = data_dict[key]['city']
                                asn = data_dict[key]['asn']
                        else:
                            try:
                                response = reader.country(ip_address)
                                country = response.country.name if response.country.name is not None else '???'
                            except:
                                country = '???'

                            try:
                                response2 = reader2.city(ip_address)
                                city = response2.city.name if response2.city.name is not None else '???'
                            except:
                                city = '???'

                            try:
                                response3 = reader3.asn(ip_address)
                                asn = response3.autonomous_system_organization if response3.autonomous_system_organization is not None else '???'
                                asn = asn.capitalize()
                                # ASN FILTER
                                if asn.startswith("Google"):
                                    asn = "Google"
                                if asn.startswith("Microsoft"):
                                    asn = "Microsoft"
                                if asn.startswith("Akamai"):
                                    asn = "Akamai"
                                if len(asn) > 20:
                                    asn = asn[:20] + "..."
                            except:
                                asn = '???'

                    # BLOCK

                    table_widget.config(state=tk.NORMAL)

                    if (ip_address, port, process_id) in connections_dict:
                        continue
                        
                    if ip_address in kill_ip_dict:
                        continue
                            
                    if port in kill_port_dict:
                        continue

                    # DICTIONARIES

                    connections_dict[(ip_address, port, process_id)] = True
                    ip_addresses_dict[ip_address, interface] = True
                    if not port in port_dict:
                        port_dict.append(port)

                    # SENT & RECEIVED BYTES

                    sent_bytes = '???'
                    received_bytes = '???'
                    
                    try:
                        if ip_address in data_usage:
                            pre_total_received_bytes = data_usage[ip_address]["received_bytes"]
                            pre_total_sent_bytes = data_usage[ip_address]["sent_bytes"]
                            sent_bytes = convert_size(pre_total_sent_bytes)
                            received_bytes = convert_size(pre_total_received_bytes)
                    except KeyError:
                        pass

                    # ASN

                    if not enable_local_status:
                        asn = 'LOCAL'
                        country = asn
                        city = asn

                    isp_host = None
                    if not static_mode:
                        if enable_local_status:
                            isp_host = data_dict.get(key, {}).get('isp_host')
                            if isp_host is None or isp_host == '???':
                                isp_host = '???'
                                if ip_address in ip_isp_dict:
                                    isp_host = ip_isp_dict[ip_address]
                                    if isp_host:
                                        parts = isp_host.split('.')
                                        isp_host = '.'.join(parts[-2:])
                        else:
                            isp_host = 'LOCAL'

                    if not static_mode:
                        if not s_filter == "NULL":
                            if s_filter:
                                matched = False
                                for val in (ip_address, port, protocol, application, process_id, city, country, asn, isp_host, interface, username):#
                                    if fuzz.ratio(s_filter.lower(), str(val).lower()) >= 85:
                                        matched = True
                                if not matched:
                                    continue

                    # SENT & RECEIVED BYTES

                    if enable_local_status:
                        try:
                            ip_obj = ipaddress.ip_address(ip_address)
                            if ip_obj.is_private:
                                continue
                            else:
                                if not static_mode:
                                    if not ip_address in total_byte_count_ip_dict:
                                        total_received_bytes += pre_total_received_bytes
                                        total_sent_bytes += pre_total_sent_bytes
                                        total_byte_count_ip_dict[ip_address] = True
                                pass
                        except ValueError:
                            pass           
                    else:
                        if ip_address in ignored_ips:
                            if not static_mode:
                                if not ip_address in total_byte_count_ip_dict:
                                    total_received_bytes += pre_total_received_bytes
                                    total_sent_bytes += pre_total_sent_bytes
                                    total_byte_count_ip_dict[ip_address] = True
                            pass
                        else:
                            try:
                                ip_obj = ipaddress.ip_address(ip_address)
                                if ip_obj.is_private:
                                    if not static_mode:
                                        if not ip_address in total_byte_count_ip_dict:
                                            total_received_bytes += pre_total_received_bytes
                                            total_sent_bytes += pre_total_sent_bytes
                                            total_byte_count_ip_dict[ip_address] = True
                                    pass
                                else:
                                    continue
                            except ValueError:
                                pass
                    
                    if not static_mode:
                        if active_connections:
                            if sent_bytes == "0.00 B" and received_bytes == "0.00 B":
                                continue
                            if sent_bytes == "???" and received_bytes == "???":
                                continue
                    
                    # DATA DICT
                    
                    add_data(ip_address, port, connection_type, protocol, application, process_id, received_bytes, sent_bytes, city, country, asn, isp_host, interface, username)
                    
                    # FIELD NAMES
                    
                    if not static_mode:
                        t_row = []
                        field_names = ['IP ADDRESS', 'PORT', 'APPLICATION', 'PID', 'SENT', 'RECEIVED', 'CITY', 'COUNTRY', 'ASN', 'HOST', 'NIC', 'USER']
                        
                        # IP ADDRESS
                        if not ip_column:
                            if not ip_column_previous:
                                remove_column('IP ADDRESS')
                                ip_column_previous = True
                        elif ip_column and ip_column_previous:
                            add_column('IP ADDRESS')
                            ip_column_previous = False
                        if ip_column:
                            t_row.append(ip_address)
                        else:
                            field_names.remove('IP ADDRESS')
                        
                        # PORT
                        if not port_column:
                            if not port_column_previous:
                                remove_column('PORT')
                                port_column_previous = True
                        elif port_column and port_column_previous:
                            add_column('PORT')
                            port_column_previous = False
                        if port_column:
                            t_row.append(f"{port} {connection_type} {protocol}")
                        else:
                            field_names.remove('PORT')

                        # APPLICATION
                        if not application_column:
                            if not application_column_previous:
                                remove_column('APPLICATION‎‎')
                                application_column_previous = True
                        elif application_column and application_column_previous:
                            add_column('APPLICATION')
                            application_column_previous = False
                        if application_column:
                            t_row.append(application)
                        else:
                            field_names.remove('APPLICATION')
                            
                        # PID
                        if not pid_column:
                            if not pid_column_previous:
                                remove_column('PID‎‎')
                                pid_column_previous = True
                        elif pid_column and pid_column_previous:
                            add_column('PID')
                            pid_column_previous = False
                        if pid_column:
                            t_row.append(process_id)
                        else:
                            field_names.remove('PID')
                        
                        # RECEIVED
                        if not received_column:
                            if not received_column_previous:
                                remove_column('RECEIVED‎‎')
                                received_column_previous = True
                        elif received_column and received_column_previous:
                            add_column('RECEIVED')
                            received_column_previous = False
                        if received_column:
                            t_row.append(received_bytes)
                        else:
                            field_names.remove('RECEIVED')
                        
                        # SENT
                        if not sent_column:
                            if not sent_column_previous:
                                remove_column('SENT‎‎')
                                sent_column_previous = True
                        elif sent_column and sent_column_previous:
                            add_column('SENT')
                            sent_column_previous = False
                        if sent_column:
                            t_row.append(sent_bytes)
                        else:
                            field_names.remove('SENT')
                      
                        # CITY
                        if not city_column:
                            if not city_column_previous:
                                remove_column('CITY‎‎')
                                city_column_previous = True
                        elif city_column and city_column_previous:
                            add_column('CITY')
                            city_column_previous = False                           
                        if city_column:
                            t_row.append(city)
                        else:
                            field_names.remove('CITY')

                        # COUNTRY
                        if not country_column:
                            if not country_column_previous:
                                remove_column('COUNTRY‎‎')
                                country_column_previous = True
                        elif country_column and country_column_previous:
                            add_column('COUNTRY')
                            country_column_previous = False
                        if country_column:
                            t_row.append(country)
                        else:
                            field_names.remove('COUNTRY')

                        # ASN
                        if not asn_column:
                            if not asn_column_previous:
                                remove_column('ASN‎‎')
                                asn_column_previous = True
                        elif asn_column and asn_column_previous:
                            add_column('ASN')
                            asn_column_previous = False
                        if asn_column:
                            t_row.append(asn)
                        else:
                            field_names.remove('ASN')

                        # HOST
                        if not host_column:
                            if not host_column_previous:
                                remove_column('HOST‎‎')
                                host_column_previous = True
                        elif host_column and host_column_previous:
                            add_column('HOST')
                            host_column_previous = False
                        if host_column:
                            t_row.append(isp_host)
                        else:
                            field_names.remove('HOST')

                        # NIC
                        if not interface_column:
                            if not interface_column_previous:
                                remove_column('NIC‎‎')
                                interface_column_previous = True
                        elif interface_column and interface_column_previous:
                            add_column('NIC')
                            interface_column_previous = False
                        if interface_column:
                            t_row.append(interface)
                        else:
                            field_names.remove('NIC')

                        # USERNAME
                        if not user_column:
                            if not user_column_previous:
                                remove_column('USER‎‎')
                                user_column_previous = True
                        elif user_column and user_column_previous:
                            add_column('USER')
                            user_column_previous = False
                        if user_column:
                            t_row.append(username)
                        else:
                            field_names.remove('USER')

                        table.field_names = field_names
                        
                        # TABLE ADD ROW
                        
                        if t_row:
                            try:
                                t_rows.append(t_row)
                            except:
                                pass
                    
                    # SORT BY ACTIVE CONNECITON
                    
                    if not static_mode:
                        if active_connections:
                            try:
                                sent_index = field_names.index('SENT') if 'SENT' in field_names else None
                                received_index = field_names.index('RECEIVED') if 'RECEIVED' in field_names else None
                                
                                if sent_index is not None:
                                    t_rows.sort(key=lambda x: int(reverse_convert_size(x[sent_index])), reverse=True)

                                if received_index is not None:
                                    t_rows.sort(key=lambda x: int(reverse_convert_size(x[received_index])), reverse=True)

                                table.clear_rows()
                                row_count = len([table.add_row(row) for row in t_rows])
                            except:
                                pass

                    # SORT BY APPLICATION

                    if not static_mode:
                        if not active_connections:
                            try:
                                application_index = field_names.index('APPLICATION') if 'APPLICATION' in field_names else None
                                
                                if application_index is not None:
                                    t_rows.sort(key=lambda x: x[application_index])

                                table.clear_rows()
                                row_count = len([table.add_row(row) for row in t_rows])
                            except:
                                pass

            # SEND IP ADDRESSES TO CAPTURE

            if active_ip_addresses_csv:
                with open(active_ip_addresses_csv, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows([[ip_address, interface] for (ip_address, interface) in ip_addresses_dict])

            # STATIC MODE

            if static_mode:
                total_received_bytes = 0
                total_sent_bytes = 0
                rows = []
                t_rows = []

                static_ip_addresses = set(key[0] for key in data_dict.keys())

                for key, data in data_dict.items():
                    ip_address, port = key
                    connection_type = data['connection_type']
                    protocol = data['protocol']
                    application = data['application']
                    process_id = data['process_id']
                    received_bytes = data['received_bytes']
                    sent_bytes = data['sent_bytes']
                    city = data['city']
                    country = data['country']
                    asn = data['asn']
                    interface = data['interface']
                    username = data['username']

                    if enable_local_status:
                        ip_obj = ipaddress.ip_address(ip_address)
                        if ip_obj.is_private:
                            continue
                    else:
                        ip_obj = ipaddress.ip_address(ip_address)
                        if not ip_obj.is_private:
                            continue
                    
                    if not ip_address in hosts_ip_dict:
                        hosts_ip_dict.append(ip_address)
                    
                    isp_host = None
                    if enable_local_status:
                        isp_host = data_dict.get(key, {}).get('isp_host')
                        if isp_host is None or isp_host == '???':
                            isp_host = '???'
                            if ip_address in ip_isp_dict:
                                isp_host = ip_isp_dict[ip_address]
                                if isp_host:
                                    parts = isp_host.split('.')
                                    isp_host = '.'.join(parts[-2:])
                    else:
                        isp_host = ' '

                    if active_connections:
                        if sent_bytes == "0.00 B" and received_bytes == "0.00 B":
                            continue
                        if sent_bytes == "???" and received_bytes == "???":
                            continue

                    if not s_filter == "NULL":
                        if s_filter:
                            matched = False
                            for val in (ip_address, port, protocol, application, process_id, city, country, asn, isp_host):
                                if fuzz.ratio(s_filter.lower(), str(val).lower()) >= 85:
                                    matched = True
                            if not matched:
                                continue

                    if ip_address in kill_ip_dict:
                        continue

                    if port in kill_port_dict:
                        continue

                    if application in kill_app_dict:
                        continue

                    if process_id in kill_pid_dict:
                        continue

                    if application == "???":
                        continue

                    if not ip_address in total_byte_count_ip_dict:
                        if not sent_bytes == "???":
                            total_sent_bytes += int(reverse_convert_size(sent_bytes))
                        if not received_bytes == "???":
                            total_received_bytes += int(reverse_convert_size(received_bytes))
                        total_byte_count_ip_dict[ip_address] = True
                    
                    t_row = []
                    field_names = ['IP ADDRESS', 'PORT', 'APPLICATION', 'PID', 'SENT', 'RECEIVED', 'CITY', 'COUNTRY', 'ASN', 'HOST', 'NIC', 'USER']
                    
                    # IP ADDRESS
                    if not ip_column:
                        if not ip_column_previous:
                            remove_column('IP ADDRESS')
                            ip_column_previous = True
                    elif ip_column and ip_column_previous:
                        add_column('IP ADDRESS')
                        ip_column_previous = False
                    if ip_column:
                        t_row.append(ip_address)
                    else:
                        field_names.remove('IP ADDRESS')
                    
                    # PORT
                    if not port_column:
                        if not port_column_previous:
                            remove_column('PORT')
                            port_column_previous = True
                    elif port_column and port_column_previous:
                        add_column('PORT')
                        port_column_previous = False
                    if port_column:
                        t_row.append(f"{port} {connection_type} {protocol}")
                    else:
                        field_names.remove('PORT')

                    # APPLICATION
                    if not application_column:
                        if not application_column_previous:
                            remove_column('APPLICATION‎‎')
                            application_column_previous = True
                    elif application_column and application_column_previous:
                        add_column('APPLICATION')
                        application_column_previous = False
                    if application_column:
                        t_row.append(application)
                    else:
                        field_names.remove('APPLICATION')
                        
                    # PID
                    if not pid_column:
                        if not pid_column_previous:
                            remove_column('PID‎‎')
                            pid_column_previous = True
                    elif pid_column and pid_column_previous:
                        add_column('PID')
                        pid_column_previous = False
                    if pid_column:
                        t_row.append(process_id)
                    else:
                        field_names.remove('PID')
                    
                    # RECEIVED
                    if not received_column:
                        if not received_column_previous:
                            remove_column('RECEIVED‎‎')
                            received_column_previous = True
                    elif received_column and received_column_previous:
                        add_column('RECEIVED')
                        received_column_previous = False
                    if received_column:
                        t_row.append(received_bytes)
                    else:
                        field_names.remove('RECEIVED')
                    
                    # SENT
                    if not sent_column:
                        if not sent_column_previous:
                            remove_column('SENT‎‎')
                            sent_column_previous = True
                    elif sent_column and sent_column_previous:
                        add_column('SENT')
                        sent_column_previous = False
                    if sent_column:
                        t_row.append(sent_bytes)
                    else:
                        field_names.remove('SENT')
                  
                    # CITY
                    if not city_column:
                        if not city_column_previous:
                            remove_column('CITY‎‎')
                            city_column_previous = True
                    elif city_column and city_column_previous:
                        add_column('CITY')
                        city_column_previous = False                           
                    if city_column:
                        t_row.append(city)
                    else:
                        field_names.remove('CITY')

                    # COUNTRY
                    if not country_column:
                        if not country_column_previous:
                            remove_column('COUNTRY‎‎')
                            country_column_previous = True
                    elif country_column and country_column_previous:
                        add_column('COUNTRY')
                        country_column_previous = False
                    if country_column:
                        t_row.append(country)
                    else:
                        field_names.remove('COUNTRY')

                    # ASN
                    if not asn_column:
                        if not asn_column_previous:
                            remove_column('ASN‎‎')
                            asn_column_previous = True
                    elif asn_column and asn_column_previous:
                        add_column('ASN')
                        asn_column_previous = False
                    if asn_column:
                        t_row.append(asn)
                    else:
                        field_names.remove('ASN')

                    # HOST
                    if not host_column:
                        if not host_column_previous:
                            remove_column('HOST‎‎')
                            host_column_previous = True
                    elif host_column and host_column_previous:
                        add_column('HOST')
                        host_column_previous = False
                    if host_column:
                        t_row.append(isp_host)
                    else:
                        field_names.remove('HOST')

                    # NIC
                    if not interface_column:
                        if not interface_column_previous:
                            remove_column('NIC‎‎')
                            interface_column_previous = True
                    elif interface_column and interface_column_previous:
                        add_column('NIC')
                        interface_column_previous = False
                    if interface_column:
                        t_row.append(interface)
                    else:
                        field_names.remove('NIC')

                    # USERNAME
                    if not user_column:
                        if not user_column_previous:
                            remove_column('USER‎‎')
                            user_column_previous = True
                    elif user_column and user_column_previous:
                        add_column('USER')
                        user_column_previous = False
                    if user_column:
                        t_row.append(username)
                    else:
                        field_names.remove('USER')

                    table.field_names = field_names

                    # TABLE ADD ROW

                    if t_row:
                        try:
                            t_rows.append(t_row)
                        except:
                            pass
                
                # SORT BY ACTIVE CONNECITON
                
                if active_connections:
                    try:
                        sent_index = field_names.index('SENT') if 'SENT' in field_names else None
                        received_index = field_names.index('RECEIVED') if 'RECEIVED' in field_names else None
                        
                        if sent_index is not None:
                            t_rows.sort(key=lambda x: int(reverse_convert_size(x[sent_index])), reverse=True)

                        if received_index is not None:
                            t_rows.sort(key=lambda x: int(reverse_convert_size(x[received_index])), reverse=True)

                        table.clear_rows()
                        row_count = len([table.add_row(row) for row in t_rows])
                    except:
                        pass
                
                # SORT BY APPLICATION

                if not active_connections:
                    try:
                        application_index = field_names.index('APPLICATION') if 'APPLICATION' in field_names else None
                        
                        if application_index is not None:
                            t_rows.sort(key=lambda x: x[application_index])

                        table.clear_rows()
                        row_count = len([table.add_row(row) for row in t_rows])
                    except:
                        pass
            
            root.update_idletasks()
            table_widget.delete('1.0', tk.END)
            table.title = f"CONNECTIONS: {row_count}  +  SENT: {convert_size(total_received_bytes)}  +  RECEIVED: {convert_size(total_sent_bytes)}  +  UPTIME: {total_uptime}"

            # COLORIZE
            
            rows = table.get_string().split("\n")
            for i, row in enumerate(rows):
                if i % 2 != 0:
                    table_widget.insert(tk.END, row + "\n", "odd")
                else:
                    table_widget.insert(tk.END, row + "\n")
                table_widget.tag_configure("odd", background=bg_color, foreground=font_color_2, selectbackground="blue", selectforeground="white")
                table_widget.tag_configure('center', justify='center')
                table_widget.tag_add('center', f"{i+1}.0", f"{i+1}.end")
            
            # TABLE ERROR MESSAGES
            
            global slash_n_mod
            slasn_n_mod = None
            if row_count == 0:
                table_widget.configure(font=('Consolas', 20, 'bold'))
                slash_n_mod = True
                table_widget.config(state=tk.NORMAL)
                table.clear_rows()
                table_widget.delete('1.0', tk.END)
                table_widget.tag_configure('center', justify='center')
                      
                if not enable_local_status and active_connections:
                    if not s_filter == "NULL":
                        slash_n_count()
                        table_widget.insert(tk.END, f"{slash_n} # NO ACTIVE OR LOCAL CONNECTIONS FOUND #\n" + "'" + s_filter + "'", 'center')
                    else:
                        slash_n_count()
                        table_widget.insert(tk.END, f"{slash_n} # NO ACTIVE OR LOCAL CONNECTIONS # ", 'center')
                elif active_connections:
                    if not s_filter == "NULL":
                        slash_n_count()
                        table_widget.insert(tk.END, f"{slash_n} # NO ACTIVE CONNECTIONS FOUND #\n" + "'" + s_filter + "'", 'center')
                    else:
                        slash_n_count()
                        table_widget.insert(tk.END, f"{slash_n} # NO ACTIVE CONNECTIONS # ", 'center')
                elif not enable_local_status:
                    if not s_filter == "NULL":
                        slash_n_count()
                        table_widget.insert(tk.END, f"{slash_n} # NO LOCAL CONNECTIONS FOUND #\n" + "'" + s_filter + "'", 'center')
                    else:
                        slash_n_count()
                        table_widget.insert(tk.END, f"{slash_n} # NO LOCAL CONNECTIONS # ", 'center')
                elif not s_filter == "NULL":
                    slash_n_count()
                    table_widget.insert(tk.END, f"{slash_n} # NO CONNECTIONS FOUND #\n" + "'" + s_filter + "'", 'center')
                else:
                    slash_n_count()
                    table_widget.insert(tk.END, f"{slash_n} # NO CONNECTIONS # ", 'center')
            else:
                slash_n_mod = False
                table_widget.configure(font=('Consolas', root_font_size, 'bold'))

            table_widget.config(state=tk.DISABLED)
            #root.update()
            
            # UPTIME
            current_time = datetime.now().time()
            formatted_time = current_time.strftime("%H%M%S")
            with open(uptime_file, 'w') as file:
                file.write(formatted_time)
            
            # time.sleep variant
            pause_time = time.time()
            while time.time() - pause_time < 0.9:
                #table_widget.update()
                threading.Event().wait(0.001)
                root.update()
    
    except tk.TclError:
        pass

toggle_update()
root.mainloop() 
