import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import bcrypt
import hashlib
from tkinter import messagebox
from itertools import chain

from CategoryViewWindow import CategoryViewWindow
from CheckViewWindow import CheckViewWindow
from CreateBillWindow import CreateBillWindow
from CustomerCardViewWindow import CustomerCardViewWindow
from DatabaseManager import DatabaseManager
from EmployeeViewWindow import EmployeeViewWindow
from ProductViewWindow import ProductViewWindow
from QueriesWindow import QueriesWindow
from StoreProductsWindow import StoreProductsWindow

global user_data
user_data = ""
class UserProfileWindow(tk.Toplevel):
    def __init__(self, master, user_data):
        super().__init__(master)
        self.user_data = user_data
        self.title("Профіль користувача")
        self.geometry("400x300")  # Приклад розмірів вікна
        #user_data_split = [word for phrase in self.user_data for word in phrase.split()]
        self.create_widgets(user_data)

    def create_widgets(self, user_data):
        # Передбачаємо, що user_data це рядок, розділяємо його на слова
        print(type(user_data[0][0]))
        #user_data_split = user_data[0].split()

        # Виводимо кожне слово в окремій мітці
        for index, value in enumerate(user_data[0][:-2]):
            ttk.Label(self, text=value).grid(row=index, column=0, padx=2, pady=2, sticky="ew")

        ttk.Button(self, text="Закрити", command=self.destroy).grid(row=13, column=0, columnspan=2, sticky="ew")


class LoginWindow(tk.Toplevel):
    def __init__(self, master, show_manager_callback, db_manager):
        super().__init__(master)
        self.title("Авторизація")
        self.geometry("550x400")
        self.show_manager_callback = show_manager_callback
        self.db_manager = db_manager

        #tk.Label(self, text="Магазин Злагода", font=('Helvetica', 16)).pack(pady=10)
        original_image = Image.open("logo.png")  # Змініть на вірний шлях до файлу
        resized_image = original_image.resize((250, 125))  # Змінюємо розмір зображення
        self.logo_image = ImageTk.PhotoImage(resized_image)

        # Створюємо Label, який буде відображати зображення
        logo_label = tk.Label(self, image=self.logo_image)
        logo_label.pack(pady=20)

        tk.Label(self, text="Логін:").pack(pady=5)
        self.entry_username = tk.Entry(self)
        self.entry_username.pack(pady=5)
        tk.Label(self, text="Пароль:").pack(pady=5)
        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        tk.Button(self, text="Вхід", command=self.check_login).pack(pady=20)

    def check_login(self):
        global user_data
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Згенерувати хеш введеного паролю
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Запит до бази даних для перевірки логіну та хешу паролю
        query = "SELECT password, empl_role, id_employee, empl_surname, empl_name FROM Employee WHERE login = %s"
        result = self.db_manager.execute_query(query, (username,))

        if result and result[0][0] == password_hash:
            # Якщо хеші співпадають, викликаємо функцію для показу відповідного інтерфейсу
            query = "SELECT * FROM Employee WHERE login = %s"
            user_data = self.db_manager.execute_query(query, (username,))
            self.show_manager_callback(result[0][1])
        else:
            # Якщо немає співпадінь, показуємо помилку
            messagebox.showerror("Помилка", "Неправильний логін або пароль")

    def clear_fields(self):
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)


class ManagerWindow(tk.Toplevel):

    def __init__(self, master, logout_callback, role, db_manager):
        super().__init__(master)
        self.title("Панель управління")
        self.geometry("600x500")
        self.logout_callback = logout_callback
        self.role = role
        self.db_manager = db_manager

        # Визначення стандартної ширини для кнопок
        button_width = 35

        label = tk.Label(self, text=f"Вітаю, {role}!", font=('Helvetica', 16))
        label.pack(pady=20)

        btn_view_category = tk.Button(self, text="Переглянути відомості про категорію", command=self.view_category, width=button_width)
        btn_view_category.pack(pady=10)
        btn_view_product = tk.Button(self, text="Переглянути відомості про товар", command=self.view_product, width=button_width)
        btn_view_product.pack(pady=10)
        btn_view_store_products = tk.Button(self, text="Товари в магазині", command=self.view_store_products, width=button_width)
        btn_view_store_products.pack(pady=10)
        btn_view_customers = tk.Button(self, text="Переглянути відомості про клієнтів", command=self.view_customers, width=button_width)
        btn_view_customers.pack(pady=10)
        if self.role == 'manager':
            btn_view_employees = tk.Button(self, text="Переглянути відомості про працівників", command=self.view_employee, width=button_width)
            btn_view_employees.pack(pady=10)

        if self.role == 'cashier':
            btn_add_bill = tk.Button(self, text="Додати чек", command=self.add_bill, width=button_width)
            btn_add_bill.pack(pady=10)

        btn_view_checks = tk.Button(self, text="Переглянути чеки", command=self.view_checks, width=button_width)
        btn_view_checks.pack(pady=10)

        btn_queries = tk.Button(self, text="Запити", command=self.show_queries_window, width=button_width)
        btn_queries.pack(pady=10)
        btn_profile = tk.Button(self, text="Мій профіль", command=self.show_user_profile, width=button_width)
        btn_profile.pack(pady=10)

        btn_logout = tk.Button(self, text="Вихід", command=self.logout)
        btn_logout.pack(pady=20)

    def view_category(self):
        CategoryViewWindow(self, self.role, self.db_manager)

    def view_checks(self):
        CheckViewWindow(self, self.role, self.db_manager, user_data)

    def view_product(self):
        # Відкриття вікна товарів
        ProductViewWindow(self, self.role, self.db_manager)

    def view_store_products(self):
        StoreProductsWindow(self, self.role, self.db_manager)

    def view_customers(self):
        # Відкриття вікна карток клієнтів
        CustomerCardViewWindow(self, self.role, self.db_manager)
    def view_employee(self):
        # Відкриття вікна працівників
        EmployeeViewWindow(self, self.db_manager)

    def show_user_profile(self):
        global user_data
        profile_window = UserProfileWindow(self, user_data)
        profile_window.grab_set()

    def show_queries_window(self):
        QueriesWindow(self, self.db_manager)

    def add_bill(self):
        CreateBillWindow(self, self.db_manager, user_data)

    def logout(self):
        self.logout_callback()


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Приховуємо головне вікно

        # Ініціалізація менеджера бази даних
        self.db_manager = DatabaseManager(
            host="localhost",
            user="root",
            password="root",
            database="shop"
        )
        self.login_window = LoginWindow(self, self.show_manager_window, self.db_manager)
        self.manager_window = None  # Ініціалізується після логіну

    def show_manager_window(self, role):
        self.login_window.withdraw()
        if self.manager_window:
            self.manager_window.destroy()
        self.manager_window = ManagerWindow(self, self.show_login_window, role, self.db_manager)
        self.manager_window.deiconify()

    def show_login_window(self):
        if self.manager_window:
            self.manager_window.destroy()
        self.login_window.clear_fields()
        self.login_window.deiconify()
'''
        self.login_window = LoginWindow(self, self.show_manager_window, self.db_manager)
        self.manager_window = ManagerWindow(self, self.show_login_window)

    def show_manager_window(self):
        self.login_window.withdraw()
        self.manager_window.deiconify()

    def show_login_window(self):
        self.manager_window.withdraw()
        self.login_window.clear_fields()
        self.login_window.deiconify()
'''

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()