import socket
import nmap

# Global config vars
Conf = False
USER_NAME = "-"
mobile_en = False
teddy_en = False
mobile_addr = ""   # could be MAC or IP
teddy_mac = ""
IP_Address = ""
Teddy_ip = ""
DEFAULT_MODE = ""
GENDER = ""
gpt_en = ""
gpt_api = ""
lan_en=""
lan_ip=""

def get_local_ip():
    """Get the host’s LAN IP (e.g. 192.168.1.10)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()

def get_network_range():
    """Turn 192.168.1.10 into 192.168.1.0/24."""
    ip = get_local_ip()
    parts = ip.split('.')
    parts[3] = '0'
    return '.'.join(parts) + '/24'

def scan_wifi_network(network_range):
    """Ping‑scan the /24 and return list of {'IP':…, 'MAC':…}."""
    nm = nmap.PortScanner()
    nm.scan(hosts=network_range, arguments='-sn')
    devices = []
    for host in nm.all_hosts():
        mac = nm[host]['addresses'].get('mac', 'Unknown')
        devices.append({'IP': host, 'MAC': mac})
    return devices

def find_device_ip(devices, target_mac):
    """Lookup IP by MAC in the list."""
    for d in devices:
        if d['MAC'].lower() == target_mac.lower():
            return d['IP']
    return ""

def update_config():
    global Conf, USER_NAME, mobile_en, teddy_en, mobile_addr, teddy_mac
    global IP_Address, Teddy_ip, DEFAULT_MODE, GENDER, gpt_en, gpt_api,lan_en,lan_ip

    try:
        lines = open('User.txt').read().splitlines()
        # pull raw values
        USER_NAME   = lines[0].strip() if len(lines) > 0 else "-"
        mobile_addr = lines[1].strip() if len(lines) > 1 else ""
        DEFAULT_MODE= lines[2].strip() if len(lines) > 2 else ""
        GENDER      = lines[3].strip() if len(lines) > 3 else ""
        gpt_en      = lines[4].strip().lower() if len(lines) > 4 else ""
        gpt_api     = lines[5].strip() if len(lines) > 5 else ""
        mobile_en   = lines[6].strip().lower() == "true" if len(lines) > 6 else False
        teddy_en    = lines[7].strip().lower() == "true" if len(lines) > 7 else False
        teddy_mac   = lines[8].strip() 
        lan_en      = lines[9].strip() 
        lan_ip      = lines[10].strip() if len(lines) > 10 else ""
        # Prepare to scan if any MAC lookups are needed
        need_scan = any([
            mobile_en   and ':' in mobile_addr,
            teddy_en    and ':' in teddy_mac
        ])
        devices = []
        if need_scan:
            nr = get_network_range()
            devices = scan_wifi_network(nr)
            # first pass
            if mobile_en   and ':' in mobile_addr:   IP_Address = find_device_ip(devices, mobile_addr)
            if teddy_en    and ':' in teddy_mac:     Teddy_ip   = find_device_ip(devices, teddy_mac)

            # if either one is still missing, rescan once
            if (mobile_en   and ':' in mobile_addr   and not IP_Address) or \
               (teddy_en    and ':' in teddy_mac     and not Teddy_ip):
                print("Rescanning network…")
                devices = scan_wifi_network(nr)
                if mobile_en and ':' in mobile_addr:   IP_Address = find_device_ip(devices, mobile_addr)
                if teddy_en  and ':' in teddy_mac:     Teddy_ip   = find_device_ip(devices, teddy_mac)

        # If mobile was “given as IP” just accept it
        if mobile_en and ':' not in mobile_addr:
            IP_Address = mobile_addr

        # If teddy_mac is actually an IP for some reason
        if teddy_en and ':' not in teddy_mac and teddy_mac:
            Teddy_ip = teddy_mac

        # Report any that we still couldn’t find
        if mobile_en and not IP_Address:
            print(f"⚠️ Mobile enabled but IP not found for '{mobile_addr}'")
        if teddy_en and not Teddy_ip:
            print(f"⚠️ Teddy enabled but IP not found for MAC '{teddy_mac}'")

        # Debug print
        print("User Name:     ", USER_NAME)
        print("Mobile Enabled:", mobile_en, "→", IP_Address)
        print("Teddy Enabled: ", teddy_en, "→", Teddy_ip)
        print("Gender:        ", GENDER)
        print("Default Mode:  ", DEFAULT_MODE)
        print("GPT Enabled:   ", gpt_en, "API Key:", bool(gpt_api))
        print("Lan Enabled:   ",lan_en)
        print("Lan Enabled:   ",lan_ip)

    except Exception as e:
        Conf = True
        print("Error loading config:", e)

# initialize
# update_config()
# print (type(gpt_api))
