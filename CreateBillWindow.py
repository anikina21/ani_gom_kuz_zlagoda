import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from datetime import datetime
from fpdf import FPDF

class CreateBillWindow(tk.Toplevel):
    def __init__(self, master, db_manager, user_data):
        super().__init__(master)
        self.db_manager = db_manager
        self.user_data = user_data
        self.title("Створення чека")
        self.geometry("820x500")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="ID касира:").grid(row=0, column=0, padx=10, pady=10)
        self.label_employee_id = tk.Label(self, text=self.user_data[0][0])
        self.label_employee_id.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self, text="Номер телефону клієнта (необов'язково):").grid(row=1, column=0, padx=10, pady=10)
        self.entry_phone_number = tk.Entry(self)
        self.entry_phone_number.grid(row=1, column=1, padx=10, pady=10)

        self.products_frame = tk.Frame(self)
        self.products_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.products_frame, columns=('UPC', 'Назва', 'Кількість', 'Ціна'), show='headings')
        self.tree.heading('UPC', text='UPC')
        self.tree.heading('Назва', text='Назва')
        self.tree.heading('Кількість', text='Кількість')
        self.tree.heading('Ціна', text='Ціна')
        self.tree.pack(side=tk.LEFT)

        scrollbar = ttk.Scrollbar(self.products_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="Додати товар", command=self.add_product).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Видалити товар", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Зберегти чек", command=self.save_bill).pack(side=tk.LEFT, padx=5)

    def add_product(self):
        self.add_product_window = tk.Toplevel(self)
        self.add_product_window.title("Додати товар")

        tk.Label(self.add_product_window, text="UPC товару:").grid(row=0, column=0, padx=10, pady=10)
        self.entry_upc = tk.Entry(self.add_product_window)
        self.entry_upc.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.add_product_window, text="Кількість:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_quantity = tk.Entry(self.add_product_window)
        self.entry_quantity.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.add_product_window, text="Додати", command=self.confirm_add_product).grid(row=2, column=0,
                                                                                                 columnspan=2, pady=10)

    def confirm_add_product(self):
        upc = self.entry_upc.get().strip()
        quantity = self.entry_quantity.get().strip()

        if not upc or not quantity:
            messagebox.showerror("Помилка", "Всі поля мають бути заповнені.")
            return

        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Кількість не може бути від'ємною")
        except ValueError as e:
            messagebox.showerror("Помилка", f"Неправильний формат кількості: {e}")
            return

        query = "SELECT p.product_name, sp.selling_price, sp.products_number FROM Store_Product sp JOIN Product p ON sp.id_product = p.id_product WHERE sp.UPC = %s"
        result = self.db_manager.execute_query(query, (upc,))
        if not result:
            messagebox.showerror("Помилка", "Товар з вказаним UPC не знайдено.")
            return

        product_name, price, available_quantity = result[0]
        if quantity > available_quantity:
            messagebox.showerror("Помилка",
                                 f"Неможливо додати {quantity} одиниць товару. Доступна кількість: {available_quantity}")
            return

        # Перевірка, чи вже існує товар з таким UPC у дереві
        for item in self.tree.get_children():
            item_values = self.tree.item(item, 'values')
            if item_values[0] == upc:
                new_quantity = int(item_values[2]) + quantity
                if new_quantity > available_quantity:
                    messagebox.showerror("Помилка",
                                         f"Неможливо додати {new_quantity} одиниць товару. Доступна кількість: {available_quantity}")
                    return
                self.tree.item(item, values=(upc, product_name, new_quantity, price))
                self.add_product_window.destroy()
                return

        # Якщо товар з таким UPC ще не існує, додати новий запис
        self.tree.insert("", tk.END, values=(upc, product_name, quantity, price))
        self.add_product_window.destroy()

    def delete_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)

    def save_bill(self):
        employee_id = self.user_data[0][0]
        phone_number = self.entry_phone_number.get().strip()

        card_number = None
        discount_percent = 0
        customer_name = ""
        customer_surname = ""

        if phone_number:
            query = "SELECT card_number, percent, cust_name, customer_surname FROM Customer_Card WHERE phone_number = %s"
            result = self.db_manager.execute_query(query, (phone_number,))
            if not result:
                messagebox.showerror("Помилка", "Клієнта з вказаним номером телефону не знайдено.")
                return
            card_number, discount_percent, customer_name, customer_surname = result[0]

        items = self.tree.get_children()
        if not items:
            messagebox.showerror("Помилка", "Додайте хоча б один товар до чека.")
            return

        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            sum_total = sum(float(self.tree.item(item, 'values')[3]) * int(self.tree.item(item, 'values')[2]) for item in items)
            sum_total = sum_total * (1 - discount_percent / 100)
            vat = sum_total * 0.2

            query = """
            INSERT INTO Bill (id_employee, card_number, print_date, sum_total, vat)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.db_manager.execute_non_query(query, (employee_id, card_number, date, sum_total, vat))

            check_number = self.db_manager.cursor.lastrowid

            for item in items:
                upc, product_name, quantity, price = self.tree.item(item, 'values')
                query = """
                INSERT INTO Sale (UPC, check_number, product_number, selling_price)
                VALUES (%s, %s, %s, %s)
                """
                self.db_manager.execute_non_query(query, (upc, check_number, quantity, price))

                # Оновлення кількості товару в магазині
                update_query = "UPDATE Store_Product SET products_number = products_number - %s WHERE UPC = %s"
                self.db_manager.execute_non_query(update_query, (quantity, upc))

            self.print_bill(check_number, date, sum_total, vat, items, discount_percent, customer_name, customer_surname)
            messagebox.showinfo("Успіх", "Чек успішно створено.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося створити чек: {e}")

    def print_bill(self, check_number, date, sum_total, vat, items, discount_percent, customer_name, customer_surname):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Check", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Check number: {check_number}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Date: {date}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Cashier: {self.user_data[0][0]} {self.user_data[0][1]} {self.user_data[0][2]}", ln=True, align='L')

        if customer_name and customer_surname:
            pdf.cell(200, 10, txt=f"Client: {customer_surname} {customer_name}", ln=True, align='L')

        if discount_percent > 0:
            pdf.cell(200, 10, txt=f"Discount: {discount_percent}%", ln=True, align='L')

        pdf.cell(200, 10, txt="Products:", ln=True, align='L')

        pdf.set_font("Arial", size=10)
        pdf.cell(40, 10, txt="UPC", border=1)
        pdf.cell(50, 10, txt="Name", border=1)
        pdf.cell(40, 10, txt="Quantity", border=1)
        pdf.cell(40, 10, txt="Price", border=1)
        pdf.ln()

        for item in items:
            upc, product_name, quantity, price = self.tree.item(item, 'values')
            pdf.cell(40, 10, txt=str(upc), border=1)
            pdf.cell(50, 10, txt=str(product_name), border=1)
            pdf.cell(40, 10, txt=str(quantity), border=1)
            pdf.cell(40, 10, txt=str(price), border=1)
            pdf.ln()

        pdf.cell(200, 10, txt=f"Total: {sum_total:.2f}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"vat: {vat:.2f}", ln=True, align='L')

        pdf.output(f"check_{check_number}.pdf")
        messagebox.showinfo("Чек збережено", f"Чек збережено як check_{check_number}.pdf")