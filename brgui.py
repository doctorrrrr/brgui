try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
except ImportError:
    print("Помилка: Модуль tkinter не знайдено. Переконайтесь, що він встановлений у вашій системі.")
    exit(1)

import json
import subprocess
import os

CLIENTS_FILE = "clients.json"

def load_clients():
    try:
        with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
            data = f.read()
            parsed_data = json.loads(data)
            if isinstance(parsed_data, list):
                return [client for client in parsed_data if "name" in client and "address" in client]
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Помилка читання JSON: {e}")
        return []
    return []

def save_clients():
    with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(clients, f, indent=4, ensure_ascii=False)
    update_listbox()

def add_client():
    name = simpledialog.askstring("Додати клієнта", "Введіть ім'я клієнта:")
    address = simpledialog.askstring("Додати клієнта", "Введіть IP або мережеве ім'я клієнта:")
    if name and address:
        clients.append({"name": name, "address": address})
        save_clients()

def delete_client():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        name_part = listbox.get(index).split(" (")[0]
        client_index = next((i for i, c in enumerate(clients) if c["name"] == name_part), None)
        if client_index is not None:
            del clients[client_index]
            save_clients()
        else:
            messagebox.showwarning("Помилка", "Не вдалося знайти клієнта у списку")
    else:
        messagebox.showwarning("Видалення", "Оберіть клієнта для видалення")

def edit_client():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        name_part = listbox.get(index).split(" (")[0]
        client_index = next((i for i, c in enumerate(clients) if c["name"] == name_part), None)
        if client_index is not None:
            client = clients[client_index]
            new_name = simpledialog.askstring("Редагувати клієнта", "Введіть нове ім'я:", initialvalue=client["name"])
            new_address = simpledialog.askstring("Редагувати клієнта", "Введіть новий IP або ім'я:", initialvalue=client["address"])
            if new_name and new_address:
                clients[client_index] = {"name": new_name, "address": new_address}
                save_clients()
                update_listbox()
                for i, c in enumerate(clients):
                    if c["name"] == new_name:
                        listbox.selection_set(i)
                        break
    else:
        messagebox.showwarning("Редагування", "Оберіть клієнта для редагування")

def connect_client():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        name_part = listbox.get(index).split(" (")[0]
        client = next((c for c in clients if c["name"] == name_part), None)
        if client:
            target = client.get("address", "")
            if not target:
                messagebox.showerror("Помилка", "Вибраний клієнт не має адреси")
                return
            brynhildr_path = os.path.join(os.getcwd(), "Brynhildr.exe")
            if os.path.exists(brynhildr_path):
                try:
                    subprocess.run([brynhildr_path, f"/ip:{target}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as e:
                    messagebox.showerror("Помилка", f"Помилка запуску Brynhildr: {e}")
            else:
                messagebox.showerror("Помилка", "Не знайдено Brynhildr.exe у поточній папці")

def update_listbox():
    listbox.delete(0, tk.END)
    for client in sorted(clients, key=lambda c: c["name"].lower()):
        listbox.insert(tk.END, f"{client['name']} ({client['address']})")

def search_clients(event=None):
    query = search_var.get().strip().lower()
    listbox.delete(0, tk.END)
    found_clients = [c for c in clients if query in c["name"].lower() or query in c["address"].lower()]
    for client in found_clients:
        listbox.insert(tk.END, f"{client['name']} ({client['address']})")

def connect_from_search(event):
    if listbox.size() > 0:
        listbox.selection_set(0)
        connect_client()

def on_listbox_double_click(event):
    connect_client()

root = tk.Tk()
root.title("Brynhildr Manager")

search_var = tk.StringVar()
search_entry = tk.Entry(root, textvariable=search_var)
search_entry.grid(row=0, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
search_entry.bind("<KeyRelease>", search_clients)
search_entry.bind("<Return>", connect_from_search)

clients = load_clients()

frame = tk.Frame(root)
frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

listbox = tk.Listbox(frame, width=50, height=20)
listbox.grid(row=0, column=0, sticky="nsew")
listbox.bind("<Double-Button-1>", on_listbox_double_click)

scrollbar = tk.Scrollbar(frame, command=listbox.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
listbox.config(yscrollcommand=scrollbar.set)

btn_add = tk.Button(root, text="Додати", command=add_client)
btn_add.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

btn_edit = tk.Button(root, text="Редагувати", command=edit_client)
btn_edit.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

btn_delete = tk.Button(root, text="Видалити", command=delete_client)
btn_delete.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

btn_connect = tk.Button(root, text="Підключитися", command=connect_client)
btn_connect.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

update_listbox()
root.mainloop()
