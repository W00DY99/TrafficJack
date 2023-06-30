import subprocess
import tempfile
import time
import threading
import socket
import csv
import os
import datetime
import logging
from scapy.all import sniff, conf
global uptime_file
data_usage = {}
ip_addresses = []
ip_addresses_csv = os.path.join(tempfile.gettempdir(), 'active_ip_addresses.csv')
reset_file = os.path.join(tempfile.gettempdir(), 'reset_trafficjack.txt')
data_lock = threading.Lock()

def reset():
    os.remove(reset_file)
    global data_usage, ip_addresses
    data_usage = {}
    ip_addresses = []
    data_lock = threading.Lock()

def capture_data(ip_address, interface):
    try:
        def packet_callback(packet):
            global data_usage, data_lock

            with data_lock:
                if packet.haslayer("IP"):
                    if packet["IP"].dst == ip_address:
                        data_usage[ip_address]["received_bytes"] += len(packet.payload)
                    if packet["IP"].src == ip_address:
                        data_usage[ip_address]["sent_bytes"] += len(packet.payload)
                elif packet.haslayer("IPv6"):
                    if packet["IPv6"].dst == ip_address:
                        data_usage[ip_address]["received_bytes"] += len(packet.payload)
                    if packet["IPv6"].src == ip_address:
                        data_usage[ip_address]["sent_bytes"] += len(packet.payload)
        
        sniff(filter=f"host {ip_address}", prn=packet_callback, iface=interface, store=False)
    except:
        pass

def send_data_usage(data_usage):
    try:
        with data_lock:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', 54321))
                s.sendall(str(data_usage).encode())
    except:
        pass

def display_data_usage():
    while True:
        send_data_usage(data_usage)
        update_list()
        if os.path.exists(reset_file):
            reset()
        time.sleep(0.2)

def update_list():
    with open(ip_addresses_csv, 'r') as csvfile:
        reader = csv.reader(csvfile)
        new_ip_addresses = []
        for row in reader:
            if len(row) >= 2:
                ip_address = row[0]
                interface = row[1]
                new_ip_addresses.append(ip_address)
                if ip_address not in data_usage:
                    data_usage[ip_address] = {"sent_bytes": 0, "received_bytes": 0}
                    t = threading.Thread(target=capture_data, args=(ip_address, interface))
                    t.start()

def finish():
    try:
        update_list()
        capture_threads = []
        for ip in ip_addresses:
            t = threading.Thread(target=capture_data, args=(ip,))
            t.start()
            capture_threads.append(t)

        display_thread = threading.Thread(target=display_data_usage)
        display_thread.start()

        for t in capture_threads:
            t.join()

        display_thread.join()

    except Exception as e:
        logging.error(f"Error in finish: {str(e)}")

if __name__ == "__main__":
    finish()
