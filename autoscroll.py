import tkinter as tk
from tkinter import ttk
import time
import threading
import json
import os
def load_config():
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_config(geometry):
    with open("config.json", "w", encoding="utf-8") as f:
    # geometry 格式： "WxH+X+Y"
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump({"geometry": geometry}, f)

class TextScroller:
    def __init__(self, root):
        self.root = root
        self.root.title("None")
        self.root.configure(bg="#1f1f11")
        config = load_config()
        if config and "geometry" in config:
            self.root.geometry(config["geometry"])
            self.root.overrideredirect(True)
        else:
            self.root.geometry("800x100+100+100")  # 初始大小
            self.root.overrideredirect(False)     # 讓使用者可拖曳調整

        self.root.attributes("-topmost", True)   # 置頂顯示
        # self.root.geometry("1920x60+-1920+1010")  
        self.lines = self.load_text()
        self.index = 0
        self.is_paused = False
        self.dynamic_jump = None

        # ===== Style 設定進度條樣式與高度 =====
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor="#ffffff",
                        background="#000000",
                        thickness=3,
                        bordercolor="#000000",
                        lightcolor="#000000",
                        darkcolor="#000000")

        # ===== 按鈕區（最上方靠左） =====
        btn_frame = tk.Frame(root, bg="#1f1f11")
        btn_frame.pack(side=tk.TOP, anchor="w", pady=1, padx=1)

        self.toggle_btn = tk.Button(btn_frame, text="||", command=self.toggle,
                                    bg="#1f1f11", fg="white", font=("Arial", 10), bd=0)
        self.toggle_btn.pack(side=tk.LEFT)

        self.restart_btn = tk.Button(btn_frame, text="0", command=self.restart,
                                     bg="#1f1f11", fg="white", font=("Arial", 10), bd=0)
        self.restart_btn.pack(side=tk.LEFT, padx=1)

        # ===== 進度條（中間） =====
        self.progress = ttk.Progressbar(root, length=1920, maximum=len(self.lines),
                                        style="Custom.Horizontal.TProgressbar")
        self.progress.pack(side=tk.TOP, pady=1)
        self.progress.bind("<Button-1>", self.on_progress_click)

        # ===== 文字顯示區（最下方） =====
        self.label = tk.Label(root, text="", fg="white", bg="#1f1f11",
                              font=("Arial", 14), wraplength=1920, justify="left")
        self.label.pack(side=tk.TOP, pady=1, fill="x")

        # ===== 啟動滾動邏輯 =====
        threading.Thread(target=self.scroll_loop, daemon=True).start()

    def load_text(self):
        try:
            with open("text.txt", "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            return ["找不到 text.txt 檔案"]

        lines = [line.strip() for line in content.split("\n") if line.strip()]
        final = []
        for line in lines:
            for i in range(0, len(line), 95):
                final.append(line[i:i+95])
        return final

    def scroll_loop(self):
        while True:
            if not self.is_paused and self.index < len(self.lines):
                self.show_line()
                display_time = max(4, len(self.lines[self.index - 1]) * 0.15)
                time.sleep(display_time)
            else:
                time.sleep(0.2)

    def show_line(self):
        if self.index < len(self.lines):
            self.label.config(text=self.lines[self.index])
            self.progress["value"] = self.index + 1
            self.index += 1

    def toggle(self):
        self.is_paused = not self.is_paused
        self.toggle_btn.config(text="|>" if self.is_paused else "||")
        if self.is_paused:
            self.label.config(text="")
        else:
            self.show_line()

    def restart(self):
        self.index = 0
        self.progress["value"] = 0
        self.label.config(text="")
        self.is_paused = False
        self.toggle_btn.config(text="||")
        self.show_line()

    def on_progress_click(self, event):
        total_width = self.progress.winfo_width()
        click_x = event.x
        percentage = click_x / total_width
        self.dynamic_jump = int(percentage * len(self.lines))
        self.index = self.dynamic_jump
        self.label.config(text=self.lines[self.index])
        self.progress["value"] = self.index + 1
if __name__ == "__main__":
    def on_close():
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()
        geometry = f"{w}x{h}+{x}+{y}"
        save_config(geometry)
        root.destroy()

    root = tk.Tk()
    app = TextScroller(root)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
