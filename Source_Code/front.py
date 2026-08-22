from tkinter import (
    Tk, Label, Entry, Button, StringVar, OptionMenu, messagebox, Canvas,
    Checkbutton, BooleanVar, Frame, Text, Scrollbar, RIGHT, LEFT, Y, BOTH, WORD
)
from tkinter.font import Font
import re, os, subprocess
from PIL import Image, ImageTk
# import main
import User as U
import Default as df
import time

getinfo = U.Conf
file_op = "User.txt"

# ------------------ Helper Functions ------------------
def add_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg="gray")
    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg="black")
    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="gray")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def is_valid_ip(ip):
    ip_pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    if ip_pattern.match(ip):
        return all(0 <= int(num) <= 255 for num in ip.split('.'))
    return False

def is_valid_mac(mac):
    mac_pattern = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
    return bool(mac_pattern.match(mac))

# ------------------ Toggle Functions ------------------
def toggle_mobile_widgets():
    if enable_mobile_var.get():
        mobile_address_type_widget.pack(anchor="w", padx=40, pady=5, before=save_button)
        mobile_address_entry_widget.pack(anchor="w", padx=40, fill="x", pady=5, before=save_button)
    else:
        mobile_address_type_widget.pack_forget()
        mobile_address_entry_widget.pack_forget()

def toggle_remote_widgets():
    if remote_enabled_var.get():
        remote_mac_entry_widget.pack(anchor="w", padx=40, fill="x", pady=5, before=save_button)
    else:
        remote_mac_entry_widget.pack_forget()

def toggle_gpt_api_widgets():
    if gpt_var.get():
        gpt_api_entry_widget.pack(anchor="w", padx=40, fill="x", pady=5, before=save_button)
    else:
        gpt_api_entry_widget.pack_forget()

def toggle_lan_widgets():
    if lan_enable_var.get():
        lan_ip_entry_widget.pack(anchor="w", padx=40, fill="x", pady=5, before=save_button)
    else:
        lan_ip_entry_widget.pack_forget()

# ------------------ Main Functions ------------------
def save_info():
    name            = name_var.get().strip()
    gpt_enabled     = gpt_var.get()
    gender          = gender_var.get()
    mode            = mode_var.get()
    gpt_api         = gpt_api_var.get().strip() if gpt_enabled else "Not Enabled"
    enable_mobile   = enable_mobile_var.get()
    remote_enabled  = remote_enabled_var.get()
    lan_enabled     = lan_enable_var.get()

    if not name:
        messagebox.showerror("Invalid Input", "Name cannot be empty.")
        return

    if not enable_mobile and not remote_enabled and not lan_enabled:
        messagebox.showerror("Invalid Input",
            "Please select at least one option: Enable Mobile, Enable Remote, or Enable LAN.")
        return

    # ---- Mobile ----
    if enable_mobile:
        address_type = address_type_var.get()
        address = address_var.get().strip()
        if address == "Enter mobile IP/MAC address":
            messagebox.showerror("Invalid Input", "Please enter a valid mobile address.")
            return
        if address_type == "IP Address":
            if not is_valid_ip(address):
                messagebox.showerror("Invalid Input", "Please enter a valid IP address.")
                return
        elif address_type == "MAC Address":
            if not is_valid_mac(address):
                messagebox.showerror("Invalid Input",
                    "Please enter a valid MAC address in format XX:XX:XX:XX:XX:XX.")
                return
        else:
            messagebox.showerror("Invalid Input", "Please select an address type.")
            return
    else:
        address_type, address = "Not Applicable", "Not Applicable"

    # ---- Remote ----
    if remote_enabled:
        remote_mac = remote_mac_var.get().strip()
        if remote_mac == "Enter remote MAC address":
            messagebox.showerror("Invalid Input", "Please enter a valid remote MAC address.")
            return
        if not is_valid_mac(remote_mac):
            messagebox.showerror("Invalid Input",
                "Please enter a valid remote MAC address in format XX:XX:XX:XX:XX:XX.")
            return
    else:
        remote_mac = "Not Applicable"

    # ---- LAN ----
    if lan_enabled:
        lan_ip = lan_ip_var.get().strip()
        if lan_ip == "Enter LAN IP address" or not lan_ip:
            messagebox.showerror("Invalid Input", "Please enter a valid LAN IP address.")
            return
        if not is_valid_ip(lan_ip):
            messagebox.showerror("Invalid Input", "Please enter a valid LAN IP address.")
            return
    else:
        lan_ip = "Not Enabled"

    # ---- Write file ----
    with open(file_op, "w") as file:
        file.write(f"{name}\n")
        file.write(f"{address}\n")
        file.write(f"{mode}\n")
        file.write(f"{gender}\n")
        file.write(f"{gpt_enabled}\n")
        file.write(f"{gpt_api}\n")
        file.write(f"{enable_mobile}\n")
        file.write(f"{remote_enabled}\n")
        file.write(f"{remote_mac}\n")
        file.write(f"{lan_enabled}\n")
        file.write(f"{lan_ip}\n")

    messagebox.showinfo("Success", "Information saved successfully!")
    go_to_second_page(
        name, address_type, address, gender, mode,
        enable_mobile, remote_enabled, remote_mac,
        lan_enabled, lan_ip
    )

def go_to_second_page(name, address_type, address, gender, mode,
                      enable_mobile, remote_enabled, remote_mac,
                      lan_enabled, lan_ip):
    for widget in app.winfo_children():
        widget.destroy()
    app.config(bg="#03045e")
    add_logo()

    right_frame = Canvas(app, bg="#e0f7fa", highlightthickness=0)
    right_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

    Label(right_frame, text="User Information", bg="#e0f7fa",
          font=("Arial", 18, "bold")).pack(pady=20)
    Label(right_frame, text=f"Name: {name}", bg="#e0f7fa",
          font=("Arial", 14)).pack(pady=10)

    if enable_mobile:
        Label(right_frame, text=f"Address Type: {address_type}",
              bg="#e0f7fa", font=("Arial", 14)).pack(pady=10)
        Label(right_frame, text=f"Address: {address}",
              bg="#e0f7fa", font=("Arial", 14)).pack(pady=10)
    else:
        Label(right_frame, text="Address: Not Applicable",
              bg="#e0f7fa", font=("Arial", 14)).pack(pady=10)

    Label(right_frame, text=f"Gender: {gender}", bg="#e0f7fa",
          font=("Arial", 14)).pack(pady=10)
    Label(right_frame, text=f"Default Mode: {mode}", bg="#e0f7fa",
          font=("Arial", 14)).pack(pady=10)
    Label(right_frame, text=f"GPT API Enabled: {gpt_var.get()}",
          bg="#e0f7fa", font=("Arial", 14)).pack(pady=10)

    if remote_enabled:
        Label(right_frame, text=f"Remote MAC: {remote_mac}",
              bg="#e0f7fa", font=("Arial", 14)).pack(pady=10)
    else:
        Label(right_frame, text="Remote MAC: Not Applicable",
              bg="#e0f7fa", font=("Arial", 14)).pack(pady=10)

    if lan_enabled:
        Label(right_frame, text=f"LAN IP: {lan_ip}",
              bg="#e0f7fa", font=("Arial", 14)).pack(pady=10)
    else:
        Label(right_frame, text="LAN: Not Enabled",
              bg="#e0f7fa", font=("Arial", 14)).pack(pady=10)

    subprocess.Popen(["python", r"E:\uni work\FYP\FYP_Code\WebCam\main.py"])

# ------------------ Terms of Service ------------------
def go_to_terms_page():
    for widget in app.winfo_children():
        widget.destroy()
    app.config(bg="#03045e")
    add_logo()

    right_frame = Frame(app, bg="#e0f7fa")
    right_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

    header_font = Font(family="Arial", size=18, weight="bold")
    Label(right_frame, text="Terms of Service",
          bg="#e0f7fa", font=header_font).pack(pady=(20, 10))

    text_frame = Frame(right_frame, bg="#e0f7fa")
    text_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    scrollbar = Scrollbar(text_frame, orient="vertical")
    scrollbar.pack(side=RIGHT, fill=Y)

    body_font = Font(family="Helvetica", size=12)
    heading_font = Font(family="Helvetica", size=12, weight="bold")

    terms_widget = Text(text_frame, wrap=WORD, yscrollcommand=scrollbar.set,
                        font=body_font, bg="white", fg="#333333",
                        bd=0, padx=10, pady=10)
    terms_widget.tag_configure("heading", font=heading_font)

    def insert_heading(text):
        terms_widget.insert("end", text + "\n", "heading")

    def insert_body(text):
        terms_widget.insert("end", text + "\n")

    # ---------------- FULL TERMS TEXT (unchanged) ----------------
    insert_body("Welcome to EyeMate! These Terms of Service (\"Terms\") govern your use of the EyeMate app and its services, which are designed to assist visually impaired students with text reading, obstacle detection, live guidance, mode switching, time-telling, and navigation. By using EyeMate, you agree to these Terms. If you do not agree, please do not use the app.")
    terms_widget.insert("end", "________________________________________\n\n")

    insert_heading("1. Safety Guidelines")
    insert_body("EyeMate is designed to assist visually impaired users, but it is not a replacement for professional mobility aids or emergency services. Please follow these safety guidelines:")
    insert_body("• Do not use EyeMate as a mobility aid: EyeMate is not a substitute for a white cane, guide dog, or human guide.")
    insert_body("• Avoid sharing sensitive information: Do not share personal, financial, or health-related information through the app.")
    terms_widget.insert("end", "\n")

    insert_heading("2. Summary of Terms")
    insert_body("By using EyeMate, you agree to:")
    insert_body("• Treat other users and the app with respect.")
    insert_body("• Use the app only for its intended purposes.")
    insert_body("• Not misuse the app for illegal or harmful activities.")
    insert_body("• Comply with all applicable laws and regulations.")
    insert_body("EyeMate reserves the right to modify or terminate your access to the app if you violate these Terms.")
    terms_widget.insert("end", "\n")

    insert_heading("3. Registration and Configuration")
    insert_body("To use EyeMate, you must first register and provide the following information:")
    insert_body("• Your name")
    insert_body("• Gender")
    insert_body("• Source of input (Mobile app, Remote, or Raspberry Pi)")
    insert_body("• IP address and/or MAC address")
    insert_body("This information is used to personalize your experience and enable app features.")
    terms_widget.insert("end", "\n")

    insert_heading("4. Ownership of Content")
    insert_body("You own any content you create or submit through EyeMate, such as text, images, or audio. However, by using the app, you grant EyeMate a license to use, store, and process your content to provide and improve the Services.")
    terms_widget.insert("end", "\n")

    insert_heading("5. Prohibited Activities")
    insert_body("You agree not to:")
    insert_body("• Use EyeMate for illegal or unauthorized purposes.")
    insert_body("• Share sensitive personal information (e.g., financial details, health information).")
    insert_body("• Misuse the app as a mobility aid or emergency service.")
    insert_body("• Reverse engineer, copy, or distribute the app without permission.")
    insert_body("• Harass, bully, or harm other users.")
    terms_widget.insert("end", "\n")

    insert_heading("6. Privacy Policy")
    insert_body("Your privacy is important to us. EyeMate collects and uses your information as described in our Privacy Policy. By using the app, you consent to the collection and use of your data.")
    terms_widget.insert("end", "\n")

    insert_heading("7. Disclaimer of Liability")
    insert_body("EyeMate is provided \"as is\" and \"as available.\" We do not guarantee that the app will always be error-free or uninterrupted. You agree that EyeMate is not responsible for:")
    insert_body("• Any harm or damage caused by your use of the app.")
    insert_body("• The accuracy of text reading, obstacle detection, or navigation features.")
    terms_widget.insert("end", "\n")

    insert_heading("8. Limitation of Liability")
    insert_body("To the fullest extent permitted by law, EyeMate and its affiliates will not be liable for any indirect, incidental, or consequential damages arising from your use of the app. Our total liability to you will not exceed the amount you paid to use the app, if any.")
    terms_widget.insert("end", "\n")

    insert_heading("9. Dispute Resolution")
    insert_body("If you have a dispute with EyeMate, you agree to first contact us at [insert contact email] to attempt an informal resolution. If unresolved, disputes will be resolved through binding arbitration in [insert location], governed by the rules of the American Arbitration Association.")
    terms_widget.insert("end", "\n")

    insert_heading("10. Changes to Terms")
    insert_body("EyeMate may update these Terms from time to time. We will notify you of significant changes via email or through the app. Your continued use of the app after changes take effect constitutes your acceptance of the updated Terms.")
    terms_widget.insert("end", "\n")

    insert_heading("11. Contact Us")
    insert_body("If you have questions about these Terms or the app, please contact us at:")
    insert_body("Email: Robixlo.com")
    terms_widget.insert("end", "\n")
    insert_body("By using EyeMate, you acknowledge that you have read, understood, and agreed to these Terms of Service. Thank you for choosing EyeMate to assist you!")

    terms_widget.config(state="disabled")
    terms_widget.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.config(command=terms_widget.yview)

    Button(right_frame, text="Back to Start", command=show_start_page,
           font=("Arial", 14), bg="#4CAF50", fg="white",
           padx=20, pady=10).pack(pady=20)

# ------------------ Start / Config Pages ------------------
def show_start_page():
    for widget in app.winfo_children():
        widget.destroy()
    app.config(bg="#f0f0f0")
    add_logo()

    right_frame = Canvas(app, bg="#f0f0f0", highlightthickness=0)
    right_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

    Label(right_frame, text="Welcome to EyeMate",
          font=("Arial", 24, "bold"), bg="#f0f0f0").place(relx=0.5, rely=0.4, anchor="center")

    if U.Conf is False:
        Button(right_frame, text="Start", command=start_application,
               font=("Arial", 14), bg="#4CAF50", fg="white",
               padx=20, pady=10).place(relx=0.5, rely=0.5, anchor="center")
        Button(right_frame, text="Reconfigure", command=go_back_to_form,
               font=("Arial", 14), bg="#f44336", fg="white",
               padx=20, pady=10).place(relx=0.5, rely=0.6, anchor="center")
    else:
        Button(right_frame, text="Configure", command=go_back_to_form,
               font=("Arial", 14), bg="#f44336", fg="white",
               padx=20, pady=10).place(relx=0.5, rely=0.6, anchor="center")

    Button(right_frame, text="Terms and Conditions", command=go_to_terms_page,
           font=("Arial", 14), bg="#FFA500", fg="white",
           padx=20, pady=10).place(relx=0.5, rely=0.7, anchor="center")

def start_application():
    if os.path.exists(file_op):
        with open(file_op, "r") as file:
            lines = [ln.strip() for ln in file.readlines()]
        while len(lines) < 11:
            lines.append("")
        name, address, mode, gender = lines[:4]
        gpt_enabled     = lines[4] == "True"
        gpt_api         = lines[5]
        enable_mobile   = lines[6] == "True"
        remote_enabled  = lines[7] == "True"
        remote_mac      = lines[8]
        lan_enabled     = lines[9] == "True"
        lan_ip          = lines[10]
        address_type = address_type_var.get() if enable_mobile else "Not Applicable"
        go_to_second_page(name, address_type, address, gender, mode,
                          enable_mobile, remote_enabled, remote_mac,
                          lan_enabled, lan_ip)
    else:
        go_back_to_form()

def add_logo():
    canvas = Canvas(app, bg="#e0f7fa", highlightthickness=0)
    canvas.place(relx=0, rely=0, relwidth=0.4, relheight=1)
    try:
        image = Image.open("logo.png")
        resized_image = image.resize((800, 800))
        logo = ImageTk.PhotoImage(resized_image)
        logo_label = Label(canvas, image=logo, bg="#e0f7fa")
        logo_label.image = logo
        logo_label.place(relx=0.5, rely=0.5, anchor="center")
    except:
        canvas.create_text(200, 300, text="Logo Not Found", fill="red",
                           font=("Arial", 14, "bold"))

def go_back_to_form():
    for widget in app.winfo_children():
        widget.destroy()
    app.config(bg="#f0f0f0")
    add_logo()

    name_var.set("")
    address_var.set("")
    address_type_var.set("Select Address Type")
    gender_var.set("Select Gender")
    mode_var.set("Select Mode")
    gpt_var.set(False)
    gpt_api_var.set("")
    enable_mobile_var.set(False)
    remote_enabled_var.set(False)
    remote_mac_var.set("")
    lan_enable_var.set(False)
    lan_ip_var.set("")

    right_frame = Canvas(app, bg="#f0f0f0", highlightthickness=0)
    right_frame.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

    Label(right_frame, text="User Configuration", bg="#f0f0f0",
          font=("Arial", 18, "bold")).pack(pady=20)

    Label(right_frame, text="Name:", bg="#f0f0f0",
          font=("Arial", 14)).pack(anchor="w", padx=40)
    Entry(right_frame, textvariable=name_var,
          font=("Arial", 14)).pack(anchor="w", padx=40, fill="x", pady=5)

    checkbox_frame = Frame(right_frame, bg="#f0f0f0")
    checkbox_frame.pack(anchor="w", padx=40, pady=5, fill="x")

    Checkbutton(checkbox_frame, text="Enable Mobile", variable=enable_mobile_var,
                bg="#f0f0f0", font=("Arial", 14),
                command=toggle_mobile_widgets).pack(side="left", padx=5)
    Checkbutton(checkbox_frame, text="Enable Remote", variable=remote_enabled_var,
                bg="#f0f0f0", font=("Arial", 14),
                command=toggle_remote_widgets).pack(side="left", padx=5)
    Checkbutton(checkbox_frame, text="Enable GPT API", variable=gpt_var,
                bg="#f0f0f0", font=("Arial", 14),
                command=toggle_gpt_api_widgets).pack(side="left", padx=5)
    Checkbutton(checkbox_frame, text="Enable LAN", variable=lan_enable_var,
                bg="#f0f0f0", font=("Arial", 14),
                command=toggle_lan_widgets).pack(side="left", padx=5)

    OptionMenu(right_frame, gender_var, "Male", "Female", "Other").pack(
        anchor="w", padx=40, pady=5, fill="x")
    OptionMenu(right_frame, mode_var, "Mobile", "Desktop").pack(
        anchor="w", padx=40, pady=5, fill="x")

    global mobile_address_type_widget, mobile_address_entry_widget
    global remote_mac_entry_widget, gpt_api_entry_widget, lan_ip_entry_widget
    global save_button

    mobile_address_type_widget = OptionMenu(
        right_frame, address_type_var, "MAC Address", "IP Address")
    mobile_address_entry_widget = Entry(
        right_frame, textvariable=address_var, font=("Arial", 14))
    add_placeholder(mobile_address_entry_widget, "Enter mobile IP/MAC address")

    remote_mac_entry_widget = Entry(
        right_frame, textvariable=remote_mac_var, font=("Arial", 14))
    add_placeholder(remote_mac_entry_widget, "Enter remote MAC address")

    gpt_api_entry_widget = Entry(
        right_frame, textvariable=gpt_api_var, font=("Arial", 14))
    add_placeholder(gpt_api_entry_widget, "Enter GPT API Key")

    lan_ip_entry_widget = Entry(
        right_frame, textvariable=lan_ip_var, font=("Arial", 14))
    add_placeholder(lan_ip_entry_widget, "Enter LAN IP address")

    save_button = Button(right_frame, text="Save", command=save_info,
                         font=("Arial", 14), bg="#4CAF50", fg="white",
                         padx=20, pady=10)
    save_button.pack(pady=20)

# ------------------ App Init ------------------
app = Tk()
app.title("EyeMate")
app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}")

name_var          = StringVar(app)
address_var       = StringVar(app)
address_type_var  = StringVar(app)
gender_var        = StringVar(app)
mode_var          = StringVar(app)
gpt_var           = BooleanVar(app)
gpt_api_var       = StringVar(app)
enable_mobile_var = BooleanVar(app)
remote_enabled_var= BooleanVar(app)
remote_mac_var    = StringVar(app)
lan_enable_var    = BooleanVar(app)
lan_ip_var        = StringVar(app)

show_start_page()
app.mainloop()
