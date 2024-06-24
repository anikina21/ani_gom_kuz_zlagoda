import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from fpdf import FPDF


class ProductDialog(tk.Toplevel):
    def __init__(self, master, db_manager, product=None):
        super().__init__(master)
        self.db_manager = db_manager
        self.product = product
        self.title("Додати / Редагувати товар")
        self.geometry("400x400")

        self.create_widgets()
        if self.product:
            self.fill_data()

    def create_widgets(self):
        tk.Label(self, text="UPC:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_upc = tk.Entry(self)
        self.entry_upc.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="UPC промо:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_upc_prom = tk.Entry(self)
        self.entry_upc_prom.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text="ID продукту:").grid(row=2, column=0, padx=10, pady=5)
        self.combo_id_product = ttk.Combobox(self)
        self.combo_id_product.grid(row=2, column=1, padx=10, pady=5)
        self.combo_id_product.bind("<<ComboboxSelected>>", self.on_product_selected)

        tk.Label(self, text="Назва продукту:").grid(row=3, column=0, padx=10, pady=5)
        self.label_product_name = tk.Label(self, text="")
        self.label_product_name.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self, text="Характеристики:").grid(row=4, column=0, padx=10, pady=5)
        self.label_characteristics = tk.Label(self, text="")
        self.label_characteristics.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self, text="Ціна:").grid(row=5, column=0, padx=10, pady=5)
        self.entry_selling_price = tk.Entry(self)
        self.entry_selling_price.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(self, text="Кількість:").grid(row=6, column=0, padx=10, pady=5)
        self.entry_products_number = tk.Entry(self)
        self.entry_products_number.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(self, text="Промо продукт:").grid(row=7, column=0, padx=10, pady=5)
        self.entry_promotional_product = ttk.Combobox(self, values=["0", "1"])
        self.entry_promotional_product.grid(row=7, column=1, padx=10, pady=5)

        tk.Button(self, text="Зберегти", command=self.save_product).grid(row=8, column=0, columnspan=2, pady=10)

        self.load_product_options()

    def load_product_options(self):
        query = "SELECT id_product, product_name FROM Product"
        result = self.db_manager.execute_query(query)
        product_options = {str(row[0]): row[1] for row in result}
        self.combo_id_product['values'] = list(product_options.keys())
        self.product_options = product_options

    def on_product_selected(self, event):
        selected_id = self.combo_id_product.get()
        query = "SELECT product_name, characteristics FROM Product WHERE id_product = %s"
        result = self.db_manager.execute_query(query, (selected_id,))
        if result:
            self.label_product_name.config(text=result[0][0])
            self.label_characteristics.config(text=result[0][1])

    def fill_data(self):
        self.entry_upc.insert(0, self.product['UPC'])
        if self.product['UPC_prom']:
            self.entry_upc_prom.insert(0, self.product['UPC_prom'])
        self.combo_id_product.set(str(self.product['id_product']))
        self.label_product_name.config(text=self.product['product_name'])
        self.label_characteristics.config(text=self.product['characteristics'])
        self.entry_selling_price.insert(0, self.product['selling_price'])
        self.entry_products_number.insert(0, self.product['products_number'])
        self.entry_promotional_product.set(str(self.product['promotional_product']))

    def save_product(self):
        upc = self.entry_upc.get().strip()
        upc_prom = self.entry_upc_prom.get().strip() or None
        id_product = self.combo_id_product.get().strip()
        selling_price = self.entry_selling_price.get().strip()
        products_number = self.entry_products_number.get().strip()
        promotional_product = self.entry_promotional_product.get().strip()

        if not all([upc, id_product, selling_price, products_number, promotional_product]):
            messagebox.showerror("Помилка", "Всі поля мають бути заповнені.")
            return

        try:
            selling_price = float(selling_price)
            products_number = int(products_number)
            promotional_product = int(promotional_product)
        except ValueError:
            messagebox.showerror("Помилка", "Ціна повинна бути числом. Кількість повинна бути цілим числом.")
            return

        if selling_price < 0:
            messagebox.showerror("Помилка", "Ціна не може бути від'ємною.")
            return

        if products_number < 0:
            messagebox.showerror("Помилка", "Кількість не може бути від'ємною.")
            return

        if promotional_product not in [0, 1]:
            messagebox.showerror("Помилка", "Промо продукт повинен бути 0 або 1.")
            return

        try:
            if self.product:  # Оновлення
                query = """
                UPDATE Store_Product
                SET UPC_prom=%s, id_product=%s, selling_price=%s, products_number=%s, promotional_product=%s
                WHERE UPC=%s
                """
                self.db_manager.execute_non_query(query, (
                upc_prom, id_product, selling_price, products_number, promotional_product, upc))

                if promotional_product == 0:
                    # Оновити ціну акційного товару
                    query = "UPDATE Store_Product SET selling_price = %s * 0.8 WHERE UPC_prom = %s"
                    self.db_manager.execute_non_query(query, (selling_price, upc))
            else:  # Додавання
                if promotional_product == 1:
                    # Перевірка наявності неакційного товару
                    query = "SELECT UPC FROM Store_Product WHERE id_product = %s AND promotional_product = 0"
                    result = self.db_manager.execute_query(query, (id_product,))
                    if not result:
                        messagebox.showerror("Помилка", "Не може існувати акційний товар без неакційного.")
                        return
                query = """
                INSERT INTO Store_Product (UPC, UPC_prom, id_product, selling_price, products_number, promotional_product)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.db_manager.execute_non_query(query, (
                upc, upc_prom, id_product, selling_price, products_number, promotional_product))

                if promotional_product == 0:
                    # Оновити ціну акційного товару
                    query = "UPDATE Store_Product SET selling_price = %s * 0.8 WHERE UPC_prom = %s"
                    self.db_manager.execute_non_query(query, (selling_price, upc))

            messagebox.showinfo("Успіх", "Товар успішно збережено.")
            self.destroy()
            self.master.load_data()
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти товар: {e}")