import os
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog


DATA_FILE = "products.txt"


class InventoryApp:

  def __init__(self, root):
    self.root = root
    self.root.title(
        "ระบบจัดการข้อมูลสินค้าในคลัง"
    )
    self.root.geometry("800x600")

    self.inventory = self.load_data_from_file()

    # ----- ค้นหาสินค้า -----
    search_frame = tk.LabelFrame(self.root, text="ค้นหาสินค้า", padx=10, pady=10)
    search_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(search_frame, text="ชื่อสินค้า:").pack(side="left", padx=5)
    self.search_var = tk.StringVar()
    self.search_var.trace_add("write", self.search_product)
    tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(
        side="left", padx=5
    )

    # ----- ตารางแสดงผล -----
    table_frame = tk.Frame(self.root)
    table_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("name", "price", "stock")
    self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    self.tree.heading("name", text="ชื่อสินค้า")
    self.tree.heading("price", text="ราคา (บาท)")
    self.tree.heading("stock", text="จำนวนคงเหลือในคลัง")

    self.tree.column("name", width=250, anchor="w")
    self.tree.column("price", width=150, anchor="e")
    self.tree.column("stock", width=150, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame, orient="vertical", command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ----- ฟอร์มกรอกข้อมูล / แก้ไข / ปรับสต็อก -----
    form_frame = tk.LabelFrame(
        self.root, text="จัดการข้อมูลสินค้า", padx=10, pady=10
    )
    form_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(form_frame, text="ชื่อสินค้า:").grid(
        row=0, column=0, padx=5, pady=5, sticky="e"
    )
    self.entry_name = tk.Entry(form_frame, width=20)
    self.entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="ราคา:").grid(
        row=0, column=2, padx=5, pady=5, sticky="e"
    )
    self.entry_price = tk.Entry(form_frame, width=15)
    self.entry_price.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(form_frame, text="จำนวน:").grid(
        row=0, column=4, padx=5, pady=5, sticky="e"
    )
    self.entry_stock = tk.Entry(form_frame, width=10)
    self.entry_stock.grid(row=0, column=5, padx=5, pady=5)

    # ปุ่มคำสั่ง
    btn_frame = tk.Frame(self.root, pady=5)
    btn_frame.pack(fill="x", padx=10)

    tk.Button(
        btn_frame,
        text="เพิ่มสินค้าใหม่",
        bg="#4CAF50",
        fg="black",
        command=self.add_product,
    ).pack(side="left", padx=5)
    
    tk.Button(
        btn_frame,
        text="บันทึกการแก้ไข",
        bg="#2196F3",
        fg="black",
        command=self.update_product,
    ).pack(side="left", padx=5)
    
    tk.Button(
        btn_frame,
        text="+ เพิ่มจำนวนสต็อก",
        bg="#FF9800",
        fg="black",
        command=lambda: self.adjust_stock(1),
    ).pack(side="left", padx=5)
    
    tk.Button(
        btn_frame,
        text="- ลดจำนวนสต็อก",
        bg="#f44336",
        fg="black",
        command=lambda: self.adjust_stock(-1),
    ).pack(side="left", padx=5)
    
    tk.Button(
        btn_frame,
        text="ลบสินค้า",
        bg="#795548",
        fg="black",
        command=self.delete_product,
    ).pack(side="left", padx=5)
    
    tk.Button(
        btn_frame, text="ล้างฟอร์ม", command=self.clear_entries
    ).pack(side="right", padx=5)

    # โหลดข้อมูลขึ้นตาราง
    self.refresh_table(self.inventory)

  # ----- ฟังก์ชันจัดการไฟล์ TXT -----

  def load_data_from_file(self):
    data = []
    if not os.path.exists(DATA_FILE):
      with open(DATA_FILE, "w", encoding="utf-8") as f:
        pass
      return data

    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
          line = line.strip()
          if line:  # ข้ามบรรทัดว่าง
            parts = line.split(",")
            if len(parts) == 3:
              name, price, stock = parts
              data.append({
                  "name": name,
                  "price": float(price),
                  "stock": int(stock),
              })
    except Exception as e:
      messagebox.showerror(
          "ข้อผิดพลาด", f"ไม่สามารถอ่านไฟล์ข้อมูลได้: {str(e)}"
      )

    return data

  def save_data_to_file(self):
    try:
      with open(DATA_FILE, "w", encoding="utf-8") as f:
        for item in self.inventory:
          f.write(f"{item['name']},{item['price']},{item['stock']}\n")
    except Exception as e:
      messagebox.showerror(
          "ข้อผิดพลาด", f"ไม่สามารถบันทึกข้อมูลลงไฟล์ได้: {str(e)}"
      )

  # ----- ฟังก์ชันการทำงาน -----

  def refresh_table(self, data_list):
    for item in self.tree.get_children():
      self.tree.delete(item)

    for item in data_list:
      self.tree.insert(
          "",
          "end",
          values=(item["name"], f"{item['price']:,.2f}", item["stock"]),
      )

  def on_select(self, event):
    selected_item = self.tree.selection()
    if selected_item:
      item_data = self.tree.item(selected_item[0])["values"]
      self.entry_name.delete(0, tk.END)
      self.entry_name.insert(0, item_data[0])

      price_clean = str(item_data[1]).replace(",", "")
      self.entry_price.delete(0, tk.END)
      self.entry_price.insert(0, price_clean)

      self.entry_stock.delete(0, tk.END)
      self.entry_stock.insert(0, item_data[2])

  def add_product(self):
    name = self.entry_name.get().strip()
    try:
      price = float(self.entry_price.get())
      stock = int(self.entry_stock.get())
    except ValueError:
      messagebox.showerror(
          "ข้อผิดพลาด", "กรุณากรอกราคาเป็นตัวเลข และจำนวนเป็นจำนวนเต็ม"
      )
      return

    if not name:
      messagebox.showwarning("เตือน", "กรุณากรอกชื่อสินค้า")
      return

    for p in self.inventory:
      if p["name"] == name:
        messagebox.showwarning(
            "เตือน",
            "มีสินค้านี้ในคลังแล้ว หากต้องการแก้ไขให้ใช้ปุ่ม 'บันทึกการแก้ไข'",
        )
        return

    self.inventory.append({"name": name, "price": price, "stock": stock})
    self.save_data_to_file()  # บันทึกลงไฟล์ TXT
    self.refresh_table(self.inventory)
    self.clear_entries()
    messagebox.showinfo("สำเร็จ", "เพิ่มสินค้าและบันทึกลงไฟล์แล้ว")

  def update_product(self):
    selected_item = self.tree.selection()
    if not selected_item:
      messagebox.showwarning("เตือน", "กรุณาเลือกสินค้าจากตารางที่ต้องการแก้ไข")
      return

    name = self.entry_name.get().strip()
    try:
      price = float(self.entry_price.get())
      stock = int(self.entry_stock.get())
    except ValueError:
      messagebox.showerror(
          "ข้อผิดพลาด", "กรุณากรอกราคาเป็นตัวเลข และจำนวนเป็นจำนวนเต็ม"
      )
      return

    original_name = self.tree.item(selected_item[0])["values"][0]

    for p in self.inventory:
      if p["name"] == original_name:
        p["name"] = name
        p["price"] = price
        p["stock"] = stock
        break

    self.save_data_to_file()  # บันทึกไฟล์ TXT
    self.refresh_table(self.inventory)
    self.clear_entries()
    messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลและบันทึกลงไฟล์แล้ว")

  
  def adjust_stock(self, stock):
    selected_item = self.tree.selection()
    if not selected_item:
      messagebox.showwarning("เตือน", "กรุณาเลือกสินค้าจากตารางเพื่อปรับสต็อก")
      return

    amount = simpledialog.askinteger('ข้อมูล', 'จำนวนสินค้า', minvalue=1)

    if amount is None:
      return
    
    amount = amount * stock

    item_name = self.tree.item(selected_item[0])["values"][0]

    for p in self.inventory:
      if p["name"] == item_name:
        if p["stock"] + amount < 0:
          messagebox.showerror("ข้อผิดพลาด", "จำนวนสินค้าไม่สามารถติดลบได้")
          return
        p["stock"] += amount
        break

    self.save_data_to_file()  # บันทึกไฟล์ TXT
    self.refresh_table(self.inventory)
    self.entry_stock.delete(0, tk.END)
    self.entry_stock.insert(
        0, next(p["stock"] for p in self.inventory if p["name"] == item_name)
    )

  def delete_product(self):
    selected_item = self.tree.selection()
    if not selected_item:
      messagebox.showwarning("เตือน", "กรุณาเลือกสินค้าที่ต้องการลบ")
      return

    item_name = self.tree.item(selected_item[0])["values"][0]

    if messagebox.askyesno(
        "ยืนยันการลบ", f"คุณต้องการลบสินค้า '{item_name}' ใช่หรือไม่?"
    ):
      self.inventory = [p for p in self.inventory if p["name"] != item_name]
      self.save_data_to_file()  # บันทึกไฟล์ TXT
      self.refresh_table(self.inventory)
      self.clear_entries()
      messagebox.showinfo("สำเร็จ", "ลบสินค้าเรียบร้อยแล้ว")

  def search_product(self, *args):
    query = self.search_var.get().lower()
    filtered = [p for p in self.inventory if query in p["name"].lower()]
    self.refresh_table(filtered)

  def clear_entries(self):
    self.entry_name.delete(0, tk.END)
    self.entry_price.delete(0, tk.END)
    self.entry_stock.delete(0, tk.END)


if __name__ == "__main__":
  root = tk.Tk()
  app = InventoryApp(root)
  root.mainloop()