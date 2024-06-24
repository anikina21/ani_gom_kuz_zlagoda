import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from fpdf import FPDF

from CustomerCardDialog import CustomerCardDialog


class CustomerCardViewWindow(tk.Toplevel):
    def __init__(self, master, role, db_manager):
        super().__init__(master)
        self.title("Відомості про картки клієнтів")
        self.role = role
        self.db_manager = db_manager
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("card_number", "customer_surname", "cust_name", "cust_patronymic", "phone_number", "city", "street", "zip_code", "percent"), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=120)
        self.tree.pack(expand=True, fill=tk.BOTH)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Оновити/Скинути", command=self.load_data).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сортувати за прізвищем", command=lambda: self.sort_data("customer_surname")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Пошук за прізвищем", command=self.search_by_surname).pack(side=tk.LEFT, padx=5)

        if self.role == 'manager':
            tk.Button(btn_frame, text="Пошук за відсотком", command=self.search_by_percent).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Додати картку", command=self.add_card).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редагувати картку", command=self.edit_card).pack(side=tk.LEFT, padx=5)

        if self.role == 'manager':
            tk.Button(btn_frame, text="Видалити картку", command=self.delete_card).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Друкувати звіт", command=self.print_report).pack(side=tk.LEFT, padx=5)

        self.load_data()

    def search_by_percent(self):
        #percent = self.percent_entry.get()
        percent = simpledialog.askinteger("Пошук", "Введіть відсоток:")
        if percent < 0:
            messagebox.showerror("Помилка", "Будь ласка, введіть коректний відсоток.")
            return
        query = """
        SELECT * FROM Customer_Card
        WHERE percent = %s
        ORDER BY customer_surname ASC
        """
        result = self.db_manager.execute_query(query, (percent,))
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in result:
            self.tree.insert("", tk.END, values=row)


    def load_data(self):
        query = "SELECT * FROM Customer_Card"
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def sort_data(self, column):
        query = f"SELECT * FROM Customer_Card ORDER BY {column}"
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def search_by_surname(self):
        surname = simpledialog.askstring("Пошук", "Введіть прізвище клієнта:")
        query = "SELECT * FROM Customer_Card WHERE customer_surname LIKE %s"
        result = self.db_manager.execute_query(query, ('%' + surname + '%',))
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def add_card(self):
        # Відкриваємо діалогове вікно без передачі даних про існуючу картку
        card_dialog = CustomerCardDialog(self, self.db_manager)
        self.wait_window(card_dialog)  # Чекаємо закриття діалогового вікна
        self.load_data()

    def delete_card(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Увага", "Будь ласка, виберіть картку клієнта для видалення.")
            return

        # Вибірка номера картки клієнта з обраного елемента в дереві
        card_number = self.tree.item(selected_item, 'values')[0]

        query = "DELETE FROM Customer_Card WHERE card_number = %s"
        self.db_manager.execute_non_query(query, (card_number,))
        self.load_data()

    def edit_card(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Увага", "Будь ласка, виберіть картку клієнта для редагування.")
            return

        # Збираємо дані про обрану картку для передачі у діалогове вікно
        card_data = {col: self.tree.item(selected_item, 'values')[i] for i, col in enumerate(self.tree["columns"])}

        # Відкриваємо діалогове вікно з даними про обрану картку
        card_dialog = CustomerCardDialog(self, self.db_manager, card_data)
        self.wait_window(card_dialog)  # Чекаємо закриття діалогового вікна
        self.load_data()

    def print_report(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=7)
        column_widths = [20, 25, 25, 25, 20, 15, 25, 15, 10]  # Ширини колонок повинні відповідати кількості заголовків

        # Заголовки для стовпців
        headers = ["Card Number", "Surname", "Name", "Patronymic", "Phone", "City", "Street", "Zip Code", "Percent"]
        pdf.set_fill_color(200, 220, 255)  # Світло-блакитний фон для заголовків
        for i, header in enumerate(headers):
            pdf.cell(column_widths[i], 8, header, border=1, ln=0, align='C', fill=True)
        pdf.ln()

        # Вивід даних
        for item in self.tree.get_children():
            row_values = self.tree.item(item, 'values')
            if len(row_values) != len(headers):  # Перевірка на відповідність довжини даних і заголовків
                continue  # Пропускаємо рядки, які не відповідають очікуваному формату
            for i, value in enumerate(row_values):
                pdf.cell(column_widths[i], 8, str(value), border=1, ln=0, align='C')
            pdf.ln()

        # Збереження PDF
        pdf.output("Customer_Card_Report.pdf")
        messagebox.showinfo("Звіт створено", "Звіт про картки клієнтів збережено як 'Customer_Card_Report.pdf'")