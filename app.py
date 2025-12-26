#-----app.py-------
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, PhotoImage
import sqlite3
import uuid
from datetime import datetime
import os

#Optional PDF library
try:
    from fpdf import FPDF
    HAS_FPDF = True
except Exception:
    HAS_FPDF = False

#Config
DB = "coffee_shop.db"
SHOP_NAME = "THE CAFE CORNER"
ADDR_LINE1 = "152/9, PJN Road"
ADDR_LINE2 = "(Opp.to Poorvika Mobiles)"
ADDR_LINE3 = "Villupuram - 605602"
SHOP_PHONE = "04146-22233"

MENU = {
    "Dougnut": 120,
    "Cookies": 160,
    "Filter Coffee": 50,
    "Cappuccino": 50,
    "Milkshake": 45,
    "Cold Coffee": 130,
    "Hot Chocolate": 175,
    "Flat White": 140,
    "Brownie": 100,
    "Sandwich": 120
}

#Database setup
def ensure_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            item TEXT,
            quantity INTEGER,
            price REAL,
            total REAL,
            created TEXT
        )
    """)
    conn.commit()
    conn.close()

ensure_db()

#Login Window
class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Admin Login")
        master.geometry("320x200")
        master.resizable(False, False)

        tk.Label(master, text="Username:").pack(pady=(18, 4))
        self.user = tk.Entry(master)
        self.user.pack()

        tk.Label(master, text="Password:").pack(pady=(8, 4))
        self.pwd = tk.Entry(master, show="*")
        self.pwd.pack()

        tk.Button(master, text="Login", width=12, command=self.check).pack(pady=12)

    def check(self):
        if self.user.get() == "admin" and self.pwd.get() == "123":
            self.master.destroy()
            root = tk.Tk()
            CoffeeApp(root)
            root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid login")
#Main App
class CoffeeApp:
    def __init__(self, master):
        self.master = master
        master.title("Coffee Shop Management System")
        master.geometry("980x760")
        master.resizable(False, False)

        self.logo_img = None
        self.qr_img = None
        self.load_images()

        self.qty_vars = {}
        self.current_order_id = None

        self.build_header()
        self.build_menu_area()
        self.build_receipt_area()
        self.build_buttons_row()

    #Load logo
    def load_images(self):
        try:
            if os.path.exists("logo.png"):
                self.logo_img = PhotoImage(file="logo.png")
            elif os.path.exists("logo.gif"):
                self.logo_img = PhotoImage(file="logo.gif")
        except:
            self.logo_img = None

        try:
            if os.path.exists("qrcode.png"):
                self.qr_img = PhotoImage(file="qrcode.png")
            elif os.path.exists("qrcode.gif"):
                self.qr_img = PhotoImage(file="qrcode.gif")
        except:
            self.qr_img = None

        if self.logo_img:
            try:
                w, h = self.logo_img.width(), self.logo_img.height()
                if max(w, h) > 120:
                    factor = max(w, h) // 120 + 1
                    self.logo_img = self.logo_img.subsample(factor, factor)
            except: pass

        if self.qr_img:
            try:
                w, h = self.qr_img.width(), self.qr_img.height()
                if max(w, h) > 110:
                    factor = max(w, h) // 110 + 1
                    self.qr_img = self.qr_img.subsample(factor, factor)
            except: pass

    #Header
    def build_header(self):
        top_frame = tk.Frame(self.master)
        top_frame.place(x=50, y=8, width=950, height=100)

        if self.logo_img:
            tk.Label(top_frame, image=self.logo_img).pack(anchor="n", pady=(2, 0))

        tk.Label(top_frame, text=SHOP_NAME, font=("Times New Roman", 24, "bold")).pack(anchor="n")
        tk.Label(top_frame, text=ADDR_LINE1 + "  " + ADDR_LINE2, font=("Times New Roman", 10)).pack(anchor="n")
        tk.Label(top_frame, text=ADDR_LINE3 + "   Phone: " + SHOP_PHONE, font=("Times New Roman", 10)).pack(anchor="n")

    #Menu Area
    def build_menu_area(self):
        lf = tk.Frame(self.master)
        lf.place(x=10, y=140, width=620, height=480)

        tk.Label(lf, text="Menu", font=("Times New Roman", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=6)

        r = 1
        for item, price in MENU.items():
            tk.Label(lf, text=item, anchor="w", width=28).grid(row=r, column=0, sticky="w", padx=4, pady=4)
            tk.Label(lf, text=f"₹{price}", width=8).grid(row=r, column=1, padx=4)

            v = tk.IntVar(value=0)
            tk.Entry(lf, textvariable=v, width=6).grid(row=r, column=2, padx=4)

            self.qty_vars[item] = v
            r += 1

    #Receipt Area
    def build_receipt_area(self):
        rf = tk.Frame(self.master)
        rf.place(x=640, y=140, width=320, height=520)

        tk.Label(rf, text="Receipt", font=("Times New Roman", 16, "bold")).pack(anchor="w")

        self.canvas_w = 300
        self.canvas_h = 480
        self.rc = tk.Canvas(rf, width=self.canvas_w, height=self.canvas_h, bg="white",
                            highlightthickness=1, highlightbackground="#888")
        self.rc.pack(padx=6, pady=6)

        self.start_y = 8
        self.line_h = 18

        self.render_receipt_initial()

    #Draw initial receipt template
    def render_receipt_initial(self):
        self.rc.delete("all")
        self.y = self.start_y
        cx = self.canvas_w // 2

        ##Logo
        if self.logo_img:
            self.rc.create_image(cx, self.y, image=self.logo_img, anchor="n")
            try:
                self.y += self.logo_img.height() + 4
            except:
                self.y += 66
        else:
            self.y += 2

        #Header text
        self.rc.create_text(cx, self.y, text=SHOP_NAME, font=("Times New Roman", 10, "bold"), anchor="n")
        self.y += 18
        self.rc.create_text(cx, self.y, text=ADDR_LINE1, font=("Courier New", 9), anchor="n")
        self.y += 14
        self.rc.create_text(cx, self.y, text=ADDR_LINE2, font=("Courier New", 9), anchor="n")
        self.y += 14
        self.rc.create_text(cx, self.y, text=ADDR_LINE3, font=("Courier New", 9), anchor="n")
        self.y += 18

        #Divider
        self.rc.create_text(8, self.y, anchor="nw", text="-" * 38, font=("Courier New", 9))
        self.y += self.line_h

        #Date/time
        now = datetime.now()
        dt = f"Date: {now.strftime('%d-%m-%Y')}    Time: {now.strftime('%H:%M:%S')}"
        self.rc.create_text(8, self.y, anchor="nw", text=dt, font=("Courier New", 8))
        self.y += self.line_h

        #Order ID
        oid_text = self.current_order_id if self.current_order_id else "-"
        self.order_id_text_id = self.rc.create_text(
            8, self.y, anchor="nw",
            text=f"Order ID: {oid_text}", font=("Courier New", 8)
        )
        self.y += self.line_h

        #Divider + Table header
        self.rc.create_text(8, self.y, anchor="nw", text="-" * 38, font=("Courier New", 8))
        self.y += self.line_h

        self.rc.create_text(
            8, self.y, anchor="nw",
            text=f"{'Item':14}{'Qty':>2}{'Rate':>8}{'Total':>11}",
            font=("Courier New", 8, "bold")
        )
        self.y += self.line_h

        self.rc.create_text(8, self.y, anchor="nw", text="-" * 38, font=("Courier New", 8))
        self.y += self.line_h

        

        #Reserve item space
        self.items_start_y = self.y
        self.y += 3 * self.line_h

        #Divider before totals
        self.rc.create_text(8, self.y, anchor="nw", text="-" * 38, font=("Courier New", 8))
        self.y += 30

        #Grand Total
        self.grand_total_text_id = self.rc.create_text(
            8, self.y, anchor="nw",
            text=f"{'GRAND TOTAL'.rjust(30)}  ₹0.00",
            font=("Courier New", 9, "bold")
        )

        #Thank you footer
        self.thanks_y = self.canvas_h - 30
        self.rc.create_text(
            cx, self.thanks_y, anchor="center",
            text="Thank u,visit again!",
            font=("Times New Roman", 9, "bold"),
            tags=("thanks",)
        )

        #QR bottom-right
        qr_w = 68
        qr_h = 68
        self.qr_box_coords = (
            self.canvas_w - qr_w - 10, self.canvas_h - qr_h - 10,
            self.canvas_w - 10, self.canvas_h - 10
        )

        if self.qr_img:
            cx_q = (self.qr_box_coords[0] + self.qr_box_coords[2]) // 2
            cy_q = (self.qr_box_coords[1] + self.qr_box_coords[3]) // 2
            self.rc.create_image(cx_q, cy_q, image=self.qr_img, anchor="center", tags=("qr",))
        else:
            self.rc.create_rectangle(*self.qr_box_coords, outline="#666", tags=("qr_box",))
            self.rc.create_text(
                (self.qr_box_coords[0] + self.qr_box_coords[2]) // 2,
                (self.qr_box_coords[1] + self.qr_box_coords[3]) // 2,
                text="QR\nHere", font=("Arial", 8),
                fill="#666", anchor="center", tags=("qr_box",)
            )

    #Buttons Row
    def build_buttons_row(self):
        btn_frame = tk.Frame(self.master)
        btn_frame.place(x=450, y=640, width=500, height=60)

        tk.Button(btn_frame, text="Save Order", width=12, command=self.save_order).pack(side="left", padx=6, pady=8)
        tk.Button(btn_frame, text="Clear", width=12, command=self.clear_inputs).pack(side="left", padx=6, pady=8)
        tk.Button(btn_frame, text="Show Orders", width=12, command=self.show_orders).pack(side="left", padx=6, pady=8)
        tk.Button(btn_frame, text="Save TXT", width=12, command=self.save_txt).pack(side="left", padx=6, pady=8)
        tk.Button(btn_frame, text="Save PDF", width=12, command=self.save_pdf).pack(side="left", padx=6, pady=8)
        tk.Button(btn_frame, text="Exit", width=8, command=self.master.quit).pack(side="right", padx=6, pady=8)

    #Save Order
    def save_order(self):
        oid = str(uuid.uuid4())[:8].upper()
        self.current_order_id = oid

        self.rc.delete("itemline")
        y = self.items_start_y

        total_bill = 0.0
        items_saved = 0

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        created_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        for item, v in self.qty_vars.items():
            q = int(v.get() or 0)
            if q > 0:
                rate = float(MENU[item])
                tot = q * rate
                total_bill += tot

                line = f"{item[:14]:14}{q:>2}{rate:>10.2f}{tot:>11.2f}"

                self.rc.create_text(
                    8, y, anchor="nw", text=line,
                    font=("Courier New", 8), tags=("itemline",)
                )
                y += self.line_h

                items_saved += 1

                cur.execute(
                    "INSERT INTO orders (order_id, item, quantity, price, total, created) VALUES (?, ?, ?, ?, ?, ?)",
                    (oid, item, q, rate, tot, created_time)
                )

        conn.commit()
        conn.close()

        if items_saved == 0:
            messagebox.showwarning("No items", "Please enter quantity for at least one item.")
            return

        self.rc.itemconfig(self.order_id_text_id, text=f"Order ID: {oid}")

        #Update totals
        self.rc.itemconfig(self.grand_total_text_id, text=f"{'GRAND TOTAL'.rjust(30)}  ₹{total_bill:.2f}")

        #Refresh Thank you
        try:
            self.rc.delete("thanks")
        except:
            pass

        cx = self.canvas_w // 2
        self.rc.create_text(
            cx, self.thanks_y, anchor="center",
            text="Thank u, visit again!",
            font=("Arial", 7, "bold"),
            tags=("thanks",)
        )

        #Refresh QR
        if self.qr_img:
            try:
                self.rc.delete("qr")
            except:
                pass

            cx_q = (self.qr_box_coords[0] + self.qr_box_coords[2]) // 2
            cy_q = (self.qr_box_coords[1] + self.qr_box_coords[3]) // 2
            self.rc.create_image(cx_q, cy_q, image=self.qr_img, anchor="center", tags=("qr",))

        messagebox.showinfo("Saved", f"Order saved (ID: {oid})")

    #Clear
    def clear_inputs(self):
        for v in self.qty_vars.values():
            v.set(0)
        self.current_order_id = None
        self.render_receipt_initial()

    #Save TXT
    def save_txt(self):
        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        time = now.strftime("%H:%M:%S")

        lines = []
        lines.append(SHOP_NAME)
        lines.append(ADDR_LINE1)
        lines.append(ADDR_LINE2)
        lines.append(ADDR_LINE3)
        lines.append(f"Phone: {SHOP_PHONE}")
        lines.append("-" * 48)
        lines.append(f"Date: {date}    Time: {time}")
        lines.append(f"Order ID: {self.current_order_id if self.current_order_id else '-'}")
        lines.append("-" * 48)
        lines.append(f"{'Item':16}{'Qty':>3}{'Rate':>7}{'Total':>7}")
        lines.append("-" * 48)

        total_bill = 0.0

        for item, v in self.qty_vars.items():
            q = int(v.get() or 0)
            if q > 0:
                rate = float(MENU[item])
                tot = q * rate
                total_bill += tot
                lines.append(f"{item[:16]:16}{q:>3}{rate:>7.2f}{tot:>7.2f}")

        lines.append("-" * 48)
        lines.append(f"{'Total'.rjust(34)}  ₹{total_bill:.2f}")
        lines.append("")
        lines.append("Thank u,visit again!")

        fname = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if fname:
            with open(fname, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Saved", "TXT saved")

    #Save PDF
    def save_pdf(self):
        if not HAS_FPDF:
            messagebox.showerror("Missing library", "Install fpdf: pip install fpdf")
            return

        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        time = now.strftime("%H:%M:%S")

        page_w, page_h = 420, 600
        pdf = FPDF(orientation="P", unit="pt", format=(page_w, page_h))
        pdf.add_page()
        pdf.set_auto_page_break(False)

        #Top Logo
        if os.path.exists("logo.png"):
            try:
                pdf.image("logo.png", x=(page_w / 2) - 40, y=12, w=80)
            except: pass

        pdf.set_font("Arial", "B", 14)
        pdf.set_xy(0, 12 + 80)
        pdf.cell(page_w, 18, SHOP_NAME, ln=1, align="C")

        pdf.set_font("Arial", "", 9)
        pdf.cell(page_w, 12, ADDR_LINE1, ln=1, align="C")
        pdf.cell(page_w, 12, ADDR_LINE2, ln=1, align="C")
        pdf.cell(page_w, 12, ADDR_LINE3 + "    Phone: " + SHOP_PHONE, ln=1, align="C")

        pdf.set_font("Courier", "", 8)
        pdf.cell(page_w, 12, "-" * 44, ln=1, align="L")
        pdf.cell(page_w, 12, f"Date: {date}    Time: {time}", ln=1, align="L")
        pdf.cell(page_w, 12, f"Order ID: {self.current_order_id if self.current_order_id else '-'}", ln=1, align="L")
        pdf.cell(page_w, 12, "-" * 44, ln=1, align="L")

        pdf.set_font("Courier", "B", 9)
        pdf.cell(200, 12, "Item", border=0)
        pdf.cell(40, 12, "Qty", border=0, align="R")
        pdf.cell(80, 12, "Rate", border=0, align="R")
        pdf.cell(80, 12, "Total", border=0, align="R")
        pdf.ln(14)

        pdf.set_font("Courier", "", 9)

        total_bill = 0.0
        for item, v in self.qty_vars.items():
            q = int(v.get() or 0)
            if q > 0:
                rate = float(MENU[item])
                tot = q * rate
                total_bill += tot

                pdf.cell(200, 12, item[:24], border=0)
                pdf.cell(40, 12, str(q), border=0, align="R")
                pdf.cell(80, 12, f"{rate:.2f}", border=0, align="R")
                pdf.cell(80, 12, f"{tot:.2f}", border=0, align="R")
                pdf.ln(12)

        pdf.cell(page_w, 12, "-" * 44, ln=1, align="L")

        pdf.set_font("Courier", "B", 10)
        pdf.cell(320, 12, "", border=0)
        pdf.cell(100, 12, f"Total ₹{total_bill:.2f}", border=0, align="R")

        pdf.ln(20)

        if os.path.exists("qrcode.png"):
            try:
                pdf.image("qrcode.png", x=page_w - 40 - 20, y=page_h - 140, w=50)
            except: pass

        fname = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if fname:
            try:
                pdf.output(fname)
                messagebox.showinfo("Saved", "PDF saved.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {e}")

    #Show Orders
    def show_orders(self):
        win = tk.Toplevel(self.master)
        win.title("All Orders")
        win.geometry("1000x420")

        cols = ("SNo", "OrderID", "Item", "Qty", "Rate", "Total", "Created")
        tree = ttk.Treeview(win, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)

        tree.column("SNo", width=50, anchor="center")
        tree.column("OrderID", width=110, anchor="center")
        tree.column("Item", width=250, anchor="w")
        tree.column("Qty", width=50, anchor="center")
        tree.column("Rate", width=80, anchor="e")
        tree.column("Total", width=90, anchor="e")
        tree.column("Created", width=200, anchor="center")
        tree.pack(fill="both", expand=True, padx=8, pady=8)

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT id, order_id, item, quantity, price, total, created FROM orders ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        sno = 1
        for r in rows:
            rate = float(r[4]) if r[4] is not None else 0.0
            total = float(r[5]) if r[5] is not None else 0.0
            created = r[6] if r[6] else ""

            tree.insert("", tk.END, values=(sno, r[1], r[2], r[3], f"{rate:.2f}", f"{total:.2f}", created))
            sno += 1


#Run
if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
