import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from datetime import datetime
from fpdf import FPDF

class CheckViewWindow(tk.Toplevel):
    def __init__(self, master, role, db_manager, user_data):
        super().__init__(master)
        self.role = role
        self.db_manager = db_manager
        self.user_data = user_data
        self.title("Перегляд чеків")
        self.geometry("1300x600")

        self.delete_old_checks()  # Видалення старих чеків

        self.cashiers = self.load_cashiers()

        self.create_widgets()

    def create_widgets(self):
        # Верхній фрейм для кнопок
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Оновити/Скинути", command=self.load_checks).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Пошук за номером чеку", command=self.search_by_check_number).grid(row=0, column=1, padx=5, pady=5)

        if self.role == 'cashier':
            tk.Button(btn_frame, text="Переглянути чеки за день", command=self.view_checks_for_today).grid(row=0, column=2, padx=5, pady=5)
            tk.Button(btn_frame, text="Переглянути чеки за період", command=self.view_checks_for_period).grid(row=0, column=3, padx=5, pady=5)
        elif self.role == 'manager':
            tk.Button(btn_frame, text="Видалити чек", command=self.delete_check).grid(row=0, column=2, padx=5, pady=5)
            tk.Button(btn_frame, text="Чеки за період (касирами)", command=self.view_checks_by_cashier_for_period).grid(row=0, column=3, padx=5, pady=5)
            tk.Button(btn_frame, text="Чеки за період (усі)", command=self.view_all_checks_for_period).grid(row=0, column=4, padx=5, pady=5)
            tk.Button(btn_frame, text="Сума проданих товарів (касирами)", command=self.calculate_total_sales_by_cashier).grid(row=1, column=0, padx=5, pady=5)
            tk.Button(btn_frame, text="Сума проданих товарів (усі)", command=self.calculate_total_sales_all_cashiers).grid(row=1, column=1, padx=5, pady=5)
            tk.Button(btn_frame, text="Кількість проданого товару", command=self.calculate_total_quantity_of_product).grid(row=1, column=2, padx=5, pady=5)

        tk.Button(btn_frame, text="Складові чеку", command=self.view_check_details).grid(row=1, column=3, padx=5, pady=5)
        tk.Button(btn_frame, text="Друк чеку", command=self.print_check).grid(row=1, column=4, padx=5, pady=5)
        tk.Button(btn_frame, text="Друк звіту", command=self.print_report).grid(row=1, column=5, padx=5, pady=5)

        # Фрейм для таблиці
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ['Check number', 'cashier id', 'cashier surname', 'client card id', 'cashier surname', 'Date', 'Total', 'vat']
        #columns = ['Номер чеку', 'ID касира', 'Прізвище касира', 'ID клієнта', 'Прізвище клієнта', 'Дата', 'Загальна сума', 'ПДВ']
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=50, width=150, stretch=tk.NO)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.load_checks()

    def delete_old_checks(self):
        query = """
        DELETE FROM Bill
        WHERE print_date < NOW() - INTERVAL 3 YEAR
        """
        self.db_manager.execute_non_query(query)
    def load_checks(self):
        query = """
        SELECT b.check_number, b.id_employee, e.empl_surname, b.card_number, c.customer_surname, b.print_date, b.sum_total, b.vat
        FROM Bill b
        JOIN Employee e ON b.id_employee = e.id_employee
        LEFT JOIN Customer_Card c ON b.card_number = c.card_number
        """
        result = self.db_manager.execute_query(query)
        self.update_table(result)

    def update_table(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def search_by_check_number(self):
        check_number = simpledialog.askstring("Пошук", "Введіть номер чеку:")
        query = """
        SELECT b.check_number, b.id_employee, e.empl_surname, b.card_number, c.customer_surname, b.print_date, b.sum_total, b.vat
        FROM Bill b
        JOIN Employee e ON b.id_employee = e.id_employee
        LEFT JOIN Customer_Card c ON b.card_number = c.card_number
        WHERE b.check_number = %s
        """
        result = self.db_manager.execute_query(query, (check_number,))
        self.update_table(result)
        if result:
            self.view_check_details(check_number)

    def view_checks_for_today(self):
        employee_id = self.user_data[0][0]
        start_date = datetime.now().strftime('%Y-%m-%d 00:00:00')
        end_date = datetime.now().strftime('%Y-%m-%d 23:59:59')
        query = """
        SELECT b.check_number, b.id_employee, e.empl_surname, b.card_number, c.customer_surname, b.print_date, b.sum_total, b.vat
        FROM Bill b
        JOIN Employee e ON b.id_employee = e.id_employee
        LEFT JOIN Customer_Card c ON b.card_number = c.card_number
        WHERE b.id_employee = %s AND b.print_date BETWEEN %s AND %s
        """
        result = self.db_manager.execute_query(query, (employee_id, start_date, end_date))
        self.update_table(result)

    def view_checks_for_period(self):
        self.period_window("Період", self.load_checks_for_period)

    def view_checks_by_cashier_for_period(self):
        self.period_window("Період касира", self.load_checks_by_cashier_for_period, include_cashier=True)

    def view_all_checks_for_period(self):
        self.period_window("Період (усі)", self.load_all_checks_for_period)

    def calculate_total_sales_by_cashier(self):
        self.period_window("Сума товарів касира", self.load_total_sales_by_cashier, include_cashier=True)

    def calculate_total_sales_all_cashiers(self):
        self.period_window("Сума товарів (усі)", self.load_total_sales_all_cashiers)

    def calculate_total_quantity_of_product(self):
        window = tk.Toplevel(self)
        window.title("Кількість проданих товарів")
        window.geometry("300x300")

        tk.Label(window, text="Початкова дата:").pack(pady=5)
        start_date_entry = DateEntry(window)
        start_date_entry.pack(pady=5)

        tk.Label(window, text="Кінцева дата:").pack(pady=5)
        end_date_entry = DateEntry(window)
        end_date_entry.pack(pady=5)

        # Завантаження товарів для випадаючого списку
        products = self.load_products()
        tk.Label(window, text="Товар:").pack(pady=5)
        product_combobox = ttk.Combobox(window, values=products)
        product_combobox.pack(pady=5)

        def on_submit():
            start_date = start_date_entry.get_date().strftime('%Y-%m-%d')
            end_date = end_date_entry.get_date().strftime('%Y-%m-%d')
            upc = product_combobox.get().split()[0]
            window.destroy()
            self.load_total_quantity_of_product(start_date, end_date, upc)

        tk.Button(window, text="OK", command=on_submit).pack(pady=10)

    def load_products(self):
        query = "SELECT id_product, product_name FROM Product"
        result = self.db_manager.execute_query(query)
        return [f"{row[0]} - {row[1]}" for row in result]

    def load_total_quantity_of_product(self, start_date, end_date, upc):
        query = """
        SELECT SUM(s.product_number)
        FROM Sale s
        JOIN Bill b ON s.check_number = b.check_number
        WHERE s.UPC = %s AND b.print_date BETWEEN %s AND %s
        """
        result = self.db_manager.execute_query(query, (upc, start_date, end_date))
        total_quantity = result[0][0] if result[0][0] else 0
        messagebox.showinfo("Загальна кількість", f"Загальна кількість проданих товарів: {total_quantity}")

    def delete_check(self):
        selected_item = self.tree.selection()
        if selected_item:
            check_number = self.tree.item(selected_item, 'values')[0]
            confirm = messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете видалити чек №{check_number}?")
            if confirm:
                query = "DELETE FROM Bill WHERE check_number = %s"
                self.db_manager.execute_non_query(query, (check_number,))
                self.load_checks()

    def view_check_details(self, check_number=None):
        if not check_number:
            selected_item = self.tree.selection()
            if selected_item:
                check_number = self.tree.item(selected_item, 'values')[0]
            else:
                messagebox.showinfo("Увага", "Будь ласка, виберіть чек для перегляду.")
                return

        details_window = tk.Toplevel(self)
        details_window.title(f"Деталі чеку №{check_number}")
        details_window.geometry("800x400")

        columns = ['UPC', 'Name', 'Quantity', 'Price']
        tree = ttk.Treeview(details_window, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, minwidth=50, width=150, stretch=tk.NO)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        query = """
        SELECT s.UPC, p.product_name, s.product_number, s.selling_price
        FROM Sale s
        JOIN Store_Product sp ON s.UPC = sp.UPC
        JOIN Product p ON sp.id_product = p.id_product
        WHERE s.check_number = %s
        """
        result = self.db_manager.execute_query(query, (check_number,))
        for row in result:
            tree.insert("", tk.END, values=row)

    def print_check(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Увага", "Будь ласка, виберіть чек для друку.")
            return

        check_number = self.tree.item(selected_item, 'values')[0]
        query = """
        SELECT s.UPC, p.product_name, s.product_number, s.selling_price
        FROM Sale s
        JOIN Store_Product sp ON s.UPC = sp.UPC
        JOIN Product p ON sp.id_product = p.id_product
        WHERE s.check_number = %s
        """
        result = self.db_manager.execute_query(query, (check_number,))
        self.generate_pdf_report(f"Check_{check_number}.pdf", result, title=f"Check{check_number}", report_type="check", check_number=check_number)

    def print_report(self):
        query = """
        SELECT b.check_number, b.id_employee, e.empl_surname, b.card_number, c.customer_surname, b.print_date, b.sum_total, b.vat
        FROM Bill b
        JOIN Employee e ON b.id_employee = e.id_employee
        LEFT JOIN Customer_Card c ON b.card_number = c.card_number
        """
        result = self.db_manager.execute_query(query)
        self.generate_pdf_report("Check_Report.pdf", result, title="check report", report_type="report")

    def generate_pdf_report(self, filename, data, title="Report", report_type="report", check_number=None):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=8)
        pdf.cell(200, 8, txt=title, ln=True, align='C')

        pdf.set_font("Arial", size=6)

        if report_type == "report":
            #command_name = simpledialog.askstring("Команда", "Введіть назву команди, яка дала результат:")
            #pdf.cell(200, 10, txt=f"Команда: {command_name}", ln=True, align='L')

            # Заголовки колонок
            columns = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
            col_width = 190 / len(columns)  # Загальна ширина сторінки 190, ділиться на кількість колонок
            col_widths = [col_width] * len(columns)

            for col, width in zip(columns, col_widths):
                pdf.cell(width, 8, txt=str(col), border=1)
            pdf.ln()

            # Дані з таблиці
            for row_id in self.tree.get_children():
                row = self.tree.item(row_id)["values"]
                for i, item in enumerate(row):
                    pdf.cell(col_widths[i], 10, txt=str(item), border=1)
                pdf.ln()

        elif report_type == "check":
            pdf.cell(200, 10, txt=f"Check number: {check_number}", ln=True, align='L')
            pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='L')
            pdf.cell(200, 10, txt=f"Cashier: {self.user_data[0][0]} {self.user_data[0][1]} {self.user_data[0][2]}",
                     ln=True, align='L')

            query = """
            SELECT c.cust_name, c.customer_surname, c.percent
            FROM Bill b
            LEFT JOIN Customer_Card c ON b.card_number = c.card_number
            WHERE b.check_number = %s
            """
            result = self.db_manager.execute_query(query, (check_number,))
            if result and result[0][0] and result[0][1]:
                pdf.cell(200, 10, txt=f"Client: {result[0][1]} {result[0][0]}", ln=True, align='L')
            if result and result[0][2]:
                pdf.cell(200, 10, txt=f"Discount: {result[0][2]}%", ln=True, align='L')

            pdf.cell(200, 10, txt="Products:", ln=True, align='L')

            pdf.set_font("Arial", size=10)
            pdf.cell(40, 10, txt="UPC", border=1)
            pdf.cell(50, 10, txt="Name", border=1)
            pdf.cell(40, 10, txt="Quantity", border=1)
            pdf.cell(40, 10, txt="Price", border=1)
            pdf.ln()

            col_widths = [40, 50, 40, 40]
            for item in data:
                upc, product_name, quantity, price = item
                pdf.cell(col_widths[0], 10, txt=str(upc), border=1)
                pdf.cell(col_widths[1], 10, txt=str(product_name), border=1)
                pdf.cell(col_widths[2], 10, txt=str(quantity), border=1)
                pdf.cell(col_widths[3], 10, txt=str(price), border=1)
                pdf.ln()

            query = """
            SELECT sum_total, vat
            FROM Bill
            WHERE check_number = %s
            """
            result = self.db_manager.execute_query(query, (check_number,))
            sum_total, vat = result[0]
            pdf.cell(200, 10, txt=f"Total: {sum_total:.2f}", ln=True, align='L')
            pdf.cell(200, 10, txt=f"vat: {vat:.2f}", ln=True, align='L')

        pdf.output(filename)
        messagebox.showinfo("Звіт створено", f"Звіт збережено як '{filename}'")

    def period_window(self, title, command, include_cashier=False):
        def on_submit():
            start_date = start_date_entry.get_date()
            end_date = end_date_entry.get_date()
            cashier = cashier_combo.get().split(" - ")[0] if include_cashier else None

            if include_cashier and not cashier:
                messagebox.showerror("Помилка", "Будь ласка, виберіть касира.")
                return

            command(start_date, end_date, cashier)
            dialog.destroy()

        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("300x300")

        tk.Label(dialog, text="Початкова дата:").pack(pady=5)
        start_date_entry = DateEntry(dialog, width=12, background='darkblue', foreground='white', borderwidth=2)
        start_date_entry.pack(pady=5)

        tk.Label(dialog, text="Кінцева дата:").pack(pady=5)
        end_date_entry = DateEntry(dialog, width=12, background='darkblue', foreground='white', borderwidth=2)
        end_date_entry.pack(pady=5)

        if include_cashier:
            tk.Label(dialog, text="Касир:").pack(pady=5)
            cashier_combo = ttk.Combobox(dialog, values=self.cashiers)
            cashier_combo.pack(pady=5)

        tk.Button(dialog, text="Підтвердити", command=on_submit).pack(pady=10)

    def get_date_range(self):
        dialog = tk.Toplevel(self)
        dialog.title("Вибір періоду")
        dialog.geometry("300x200")

        tk.Label(dialog, text="Початкова дата:").pack(pady=5)
        start_date_entry = DateEntry(dialog, width=12, background='darkblue', foreground='white', borderwidth=2)
        start_date_entry.pack(pady=5)

        tk.Label(dialog, text="Кінцева дата:").pack(pady=5)
        end_date_entry = DateEntry(dialog, width=12, background='darkblue', foreground='white', borderwidth=2)
        end_date_entry.pack(pady=5)

        def on_submit():
            start_date = start_date_entry.get_date()
            end_date = end_date_entry.get_date()
            dialog.destroy()
            return start_date, end_date

        tk.Button(dialog, text="Підтвердити", command=on_submit).pack(pady=10)
        self.wait_window(dialog)

        return start_date_entry.get_date(), end_date_entry.get_date()

    def load_cashiers(self):
        query = "SELECT id_employee, empl_surname, empl_name FROM Employee WHERE empl_role = 'cashier'"
        result = self.db_manager.execute_query(query)
        return [f"{row[0]} - {row[1]} {row[2]}" for row in result]

    def load_checks_for_period(self, start_date, end_date, _):
        query = """
        SELECT b.check_number, b.id_employee, e.empl_surname, b.card_number, c.customer_surname, b.print_date, b.sum_total, b.vat
        FROM Bill b
        JOIN Employee e ON b.id_employee = e.id_employee
        LEFT JOIN Customer_Card c ON b.card_number = c.card_number
        WHERE b.id_employee = %s AND b.print_date BETWEEN %s AND %s
        """
        employee_id = self.user_data[0][0]
        result = self.db_manager.execute_query(query, (employee_id, start_date, end_date))
        self.update_table(result)

    def load_checks_by_cashier_for_period(self, start_date, end_date, cashier_id):
        query = """
        SELECT b.check_number, b.id_employee, e.empl_surname, b.card_number, c.customer_surname, b.print_date, b.sum_total, b.vat
        FROM Bill b
        JOIN Employee e ON b.id_employee = e.id_employee
        LEFT JOIN Customer_Card c ON b.card_number = c.card_number
        WHERE b.id_employee = %s AND b.print_date BETWEEN %s AND %s
        """
        result = self.db_manager.execute_query(query, (cashier_id, start_date, end_date))
        self.update_table(result)

    def load_all_checks_for_period(self, start_date, end_date, _):
        query = """
        SELECT b.check_number, b.id_employee, e.empl_surname, b.card_number, c.customer_surname, b.print_date, b.sum_total, b.vat
        FROM Bill b
        JOIN Employee e ON b.id_employee = e.id_employee
        LEFT JOIN Customer_Card c ON b.card_number = c.card_number
        WHERE b.print_date BETWEEN %s AND %s
        """
        result = self.db_manager.execute_query(query, (start_date, end_date))
        self.update_table(result)

    def load_total_sales_by_cashier(self, start_date, end_date, cashier_id):
        query = """
        SELECT SUM(b.sum_total)
        FROM Bill b
        WHERE b.id_employee = %s AND b.print_date BETWEEN %s AND %s
        """
        result = self.db_manager.execute_query(query, (cashier_id, start_date, end_date))
        total_sales = result[0][0] if result[0][0] else 0
        messagebox.showinfo("Загальна сума", f"Загальна сума проданих товарів: {total_sales:.2f}")

    def load_total_sales_all_cashiers(self, start_date, end_date, _):
        query = """
        SELECT SUM(b.sum_total)
        FROM Bill b
        WHERE b.print_date BETWEEN %s AND %s
        """
        result = self.db_manager.execute_query(query, (start_date, end_date))
        total_sales = result[0][0] if result[0][0] else 0
        messagebox.showinfo("Загальна сума", f"Загальна сума проданих товарів: {total_sales:.2f}")