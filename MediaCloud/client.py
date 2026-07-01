import tkinter as tk
from tkinter import filedialog
import requests
import os
import json
import threading
import webbrowser
import uuid

CONFIG_FILE = "config.json"
DEVICE_FILE = "device.json"

SAVE_DIR = "/storage/emulated/0/MediaCloud/Files"
os.makedirs(SAVE_DIR, exist_ok=True)


# ================= DEVICE ID =================
def load_device_id():
    if os.path.exists(DEVICE_FILE):
        return json.load(open(DEVICE_FILE))["id"]

    device_id = str(uuid.uuid4())
    json.dump({"id": device_id}, open(DEVICE_FILE, "w"))
    return device_id


# ================= CONFIG =================
def save_ip(ip):
    json.dump({"ip": ip}, open(CONFIG_FILE, "w"))

def load_ip():
    if os.path.exists(CONFIG_FILE):
        return json.load(open(CONFIG_FILE)).get("ip", "")
    return ""


# ================= APP =================
class ClientApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Media Cloud Client")
        self.root.geometry("520x650")

        self.ip = tk.StringVar(value=load_ip())
        self.device_id = load_device_id()

        # ===== TOP =====
        top = tk.Frame(root)
        top.pack(pady=10)

        tk.Label(top, text="Server IP:").pack(side=tk.LEFT)

        tk.Entry(top, textvariable=self.ip, width=30).pack(side=tk.LEFT)

        tk.Button(top, text="Connect", command=self.connect).pack(side=tk.LEFT)

        # ===== STATUS =====
        self.status = tk.Label(root, text="Ready", fg="blue")
        self.status.pack()

        # ===== FILE LIST =====
        self.files_box = tk.Frame(root)
        self.files_box.pack(fill=tk.BOTH, expand=True)

        # ===== BOTTOM =====
        bottom = tk.Frame(root)
        bottom.pack(pady=10)

        tk.Button(bottom, text="Upload", command=self.upload_file).pack(side=tk.LEFT)
        tk.Button(bottom, text="Refresh", command=self.load_files).pack(side=tk.LEFT)

    # ================= CONNECT =================
    def connect(self):
        ip = self.ip.get().strip()

        if "://" not in ip:
            ip = "http://" + ip

        if ":5000" not in ip:
            ip += ":5000"

        self.ip.set(ip)

        try:
            r = requests.get(ip + "/files", timeout=5)

            if r.status_code == 200:
                save_ip(ip)
                self.status.config(text="Connected ✔")
                self.load_files()
            else:
                self.status.config(text="Server error")

        except:
            self.status.config(text="Connection failed")

    # ================= LOAD FILES =================
    def load_files(self):

        def run():
            try:
                r = requests.get(self.ip.get() + "/files", timeout=5)
                data = r.json()
                self.update_ui(data)

            except:
                self.status.config(text="Load error")

        threading.Thread(target=run, daemon=True).start()

    # ================= UI (MOBILE FIXED) =================
    def update_ui(self, data):

        def draw():
            for w in self.files_box.winfo_children():
                w.destroy()

            for f in data:
                name = f["name"]

                # CARD
                card = tk.Frame(self.files_box, bg="#f2f2f2", pady=6)
                card.pack(fill=tk.X, padx=6, pady=6)

                # FILE NAME
                tk.Label(
                    card,
                    text=name,
                    bg="#f2f2f2",
                    anchor="w",
                    font=("Arial", 11, "bold")
                ).pack(fill=tk.X)

                # BUTTON ROW
                row = tk.Frame(card, bg="#f2f2f2")
                row.pack(fill=tk.X, pady=5)

                tk.Button(row, text="View",
                          width=10,
                          command=lambda n=name: self.view(n)).pack(side=tk.LEFT, expand=True, fill=tk.X)

                tk.Button(row, text="Import",
                          width=10,
                          command=lambda n=name: self.import_file(n)).pack(side=tk.LEFT, expand=True, fill=tk.X)

                # 🔴 DELETE (VISIBLE ALWAYS)
                tk.Button(row, text="DELETE",
                          width=10,
                          bg="red",
                          fg="white",
                          command=lambda n=name: self.delete(n)).pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.root.after(0, draw)

    # ================= VIEW =================
    def view(self, name):
        webbrowser.open(self.ip.get() + "/view/" + name)

    # ================= IMPORT =================
    def import_file(self, name):

        def run():
            try:
                url = self.ip.get() + "/file/" + name
                path = os.path.join(SAVE_DIR, name)

                r = requests.get(url, stream=True)

                with open(path, "wb") as f:
                    for chunk in r.iter_content(1024):
                        if chunk:
                            f.write(chunk)

                self.status.config(text="Imported ✔ " + name)

            except:
                self.status.config(text="Import error")

        threading.Thread(target=run, daemon=True).start()

    # ================= DELETE =================
    def delete(self, name):

        def run():
            try:
                url = self.ip.get() + "/delete/" + name
                requests.get(url, params={"owner_id": self.device_id})
                self.load_files()

            except:
                self.status.config(text="Delete error")

        threading.Thread(target=run, daemon=True).start()

    # ================= UPLOAD =================
    def upload_file(self):

        path = filedialog.askopenfilename()

        if not path:
            return

        def run():
            try:
                with open(path, "rb") as f:
                    requests.post(
                        self.ip.get() + "/upload",
                        files={"file": f},
                        data={"owner_id": self.device_id}
                    )

                self.status.config(text="Uploaded ✔")
                self.load_files()

            except:
                self.status.config(text="Upload error")

        threading.Thread(target=run, daemon=True).start()


# ================= RUN =================
root = tk.Tk()
app = ClientApp(root)
root.mainloop()