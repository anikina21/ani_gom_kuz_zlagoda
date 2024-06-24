from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog

from ProductDialog import ProductDialog


class StoreProductsWindow(tk.Toplevel):
    def __init__(self, master, role, db_manager):
        super().__init__(master)
        self.title("Товари в магазині")
        self.role = role
        self.db_manager = db_manager
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=(
        'UPC', 'UPC_prom', 'id_product', 'product_name', 'characteristics', 'selling_price', 'products_number',
        'promotional_product'), show='headings')
        self.tree.heading('UPC', text='UPC')
        self.tree.heading('UPC_prom', text='UPC промо')
        self.tree.heading('id_product', text='ID продукту')
        self.tree.heading('product_name', text='Назва продукту')
        self.tree.heading('characteristics', text='Характеристики')
        self.tree.heading('selling_price', text='Ціна')
        self.tree.heading('products_number', text='Кількість')
        self.tree.heading('promotional_product', text='Промо продукт')

        # Встановлюємо ширину колонок
        column_widths = {
            'UPC': 120,
            'UPC_prom': 120,
            'id_product': 100,
            'product_name': 150,
            'characteristics': 200,
            'selling_price': 100,
            'products_number': 100,
            'promotional_product': 120
        }
        for col, width in column_widths.items():
            self.tree.column(col, width=width)

        self.tree.pack(expand=True, fill=tk.BOTH, pady=10, padx=10)

        btn_frame_top = tk.Frame(self)
        btn_frame_top.pack(pady=5)

        btn_frame_bottom = tk.Frame(self)
        btn_frame_bottom.pack(pady=5)

        tk.Button(btn_frame_top, text="Оновити/Скинути", command=self.load_data).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame_top, text="Пошук за UPC", command=self.search_by_upc).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame_top, text="Сортувати за назвою", command=self.sort_by_name).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame_top, text="Друк звіту", command=self.print_report).pack(side=tk.LEFT, padx=5)

        if self.role == 'manager':
            tk.Button(btn_frame_bottom, text="Додати товар", command=self.add_product).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame_bottom, text="Редагувати товар", command=self.edit_product).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame_bottom, text="Видалити товар", command=self.delete_product).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame_bottom, text="Поставка", command=self.increase_product_quantity).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame_bottom, text="Списання", command=self.decrease_product_quantity).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame_top, text="Сортувати за кількістю", command=self.sort_by_number).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame_bottom, text="Акційні за назвою", command=self.show_promotional_products_by_name).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame_bottom, text="Акційні за кількістю", command=self.show_promotional_products_by_quantity).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame_bottom, text="Не акційні за назвою", command=self.show_non_promotional_products_by_name).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame_bottom, text="Не акційні за кількістю", command=self.show_non_promotional_products_by_quantity).pack(side=tk.LEFT, padx=5)

        self.load_data()

        # Встановлюємо ширину вікна відповідно до ширини таблиці
        total_width = sum(column_widths.values()) + 20  # Додаємо невеликий відступ
        self.geometry(f"{total_width}x600")

    def load_data(self):
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def add_product(self):
        ProductDialog(self, self.db_manager)

    def edit_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Увага", "Будь ласка, виберіть товар для редагування.")
            return

        upc = self.tree.item(selected_item, 'values')[0]
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        WHERE sp.UPC = %s
        """
        result = self.db_manager.execute_query(query, (upc,))
        if result:
            product_data = {
                'UPC': result[0][0],
                'UPC_prom': result[0][1],
                'id_product': result[0][2],
                'product_name': result[0][3],
                'characteristics': result[0][4],
                'selling_price': result[0][5],
                'products_number': result[0][6],
                'promotional_product': result[0][7]
            }
            ProductDialog(self, self.db_manager, product_data)
        else:
            messagebox.showerror("Помилка", "Не вдалося завантажити дані товару.")

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Увага", "Будь ласка, виберіть товар для видалення.")
            return

        upc = self.tree.item(selected_item, 'values')[0]
        query = "DELETE FROM Store_Product WHERE UPC = %s"

        try:
            self.db_manager.execute_non_query(query, (upc,))
            messagebox.showinfo("Успіх", "Товар успішно видалено.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося видалити товар: {e}")

    def increase_product_quantity(self):
        self.modify_product_quantity("Поставка", "Введіть кількість для поставки:", True)

    def decrease_product_quantity(self):
        self.modify_product_quantity("Списання", "Введіть кількість для списання:", False)

    def modify_product_quantity(self, title, prompt, increase):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Увага", f"Будь ласка, виберіть товар для: {title.lower()}.")
            return

        upc = self.tree.item(selected_item, 'values')[0]
        quantity = simpledialog.askinteger(title, prompt)
        if quantity is None or quantity <= 0:
            messagebox.showwarning("Увага", "Будь ласка, введіть дійсну кількість.")
            return

        current_quantity = int(self.tree.item(selected_item, 'values')[6])
        new_quantity = current_quantity + quantity if increase else current_quantity - quantity
        if new_quantity < 0:
            messagebox.showerror("Помилка", "Кількість товару не може бути від'ємною.")
            return

        query = "UPDATE Store_Product SET products_number = %s WHERE UPC = %s"
        try:
            self.db_manager.execute_non_query(query, (new_quantity, upc))
            messagebox.showinfo("Успіх", f"Кількість товару успішно змінено.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося змінити кількість товару: {e}")

    def search_by_upc(self):
        upc = simpledialog.askstring("Пошук", "Введіть UPC товару:")
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        WHERE sp.UPC = %s
        """
        result = self.db_manager.execute_query(query, (upc,))
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def show_promotional_products(self):
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        WHERE sp.promotional_product = 1
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def show_promotional_products_by_name(self):
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        WHERE sp.promotional_product = 1
        ORDER BY p.product_name
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def show_promotional_products_by_quantity(self):
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        WHERE sp.promotional_product = 1
        ORDER BY sp.products_number
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def show_non_promotional_products_by_name(self):
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        WHERE sp.promotional_product = 0
        ORDER BY p.product_name
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def show_non_promotional_products_by_quantity(self):
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        WHERE sp.promotional_product = 0
        ORDER BY sp.products_number
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def sort_by_name(self):
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        ORDER BY p.product_name
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def sort_by_number(self):
        query = """
        SELECT sp.UPC, sp.UPC_prom, sp.id_product, p.product_name, p.characteristics, sp.selling_price, sp.products_number, sp.promotional_product
        FROM Store_Product sp
        JOIN Product p ON sp.id_product = p.id_product
        ORDER BY sp.products_number
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def print_report(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=7)
        column_widths = [20, 25, 20, 30, 40, 15, 15, 15]  # Ширини колонок повинні відповідати кількості заголовків

        # Заголовки для стовпців
        headers = ["UPC", "UPC prom", "product id", "name", "characteristics", "price", "number", "is promo"]
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
        pdf.output("Store_Products_Report.pdf")
        messagebox.showinfo("Звіт створено", "Звіт про товари в магазині збережено як 'Store_Products_Report.pdf'")