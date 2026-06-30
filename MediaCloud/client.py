import requests
import os
import json
import threading

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


CONFIG = "config.json"


# ---------------- IP ----------------
def load_ip():
    if os.path.exists(CONFIG):
        return json.load(open(CONFIG)).get("ip", "")
    return ""

def save_ip(ip):
    json.dump({"ip": ip}, open(CONFIG, "w"))


# ---------------- TYPE ----------------
def get_type(name):
    n = name.lower()

    if n.endswith((".mp4", ".mkv", ".avi")):
        return "VIDEO"
    elif n.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return "IMAGE"
    elif n.endswith(".gif"):
        return "GIF"
    elif n.endswith((".txt", ".py", ".js", ".json")):
        return "CODE"
    elif n.endswith(".apk"):
        return "APK"
    else:
        return "FILE"


# ---------------- IP SCREEN ----------------
class IPScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        box = BoxLayout(orientation="vertical")

        self.ip = TextInput(
            text=load_ip().replace("http://", "").replace(":5000", ""),
            hint_text="Server IP",
            size_hint_y=None,
            height=50
        )

        box.add_widget(self.ip)

        btn = Button(text="CONNECT", size_hint_y=None, height=50)
        btn.bind(on_press=self.connect)

        box.add_widget(btn)

        self.status = Label(text="")
        box.add_widget(self.status)

        self.add_widget(box)

    def connect(self, *args):
        ip = self.ip.text.strip()

        if "://" not in ip:
            ip = "http://" + ip

        if ":5000" not in ip:
            ip += ":5000"

        try:
            r = requests.get(ip + "/files", timeout=4)

            if r.status_code == 200:
                save_ip(ip)
                self.manager.current = "main"
            else:
                self.status.text = "Server Error"

        except:
            self.status.text = "Connection Failed"


# ---------------- MAIN ----------------
class MainScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical")

        top = BoxLayout(size_hint_y=None, height=50)

        b1 = Button(text="REFRESH")
        b2 = Button(text="UPLOAD")
        b3 = Button(text="BACK")

        b1.bind(on_press=self.load)
        b2.bind(on_press=self.upload)
        b3.bind(on_press=self.back)

        top.add_widget(b1)
        top.add_widget(b2)
        top.add_widget(b3)

        root.add_widget(top)

        self.status = Label(text="Ready", size_hint_y=None, height=40)
        root.add_widget(self.status)

        self.scroll = ScrollView()
        self.list = GridLayout(cols=1, size_hint_y=None)
        self.list.bind(minimum_height=self.list.setter("height"))

        self.scroll.add_widget(self.list)
        root.add_widget(self.scroll)

        self.add_widget(root)

    # ---------------- LOAD ----------------
    def load(self, *args):

        self.list.clear_widgets()

        try:
            data = requests.get(load_ip() + "/files").json()
        except:
            self.status.text = "Server Error"
            return

        for f in data:

            fid = f["id"]
            name = f["name"]
            t = get_type(name)

            row = BoxLayout(size_hint_y=None, height=55)

            row.add_widget(Label(text=f"{name}\n[{t}]", size_hint_x=0.6))

            actions = BoxLayout(size_hint_x=0.4)

            btn_view = Button(text="View", font_size=11)
            btn_dl = Button(text="DL", font_size=11)
            btn_del = Button(text="Del", font_size=11)

            btn_view.bind(on_press=lambda x, i=fid: self.preview(i))
            btn_dl.bind(on_press=lambda x, i=fid: self.download(i))
            btn_del.bind(on_press=lambda x, i=fid: self.delete(i))

            actions.add_widget(btn_view)
            actions.add_widget(btn_dl)
            actions.add_widget(btn_del)

            row.add_widget(actions)
            self.list.add_widget(row)

    # ---------------- PREVIEW ----------------
    def preview(self, fid):
        url = load_ip() + "/download/" + fid
        import webbrowser
        webbrowser.open(url)

    # ---------------- DOWNLOAD ----------------
    def download(self, fid):

        def run():
            try:
                self.status.text = "Downloading..."

                url = load_ip() + "/download/" + fid
                name = fid.split("_", 1)[-1]
                path = "/storage/emulated/0/Download/" + name

                r = requests.get(url, stream=True)

                with open(path, "wb") as f:
                    for c in r.iter_content(1024):
                        if c:
                            f.write(c)

                self.status.text = "Downloaded"

                # 🔥 زر فتح الملف بعد التحميل
                self.add_open_button(path)

            except:
                self.status.text = "Download Failed"

        threading.Thread(target=run).start()

    # ---------------- OPEN FILE BUTTON ----------------
    def add_open_button(self, path):

        def open_file(_):
            import os
            os.system(f"am start -a android.intent.action.VIEW -d file://{path}")

        btn = Button(
            text="OPEN FILE",
            size_hint_y=None,
            height=50
        )

        btn.bind(on_press=open_file)

        self.list.add_widget(btn)

    # ---------------- DELETE ----------------
    def delete(self, fid):
        try:
            requests.post(load_ip() + "/delete/" + fid)
            self.load()
        except:
            self.status.text = "Delete Failed"

    # ---------------- UPLOAD ----------------
    def upload(self, *args):

        chooser = FileChooserListView(path="/storage/emulated/0")

        box = BoxLayout(orientation="vertical")
        box.add_widget(chooser)

        btn = Button(text="UPLOAD", size_hint_y=None, height=50)
        box.add_widget(btn)

        popup = Popup(title="Upload", content=box, size_hint=(0.9, 0.9))

        def send(_):
            if chooser.selection:
                path = chooser.selection[0]
                try:
                    with open(path, "rb") as f:
                        requests.post(load_ip() + "/upload", files={"file": f})
                    self.load()
                except:
                    self.status.text = "Upload Failed"

        btn.bind(on_press=send)
        popup.open()

    def back(self, *args):
        self.manager.current = "ip"


# ---------------- APP ----------------
class AppMain(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(IPScreen(name="ip"))
        sm.add_widget(MainScreen(name="main"))
        return sm


AppMain().run()