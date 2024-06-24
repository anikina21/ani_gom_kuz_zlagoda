import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from fpdf import FPDF

# Клас для створення PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Category Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


class CategoryViewWindow(tk.Toplevel):
    def __init__(self, master, role, db_manager):
        super().__init__(master)
        self.title("Відомості про категорії")
        self.role = role
        self.db_manager = db_manager
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("category_number", "category_name"), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=150)
        self.tree.pack(expand=True, fill=tk.BOTH)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Скинути", command=self.load_data).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сортувати за назвою", command=self.sort_by_name).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Друкувати звіт", command=self.print_report).pack(side=tk.LEFT, padx=5)

        if self.role == 'manager':
            tk.Button(btn_frame, text="Додати/Редагувати категорію", command=self.modify_category).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Видалити", command=self.delete_category).pack(side=tk.LEFT, padx=5)

        self.load_data()

    def load_data(self):
        query = "SELECT * FROM Category"
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def sort_by_name(self):
        query = "SELECT * FROM Category ORDER BY category_name"
        result = self.db_manager.execute_query(query)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in result:
            self.tree.insert("", tk.END, values=row)

    def print_report(self):
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Визначення ширини та висоти комірок
        cell_width = 90
        cell_height = 10

        # Додавання заголовків для стовпців
        pdf.cell(cell_width, cell_height, "Category Number", border=1, ln=0)
        pdf.cell(cell_width, cell_height, "Category Name", border=1, ln=1)  # ln=1 означає перехід на новий рядок

        # Витягуємо дані з TreeView
        for item in self.tree.get_children():
            category_number, category_name = self.tree.item(item, 'values')
            pdf.cell(cell_width, cell_height, str(category_number), border=1, ln=0)
            pdf.cell(cell_width, cell_height, category_name, border=1, ln=1)  # Кожен новий рядок для нової категорії

        # Збереження PDF
        pdf.output("Category_Report.pdf")
        messagebox.showinfo("PDF Created", "The sorted category report has been created as 'Category_Report.pdf'.")
    def modify_category(self):
        selected_item = self.tree.selection()
        category_number = None
        category_name = ""

        if selected_item:
            category_number, category_name = self.tree.item(selected_item, 'values')

        def save_category():
            new_category_name = entry_name.get().strip()  # Видаляємо пробіли з початку та кінця

            if not new_category_name:  # Перевірка чи назва категорії не є порожньою
                messagebox.showerror("Error", "The category name cannot be empty.")
                return  # Припиняємо виконання функції, якщо поле порожнє

            if category_number:
                query = "UPDATE Category SET category_name = %s WHERE category_number = %s"
                self.db_manager.execute_non_query(query, (entry_name.get(), category_number))
            else:
                query = "INSERT INTO Category (category_name) VALUES (%s)"
                self.db_manager.execute_non_query(query, (entry_name.get(),))
            self.load_data()
            modify_window.destroy()

        modify_window = tk.Toplevel(self)
        modify_window.title("Add/Edit Category")

        tk.Label(modify_window, text="Category Name:").grid(row=0, column=0, padx=10, pady=10)
        entry_name = tk.Entry(modify_window)
        entry_name.grid(row=0, column=1, padx=10, pady=10)
        entry_name.insert(0, category_name)

        tk.Button(modify_window, text="Save Category", command=save_category).grid(row=1, column=0, columnspan=2, pady=10)

    def delete_category(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Delete Category", "Please select a category to delete.")
            return
        category_number = self.tree.item(selected_item, 'values')[0]
        query = "DELETE FROM Category WHERE category_number = %s"
        self.db_manager.execute_non_query(query, (category_number,))
        self.load_data()