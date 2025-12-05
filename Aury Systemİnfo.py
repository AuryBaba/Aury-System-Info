
import ctypes
import matplotlib
matplotlib.use("TkAgg")  
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  
except:
    pass


import ttkbootstrap as tb
from ttkbootstrap.constants import *
import psutil
import platform
import socket
import datetime
import os
import subprocess
import threading
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


if sys.platform == "win32":
    try:
        import wmi
        c = wmi.WMI()
    except:
        c = None


def get_os_info():
    try:
        if sys.platform == "win32" and c:
            os_info = c.Win32_OperatingSystem()[0]
            return f"{os_info.Caption} {os_info.Version} Build {os_info.BuildNumber}"
        else:
            uname = platform.uname()
            return f"{uname.system} {uname.release} ({uname.version})"
    except:
        return platform.platform()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Bulunamadı"

def get_public_ip():
    try:
        import requests
        return requests.get("https://api.ipify.org").text
    except:
        return "Bulunamadı"

def get_system_info():
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot
    return {
        "OS": get_os_info(),
        "Hostname": socket.gethostname(),
        "Local IP": get_local_ip(),
        "Public IP": get_public_ip(),
        "User": os.getlogin(),
        "Uptime": str(uptime).split(".")[0],
        "CPU": platform.processor(),
    }


def get_cpu_info():
    freq = psutil.cpu_freq()
    usage = psutil.cpu_percent(interval=0.1)
    return {"Usage": usage, "Freq": freq.current if freq else 0,
            "Physical": psutil.cpu_count(logical=False),
            "Logical": psutil.cpu_count(logical=True)}

def get_ram_info():
    r = psutil.virtual_memory()
    return {"Total": r.total / (1024**3),
            "Used": r.used / (1024**3),
            "Free": r.available / (1024**3),
            "Percent": r.percent}

def get_disk_info():
    d = psutil.disk_usage("C:\\") if sys.platform=="win32" else psutil.disk_usage("/")
    return {"Total": d.total / (1024**3),
            "Used": d.used / (1024**3),
            "Free": d.free / (1024**3),
            "Percent": d.percent}

def get_network_info():
    s = psutil.net_io_counters()
    return {"Upload": s.bytes_sent / (1024**2),
            "Download": s.bytes_recv / (1024**2)}


def get_wifi_signal():
    if sys.platform=="win32":
        try:
            result = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
            for line in result.split("\n"):
                if "Signal" in line:
                    return line.split(":")[1].strip()
            return "Bulunamadı"
        except:
            return "Bulunamadı"
    else:
        return "Sadece Windows destekli"


def ping_test(host="8.8.8.8"):
    try:
        output = subprocess.run(f"ping -n 4 {host}" if sys.platform=="win32" else f"ping -c 4 {host}",
                                capture_output=True, text=True, shell=True)
        return output.stdout
    except:
        return "Ping testi başarısız."

def speed_test_thread(result_widget):
    def run_test():
        result_widget.delete("1.0", "end")
        result_widget.insert("end", "Speedtest başlatıldı, lütfen bekleyin...\n")
        try:
            output = subprocess.check_output("speedtest-cli --simple", shell=True, text=True)
            result_widget.insert("end", output)
        except Exception as e:
            result_widget.insert("end", f"Speedtest başarısız: {e}")
    threading.Thread(target=run_test, daemon=True).start()


app = tb.Window("System Control Center AurySoftWare© ", themename="cyborg")
app.geometry("1100x850")

notebook = tb.Notebook(app, bootstyle="dark", padding=15)
notebook.pack(fill=BOTH, expand=True, padx=20, pady=20)

tabs = {
    "Sistem": tb.Frame(notebook, padding=20),
    "CPU/RAM": tb.Frame(notebook, padding=20),
    "Disk": tb.Frame(notebook, padding=20),
    "Ağ & WiFi": tb.Frame(notebook, padding=20),
}

for name, tab in tabs.items():
    notebook.add(tab, text=name)


def create_card(parent, title, content=""):
    frame = tb.Frame(parent, padding=15, bootstyle="info")
    label_title = tb.Label(frame, text=title, font=("Segoe UI", 14, "bold"))
    label_title.pack(anchor=W)
    label_content = tb.Label(frame, text=content, font=("Segoe UI", 11), justify=LEFT)
    label_content.pack(anchor=W)
    frame.pack(fill=X, pady=10)
    return label_content

sys_card = create_card(tabs["Sistem"], "Sistem Bilgileri")
cpu_card = create_card(tabs["CPU/RAM"], "CPU Bilgileri")
cpu_bar = tb.Progressbar(tabs["CPU/RAM"], maximum=100, bootstyle="success")
cpu_bar.pack(fill=X, pady=5)
ram_card = create_card(tabs["CPU/RAM"], "RAM Bilgileri")
ram_bar = tb.Progressbar(tabs["CPU/RAM"], maximum=100, bootstyle="info")
ram_bar.pack(fill=X, pady=5)


fig, ax = plt.subplots(figsize=(5,2))
canvas = FigureCanvasTkAgg(fig, master=tabs["CPU/RAM"])
canvas.get_tk_widget().pack(pady=10, fill=X)
cpu_history = []
ram_history = []

disk_card = create_card(tabs["Disk"], "Disk Bilgileri")
disk_bar = tb.Progressbar(tabs["Disk"], maximum=100, bootstyle="warning")
disk_bar.pack(fill=X, pady=5)

net_card = create_card(tabs["Ağ & WiFi"], "Ağ Bilgileri")
wifi_card = create_card(tabs["Ağ & WiFi"], "WiFi Sinyal Gücü")
internet_text = tb.Text(tabs["Ağ & WiFi"], height=12)
internet_text.pack(fill=BOTH, expand=True, pady=10)
ping_btn = tb.Button(tabs["Ağ & WiFi"], text="Ping Testi", bootstyle="info",
                     command=lambda: internet_text.delete("1.0", "end") or internet_text.insert("end", ping_test()))
ping_btn.pack(pady=5)
speed_btn = tb.Button(tabs["Ağ & WiFi"], text="Speedtest", bootstyle="success",
                      command=lambda: speed_test_thread(internet_text))
speed_btn.pack(pady=5)


def update_all():
    s = get_system_info()
    sys_card.config(text=(
        f"OS: {s['OS']}\nHostname: {s['Hostname']}\nLocal IP: {s['Local IP']}\nPublic IP: {s['Public IP']}\nUser: {s['User']}\nUptime: {s['Uptime']}\nCPU: {s['CPU']}"
    ))

    c = get_cpu_info()
    cpu_card.config(text=f"Usage: %{c['Usage']}\nFreq: {c['Freq']:.0f} MHz\nCores: {c['Physical']} / Logical: {c['Logical']}")
    cpu_bar["value"] = c["Usage"]

    r = get_ram_info()
    ram_card.config(text=f"Total: {r['Total']:.2f} GB Used: {r['Used']:.2f} GB Free: {r['Free']:.2f} GB\nPercent: %{r['Percent']}")
    ram_bar["value"] = r["Percent"]

    d = get_disk_info()
    disk_card.config(text=f"Total: {d['Total']:.2f} GB Used: {d['Used']:.2f} GB Free: {d['Free']:.2f} GB\nPercent: %{d['Percent']}")
    disk_bar["value"] = d["Percent"]

    n = get_network_info()
    net_card.config(text=f"Upload: {n['Upload']:.2f} MB Download: {n['Download']:.2f} MB")
    wifi_card.config(text=f"{get_wifi_signal()}")

    cpu_history.append(c["Usage"])
    ram_history.append(r["Percent"])
    if len(cpu_history) > 50:
        cpu_history.pop(0)
        ram_history.pop(0)
    ax.clear()
    ax.plot(cpu_history, label="CPU %", color="lime")
    ax.plot(ram_history, label="RAM %", color="cyan")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right")
    canvas.draw()

    app.after(2000, update_all)

update_all()
app.mainloop()
