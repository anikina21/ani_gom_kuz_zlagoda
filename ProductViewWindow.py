import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from fpdf import FPDF

class ProductDialog(tk.Toplevel):
    def __init__(self, parent, db_manager, product=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.product = product
        self.title("Додати/Редагувати товар")

        # Вводимо елементи GUI
        tk.Label(self, text="Назва товару:").grid(row=0, column=0)
        self.product_name = tk.Entry(self)
        self.product_name.grid(row=0, column=1)

        tk.Label(self, text="Характеристики:").grid(row=1, column=0)
        self.characteristics = tk.Entry(self)
        self.characteristics.grid(row=1, column=1)

        tk.Label(self, text="Категорія:").grid(row=2, column=0)
        self.category_var = tk.StringVar(self)
        self.category_menu = ttk.Combobox(self, textvariable=self.category_var, state='readonly')
        self.category_menu.grid(row=2, column=1)
        self.load_categories()

        if product:
            # Заповнення форми даними для редагування
            self.product_name.insert(0, product['product_name'])
            self.characteristics.insert(0, product['characteristics'])
            self.category_var.set(product['category_name'])

        tk.Button(self, text="Зберегти", command=self.save_product).grid(row=3, columnspan=2)

    def load_categories(self):
        categories = self.db_manager.execute_query("SELECT category_name FROM Category")
        category_names = [category[0] for category in categories]
        self.category_menu['values'] = category_names

    def save_product(self):
        product_name = self.product_name.get().strip()
        characteristics = self.characteristics.get().strip()
        category_name = self.category_var.get().strip()

        # Перевірка чи всі поля заповнені
        if not product_name or not characteristics or not category_name:
            messagebox.showerror("Помилка", "Всі поля повинні бути заповнені!")
            return

        category_number = self.db_manager.execute_query(
            "SELECT category_number FROM Category WHERE category_name = %s", (category_name,))[0][0]

        if self.product:
            # Оновлення існуючого товару
            query = """
            UPDATE Product SET product_name = %s, characteristics = %s, category_number = %s
            WHERE id_product = %s
            """
            self.db_manager.execute_non_query(query, (product_name, characteristics, category_number, self.product['id_product']))
        else:
            # Додавання нового товару
            query = "INSERT INTO Product (product_name, category_number, characteristics) VALUES (%s, %s, %s)"
            self.db_manager.execute_non_query(query, (product_name, category_number, characteristics))
        self.destroy()

class ProductViewWindow(tk.Toplevel):
    def __init__(self, master, role, db_manager):
        super().__init__(master)
        self.title("Відомості про товари")
        self.role = role
        self.db_manager = db_manager
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("id_product", "category_name", "product_name", "characteristics"),
                                 show='headings')
        self.tree.heading("id_product", text="Product ID")
        self.tree.heading("category_name", text="Category Name")
        self.tree.heading("product_name", text="Product Name")
        self.tree.heading("characteristics", text="Characteristics")
        for col in self.tree['columns']:
            self.tree.column(col, width=150)
        self.tree.pack(expand=True, fill=tk.BOTH)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Оновити/Скинути", command=self.load_data).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сортувати за назвою", command=lambda: self.sort_data("product_name")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Пошук за назвою", command=self.search_by_name).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Пошук за категорією", command=self.search_by_category).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Друкувати звіт", command=self.print_report).pack(side=tk.LEFT, padx=5)

        if self.role == 'manager':
            tk.Button(btn_frame, text="Додати/Редагувати товар", command=self.add_edit_product).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Видалити товар", command=self.delete_product).pack(side=tk.LEFT, padx=5)

        self.load_data()

    def load_data(self):
        query = """
        SELECT p.id_product, c.category_name, p.product_name, p.characteristics
        FROM Product p
        JOIN Category c ON p.category_number = c.category_number
        ORDER BY p.id_product ASC
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def sort_data(self, column):
        query = f"""
        SELECT p.id_product, c.category_name, p.product_name, p.characteristics
        FROM Product p
        JOIN Category c ON p.category_number = c.category_number
        ORDER BY {column}
        """
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def search_by_name(self):
        name = simpledialog.askstring("Пошук", "Введіть назву товару:")
        query = """
        SELECT p.id_product, c.category_name, p.product_name, p.characteristics
        FROM Product p
        JOIN Category c ON p.category_number = c.category_number
        WHERE p.product_name LIKE %s
        ORDER BY p.product_name ASC
        """
        result = self.db_manager.execute_query(query, ('%' + name + '%',))
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def search_by_category(self):
        category_name = simpledialog.askstring("Пошук", "Введіть назву категорії:")
        query = """
        SELECT p.id_product, c.category_name, p.product_name, p.characteristics
        FROM Product p
        JOIN Category c ON p.category_number = c.category_number
        WHERE c.category_name LIKE %s
        ORDER BY p.product_name ASC
        """
        result = self.db_manager.execute_query(query, ('%' + category_name + '%',))
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def add_edit_product(self):
        selected_item = self.tree.selection()
        product = None
        if selected_item:
            product = {
                'id_product': self.tree.item(selected_item, 'values')[0],
                'product_name': self.tree.item(selected_item, 'values')[2],
                'characteristics': self.tree.item(selected_item, 'values')[3],
                'category_name': self.tree.item(selected_item, 'values')[1]
            }
        product_dialog = ProductDialog(self, self.db_manager, product)
        product_dialog.grab_set()  # Заблокувати доступ до інших вікон до закриття цього діалогу
        self.wait_window(product_dialog)  # Чекати закриття діалогового вікна
        self.load_data()

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Видалення товару", "Будь ласка, виберіть товар для видалення.")
            return
        id_product = self.tree.item(selected_item, 'values')[0]
        query = "DELETE FROM Product WHERE id_product = %s"
        self.db_manager.execute_non_query(query, (id_product,))
        self.load_data()

    def print_report(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Заголовки стовпців
        headers = ["Product ID", "Category Name", "Product Name", "Characteristics"]
        column_widths = [30, 50, 50, 60]  # Приклад розмірів колонок, налаштуйте за потребою
        for i, header in enumerate(headers):
            pdf.cell(column_widths[i], 10, header, border=1, ln=0, align='C')
        pdf.ln(10)  # Перехід на новий рядок

        # Витягуємо дані з TreeView
        for item in self.tree.get_children():
            row_values = self.tree.item(item, 'values')
            for i, value in enumerate(row_values):
                pdf.cell(column_widths[i], 10, str(value), border=1, ln=0, align='C')
            pdf.ln(10)  # Перехід на новий рядок після завершення рядка

        # Збереження PDF
        pdf.output("Product_Report.pdf")
        messagebox.showinfo("PDF Created", "The current view of products has been saved as 'Product_Report.pdf'.")