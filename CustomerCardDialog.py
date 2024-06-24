import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class CustomerCardDialog(tk.Toplevel):
    def __init__(self, parent, db_manager, card=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.card = card
        self.title("Додати / Редагувати картку клієнта")

        # Поля для введення даних
        tk.Label(self, text="Номер картки:").grid(row=0, column=0, padx=10, pady=10)
        self.entry_card_number = tk.Entry(self)
        self.entry_card_number.grid(row=0, column=1, padx=10, pady=10)
        if not self.card:  # Дозволяємо ввести номер картки тільки при створенні нової картки
            self.entry_card_number.config(state='normal')
        else:
            self.entry_card_number.insert(0, self.card['card_number'])
            self.entry_card_number.config(state='readonly')  # Робимо поле тільки для читання при редагуванні

        tk.Label(self, text="Прізвище:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_surname = tk.Entry(self)
        self.entry_surname.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self, text="Ім'я:").grid(row=2, column=0, padx=10, pady=10)
        self.entry_name = tk.Entry(self)
        self.entry_name.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self, text="По батькові:").grid(row=3, column=0, padx=10, pady=10)
        self.entry_patronymic = tk.Entry(self)
        self.entry_patronymic.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self, text="Телефон:").grid(row=4, column=0, padx=10, pady=10)
        self.entry_phone = tk.Entry(self)
        self.entry_phone.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(self, text="Місто:").grid(row=5, column=0, padx=10, pady=10)
        self.entry_city = tk.Entry(self)
        self.entry_city.grid(row=5, column=1, padx=10, pady=10)

        tk.Label(self, text="Вулиця:").grid(row=6, column=0, padx=10, pady=10)
        self.entry_street = tk.Entry(self)
        self.entry_street.grid(row=6, column=1, padx=10, pady=10)

        tk.Label(self, text="Поштовий індекс:").grid(row=7, column=0, padx=10, pady=10)
        self.entry_zip_code = tk.Entry(self)
        self.entry_zip_code.grid(row=7, column=1, padx=10, pady=10)

        tk.Label(self, text="Відсоток:").grid(row=8, column=0, padx=10, pady=10)
        self.entry_percent = tk.Entry(self)
        self.entry_percent.grid(row=8, column=1, padx=10, pady=10)

        # Кнопка для збереження
        tk.Button(self, text="Зберегти", command=self.save_card).grid(row=9, column=0, columnspan=2, pady=10)

        # Заповнення полів даними при редагуванні
        if self.card:
            self.entry_surname.insert(0, self.card['customer_surname'])
            self.entry_name.insert(0, self.card['cust_name'])
            self.entry_patronymic.insert(0, self.card.get('cust_patronymic', ''))
            self.entry_phone.insert(0, self.card['phone_number'])
            self.entry_city.insert(0, self.card.get('city', ''))
            self.entry_street.insert(0, self.card.get('street', ''))
            self.entry_zip_code.insert(0, self.card.get('zip_code', ''))
            self.entry_percent.insert(0, self.card['percent'])

    def save_card(self):
        # Валідація даних
        card_number = self.entry_card_number.get().strip()
        if not (
                card_number and self.entry_surname.get().strip() and self.entry_name.get().strip() and self.entry_phone.get().strip() and len(
                self.entry_phone.get().strip()) <= 13 and int(self.entry_percent.get()) >= 0):
            messagebox.showerror("Помилка",
                                 "Перевірте правильність введених даних.\nНомер картки, прізвище, ім'я, телефон є обов'язковими. Телефон не може бути довшим за 13 символів та відсоток не може бути від'ємним.")
            return

        # SQL запити для додавання або оновлення інформації
        if self.card:
            query = """UPDATE Customer_Card SET customer_surname=%s, cust_name=%s, cust_patronymic=%s, phone_number=%s, city=%s, street=%s, zip_code=%s, percent=%s WHERE card_number=%s"""
            self.db_manager.execute_non_query(query, (
            self.entry_surname.get(), self.entry_name.get(), self.entry_patronymic.get(), self.entry_phone.get(),
            self.entry_city.get(), self.entry_street.get(), self.entry_zip_code.get(), self.entry_percent.get(),
            card_number))
        else:
            query = """INSERT INTO Customer_Card (card_number, customer_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, percent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.db_manager.execute_non_query(query, (
            card_number, self.entry_surname.get(), self.entry_name.get(), self.entry_patronymic.get(),
            self.entry_phone.get(), self.entry_city.get(), self.entry_street.get(), self.entry_zip_code.get(),
            self.entry_percent.get()))

        messagebox.showinfo("Успішно", "Дані картки клієнта збережено.")
        self.destroy()