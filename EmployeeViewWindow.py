import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from fpdf import FPDF
from datetime import datetime, timedelta
import hashlib

class EmployeeDialog(tk.Toplevel):
    def __init__(self, parent, db_manager, employee=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.employee = employee
        self.title("Додати / Редагувати працівника")

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="ID:").grid(row=0, column=0, padx=10, pady=10)
        self.entry_id = ttk.Entry(self)
        self.entry_id.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self, text="Прізвище:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_surname = ttk.Entry(self)
        self.entry_surname.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self, text="Ім'я:").grid(row=2, column=0, padx=10, pady=10)
        self.entry_name = ttk.Entry(self)
        self.entry_name.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self, text="По батькові:").grid(row=3, column=0, padx=10, pady=10)
        self.entry_patronymic = ttk.Entry(self)
        self.entry_patronymic.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(self, text="Роль:").grid(row=4, column=0, padx=10, pady=10)
        self.combo_role = ttk.Combobox(self, values=["manager", "cashier"])
        self.combo_role.grid(row=4, column=1, padx=10, pady=10)

        ttk.Label(self, text="Зарплата:").grid(row=5, column=0, padx=10, pady=10)
        self.entry_salary = ttk.Entry(self)
        self.entry_salary.grid(row=5, column=1, padx=10, pady=10)

        ttk.Label(self, text="Дата народження (YYYY-MM-DD):").grid(row=6, column=0, padx=10, pady=10)
        self.entry_birth = ttk.Entry(self)
        self.entry_birth.grid(row=6, column=1, padx=10, pady=10)

        ttk.Label(self, text="Дата початку роботи (YYYY-MM-DD):").grid(row=7, column=0, padx=10, pady=10)
        self.entry_start = ttk.Entry(self)
        self.entry_start.grid(row=7, column=1, padx=10, pady=10)

        ttk.Label(self, text="Телефон:").grid(row=8, column=0, padx=10, pady=10)
        self.entry_phone = ttk.Entry(self)
        self.entry_phone.grid(row=8, column=1, padx=10, pady=10)

        ttk.Label(self, text="Місто:").grid(row=9, column=0, padx=10, pady=10)
        self.entry_city = ttk.Entry(self)
        self.entry_city.grid(row=9, column=1, padx=10, pady=10)

        ttk.Label(self, text="Вулиця:").grid(row=10, column=0, padx=10, pady=10)
        self.entry_street = ttk.Entry(self)
        self.entry_street.grid(row=10, column=1, padx=10, pady=10)

        ttk.Label(self, text="Поштовий індекс:").grid(row=11, column=0, padx=10, pady=10)
        self.entry_zip = ttk.Entry(self)
        self.entry_zip.grid(row=11, column=1, padx=10, pady=10)

        ttk.Label(self, text="Логін:").grid(row=12, column=0, padx=10, pady=10)
        self.entry_login = ttk.Entry(self)
        self.entry_login.grid(row=12, column=1, padx=10, pady=10)

        ttk.Label(self, text="Пароль:").grid(row=13, column=0, padx=10, pady=10)
        self.entry_password = ttk.Entry(self)
        self.entry_password.grid(row=13, column=1, padx=10, pady=10)

        ttk.Button(self, text="Зберегти", command=self.save_employee).grid(row=14, column=0, columnspan=2, pady=10)

        if self.employee:
            self.fill_data()

    def fill_data(self):
        self.entry_id.insert(0, self.employee['id_employee'])
        self.entry_surname.insert(0, self.employee['empl_surname'])
        self.entry_name.insert(0, self.employee['empl_name'])
        self.entry_patronymic.insert(0, self.employee.get('empl_patronymic', ''))
        self.combo_role.set(self.employee['empl_role'])
        self.entry_salary.insert(0, str(self.employee['salary']))
        self.entry_birth.insert(0, self.employee['date_of_birth'])
        self.entry_start.insert(0, self.employee['date_of_start'])
        self.entry_phone.insert(0, self.employee['phone_number'])
        self.entry_city.insert(0, self.employee['city'])
        self.entry_street.insert(0, self.employee['street'])
        self.entry_zip.insert(0, self.employee['zip_code'])
        self.entry_login.insert(0, self.employee['login'])
        self.entry_password.insert(0, "")  # Не відображаємо реальний пароль

    def save_employee(self):
        # Перевірка на заповненість обов'язкових полів
        if not all([self.entry_id.get().strip(), self.entry_surname.get().strip(), self.entry_name.get().strip(),
                    self.combo_role.get(), self.entry_salary.get().strip(), self.entry_birth.get().strip(),
                    self.entry_phone.get().strip(), self.entry_login.get().strip()]):
            messagebox.showerror("Помилка", "Всі поля, окрім по батькові та адреси, обов'язкові для заповнення.")
            return

        # Перевірка на коректність зарплати
        try:
            salary = float(self.entry_salary.get())
            if salary < 0:
                raise ValueError("Зарплата не може бути від'ємною.")
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))
            return

        # Перевірка на вік працівника (не менше 18 років)
        birth_date = datetime.strptime(self.entry_birth.get(), '%Y-%m-%d')
        if datetime.now() - birth_date < timedelta(days=18 * 365):
            messagebox.showerror("Помилка", "Вік працівника має бути не менше 18 років.")
            return

        # Перевірка на довжину номеру телефону
        if len(self.entry_phone.get()) > 13:
            messagebox.showerror("Помилка", "Номер телефону не може перевищувати 13 символів.")
            return

        # Хешування паролю
        password_hash = hashlib.sha256(self.entry_password.get().encode()).hexdigest()

        # Запит до бази даних
        if self.employee:  # Оновлення існуючого запису
            query = """UPDATE Employee SET empl_surname=%s, empl_name=%s, empl_patronymic=%s, empl_role=%s, salary=%s, date_of_birth=%s, date_of_start=%s, phone_number=%s, city=%s, street=%s, zip_code=%s, login=%s, password=%s WHERE id_employee=%s"""
            params = (
            self.entry_surname.get(), self.entry_name.get(), self.entry_patronymic.get(), self.combo_role.get(),
            self.entry_salary.get(), self.entry_birth.get(), self.entry_start.get(), self.entry_phone.get(),
            self.entry_city.get(), self.entry_street.get(), self.entry_zip.get(), self.entry_login.get(), password_hash,
            self.entry_id.get())
        else:  # Додавання нового запису
            query = """INSERT INTO Employee (id_employee, empl_surname, empl_name, empl_patronymic, empl_role, salary, date_of_birth, date_of_start, phone_number, city, street, zip_code, login, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            params = (self.entry_id.get(), self.entry_surname.get(), self.entry_name.get(), self.entry_patronymic.get(),
                      self.combo_role.get(), self.entry_salary.get(), self.entry_birth.get(), self.entry_start.get(),
                      self.entry_phone.get(), self.entry_city.get(), self.entry_street.get(), self.entry_zip.get(),
                      self.entry_login.get(), password_hash)

        try:
            self.db_manager.execute_non_query(query, params)
            messagebox.showinfo("Успіх", "Дані працівника успішно збережено.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка збереження даних: {e}")

class EmployeeViewWindow(tk.Toplevel):
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.title("Відомості про працівників")
        self.db_manager = db_manager
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("id_employee", "empl_surname", "empl_name", "empl_patronymic", "empl_role", "salary", "date_of_birth", "date_of_start", "phone_number", "city", "street", "zip_code", "login"), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=100)
        self.tree.pack(expand=True, fill=tk.BOTH)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Оновити/Скинути", command=self.load_data).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Фільтр по касирах", command=self.filter_cashiers).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сортувати за прізвищем", command=self.sort_by_surname).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Пошук за прізвищем", command=self.search_by_surname).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Додати працівника", command=lambda: self.add_edit_employee(edit=False)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редагувати працівника", command=lambda: self.add_edit_employee(edit=True)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Видалити працівника", command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Друкувати звіт", command=self.print_report).pack(side=tk.LEFT, padx=5)

        self.load_data()

    def load_data(self):
        query = "SELECT * FROM Employee"
        result = self.db_manager.execute_query(query)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def search_by_surname(self):
        surname = simpledialog.askstring("Пошук", "Введіть прізвище працівника:")
        if surname:
            query = """
            SELECT id_employee, empl_surname, empl_name, empl_patronymic, empl_role, salary, date_of_birth, date_of_start, phone_number, city, street, zip_code
            FROM Employee
            WHERE empl_surname LIKE %s
            ORDER BY empl_surname ASC
            """
            result = self.db_manager.execute_query(query, ('%' + surname + '%',))
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in result:
                self.tree.insert("", tk.END, values=row)
        else:
            messagebox.showinfo("Пошук", "Введення прізвища обов'язкове для пошуку.")

    def sort_by_surname(self):
        query = "SELECT * FROM Employee ORDER BY empl_surname"
        result = self.db_manager.execute_query(query)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def filter_cashiers(self):
        query = "SELECT * FROM Employee WHERE empl_role = 'cashier' ORDER BY empl_surname"
        result = self.db_manager.execute_query(query)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def add_edit_employee(self, edit=False):
        selected_item = self.tree.selection()
        employee = None
        if edit and selected_item:
            employee_id = self.tree.item(selected_item, 'values')[0]
            try:
                query = "SELECT * FROM Employee WHERE id_employee = %s"
                result = self.db_manager.execute_query(query, (employee_id,))
                employee = result[0] if result else None
                if employee:
                    employee = dict(
                        zip(["id_employee", "empl_surname", "empl_name", "empl_patronymic", "empl_role", "salary",
                             "date_of_birth", "date_of_start", "phone_number", "city", "street", "zip_code", "login",
                             "password"], employee))
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося отримати дані працівника: {e}")
                return
        elif edit and not selected_item:
            messagebox.showinfo("Увага", "Будь ласка, виберіть працівника для редагування.")
            return

        dialog = EmployeeDialog(self, self.db_manager, employee)
        self.wait_window(dialog)
        self.load_data()

    def delete_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Увага", "Будь ласка, виберіть працівника для видалення.")
            return

        # Витягуємо ідентифікатор працівника для видалення
        employee_id = self.tree.item(selected_item, 'values')[0]
        response = messagebox.askyesno("Підтвердження",
                                       f"Ви впевнені, що хочете видалити працівника з ID {employee_id}?")
        if response:
            try:
                query = "DELETE FROM Employee WHERE id_employee = %s"
                self.db_manager.execute_non_query(query, (employee_id,))
                self.load_data()  # Оновлюємо список працівників
                messagebox.showinfo("Успіх", "Працівник успішно видалений.")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося видалити працівника через помилку: {e}")

    def print_report(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=7)
        # Припустимо, що маємо 14 стовпців, але хочемо вивести лише перші 12, ширини стовпців налаштовані відповідно
        column_widths = [17, 15, 15, 18, 12, 12, 15, 15, 20, 15, 15, 12]

        # Визначаємо заголовки лише для перших 12 стовпців
        column_headers = ["ID", "Surname", "Name", "Patronymic", "Role", "Salary", "Birthday",
                          "Start of Work", "Phone", "City", "Street", "Zip Code"]
        pdf.set_fill_color(193, 229, 252)  # Світло-блакитний колір для заголовків
        for i, header in enumerate(column_headers):
            pdf.cell(column_widths[i], 8, header, border=1, ln=0, align='C', fill=True)
        pdf.ln()

        # Додавання даних, обмежуючи вивід значеннями до 12-го стовпця включно
        for item in self.tree.get_children():
            row_values = self.tree.item(item, 'values')[:12]  # Беремо лише перші 12 значень з кожного рядка
            for i, value in enumerate(row_values):
                pdf.cell(column_widths[i], 8, str(value), border=1, ln=0)
            pdf.ln()

        # Збереження PDF
        pdf.output("employee_report.pdf")
        messagebox.showinfo("Звіт створено", "Звіт про працівників збережено як 'employee_report.pdf'")