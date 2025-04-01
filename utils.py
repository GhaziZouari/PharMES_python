import socket
import netifaces

# Function to get MAC address of the Raspberry Pi
def get_mac_address():
    interface = 'wlan0'  
    try:
        mac = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
        return mac
    except (ValueError, KeyError, IndexError):
        return "Unknown"

# Function to get IP address of the Raspberry Pi
def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror:
        return "Unknown"