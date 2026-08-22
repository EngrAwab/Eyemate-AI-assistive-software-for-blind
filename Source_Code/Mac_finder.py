import tkinter as tk
from tkinter import messagebox
import nmap
import random
import threading

class EyeMateMACScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EyeMate MAC Scanner")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Background canvas for animation
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.pack(fill='both', expand=True)
        self.root.update_idletasks()
        self.draw_gradient("#FF7F50", "#1E90FF")  # Coral to DodgerBlue gradient

        # Initialize cube animations after resize
        self.cubes = []
        self.root.after(100, self._init_cubes)

        # Panel for widgets
        self.panel = tk.Frame(self.root, bg="#FFFFFF", bd=3, relief='ridge')
        self.panel.place(relx=0.5, rely=0.5, anchor='center', width=450, height=250)

        # Header
        header = tk.Label(self.panel, text="EyeMate MAC Scanner", font=("Impact", 24), bg="#FFFFFF", fg="#333333")
        header.pack(pady=(10, 5))

        # Entry and scan button
        entry_frame = tk.Frame(self.panel, bg="#FFFFFF")
        entry_frame.pack(pady=15)
        tk.Label(entry_frame, text="IP Address:", font=("Helvetica", 12), bg="#FFFFFF").pack(side='left')
        self.ip_entry = tk.Entry(entry_frame, font=("Consolas", 14), fg="#1E90FF", bd=2, relief='groove')
        self.ip_entry.pack(side='left', padx=(5,10), ipady=3)
        self.ip_entry.insert(0, "192.168.1.1")

        self.scan_button = tk.Button(
            entry_frame, text="🔍 Scan MAC", font=("Helvetica", 12, 'bold'),
            bg="#32CD32", fg="#FFFFFF", activebackground="#228B22",
            activeforeground="#FFFFFF", bd=0, padx=20, pady=5,
            command=self.scan_mac_threaded
        )
        self.scan_button.pack(side='left')
        self.scan_button.bind("<Enter>", lambda e: self.scan_button.config(bg="#2E8B57"))
        self.scan_button.bind("<Leave>", lambda e: self.scan_button.config(bg="#32CD32"))

        # Result display
        self.result_label = tk.Label(self.panel, text="MAC Address: ", font=("Verdana", 14),
                                     bg="#FFFFFF", fg="#8B0000")
        self.result_label.pack(pady=(10,0))

    def draw_gradient(self, start_color, end_color):
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        r1, g1, b1 = hex_to_rgb(start_color)
        r2, g2, b2 = hex_to_rgb(end_color)
        height = self.root.winfo_height()
        width = self.root.winfo_width()
        for i in range(height):
            ratio = i / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.bg_canvas.create_line(0, i, width, i, fill=color)

    def _init_cubes(self):
        self._create_cubes(20)
        self._animate_cubes()

    def _create_cubes(self, count):
        self.bg_canvas.update_idletasks()
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        for _ in range(count):
            size = random.randint(20, 50)
            max_x = max(w - size, 0)
            max_y = max(h - size, 0)
            x = random.randint(0, max_x)
            y = random.randint(0, max_y)
            dx = random.choice([-1,1]) * random.uniform(0.5, 1.5)
            dy = random.choice([-1,1]) * random.uniform(0.5, 1.5)
            color = random.choice(["#FFFFFF", "#E0E0E0", "#C0C0C0"])
            cube_id = self.bg_canvas.create_rectangle(x, y, x+size, y+size, outline=color)
            self.cubes.append({'id': cube_id, 'dx': dx, 'dy': dy})

    def _animate_cubes(self):
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        for cube in self.cubes:
            self.bg_canvas.move(cube['id'], cube['dx'], cube['dy'])
            x1, y1, x2, y2 = self.bg_canvas.coords(cube['id'])
            if x1 < 0 or x2 > w:
                cube['dx'] *= -1
            if y1 < 0 or y2 > h:
                cube['dy'] *= -1
        self.root.after(50, self._animate_cubes)

    def scan_mac_threaded(self):
        target = self.ip_entry.get().strip()
        if not target:
            messagebox.showwarning("Input Error", "Please enter a valid IP address.")
            return

        # Disable button and show scanning text
        self.scan_button.config(state='disabled', text='Scanning...')
        threading.Thread(target=self._perform_scan, args=(target,), daemon=True).start()

    def _perform_scan(self, target):
        mac_address = None
        nm = nmap.PortScanner()
        for _ in range(3):
            nm.scan(hosts=target, arguments='-sn')
            if target in nm.all_hosts():
                mac_address = nm[target]['addresses'].get('mac', 'Unknown')
                break
        result = mac_address if mac_address else "No MAC address found."
        # Update UI back on the main thread
        self.root.after(0, lambda: self._update_result(result))

    def _update_result(self, result):
        self.result_label.config(text=f"MAC Address: {result}")
        self.scan_button.config(state='normal', text='🔍 Scan MAC')

if __name__ == '__main__':
    root = tk.Tk()
    app = EyeMateMACScannerApp(root)
    root.mainloop()
