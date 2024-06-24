import tkinter as tk
from tkinter import ttk, simpledialog, messagebox


class QueriesWindow(tk.Toplevel):
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.title("Запити")
        self.geometry("1200x600")
        self.db_manager = db_manager
        self.create_widgets()

    def create_widgets(self):
        self.table = ttk.Treeview(self)
        self.table.pack(expand=True, fill=tk.BOTH, pady=10, padx=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_1 = tk.Button(btn_frame, text="(групування) Кількість проданих касиром товарів", command=self.execute_query_1)
        btn_1.pack(fill=tk.X, pady=2)
        btn_2 = tk.Button(btn_frame, text="Клієнти, що купували всі товари з категорії", command=self.execute_query_2)
        btn_2.pack(fill=tk.X, pady=2)
        btn_3 = tk.Button(btn_frame, text="(групування) Найдорожчий товар в категоріях", command=self.execute_query_3)
        btn_3.pack(fill=tk.X, pady=2)
        btn_4 = tk.Button(btn_frame, text="Клієнти, що скуплялись тільки на більше ніж {парам} і їх касир", command=self.execute_query_4)
        btn_4.pack(fill=tk.X, pady=2)
        btn_5 = tk.Button(btn_frame, text="(групування) Кількість куплених продуктів у кожній категорії", command=self.execute_query_5)
        btn_5.pack(fill=tk.X, pady=2)
        btn_6 = tk.Button(btn_frame, text="Працівники, що обслуговували конкретного клієнта", command=self.execute_query_6)
        btn_6.pack(fill=tk.X, pady=2)

    def execute_query_1(self):
        query = """
        SELECT e.id_employee, e.empl_name, e.empl_surname, SUM(Sale.product_number) AS total_products
        FROM Employee AS e
        LEFT JOIN Bill AS ch ON e.id_employee = ch.id_employee
        LEFT JOIN Sale ON ch.check_number = Sale.check_number
        WHERE e.empl_role = 'cashier'
        GROUP BY e.id_employee, e.empl_name, e.empl_surname;
        """
        columns = ["ID Employee", "Name", "Surname", "Total Products"]
        self.execute_and_display(query, columns)

    def execute_query_4(self):
        param = simpledialog.askstring("Клієнти, що скуплялись тільки на більше ніж {парам} і їх касир", "Мінімальну суму чеку:")
        if param:
            query = """
            SELECT C.card_number AS card_number, 
	   C.customer_surname,
       C.cust_name, 
       C.phone_number, 
       C.percent, 
       E.empl_surname AS cashier_surname
FROM `bill` AS Ch
JOIN Customer_Card AS C ON C.card_number = Ch.card_number
JOIN Employee AS E ON E.id_employee = Ch.id_employee
WHERE NOT EXISTS (
    SELECT Ch2.check_number
    FROM `bill` AS Ch2
    JOIN Customer_Card AS C2 ON C2.card_number = Ch2.card_number
    WHERE C2.card_number = C.card_number
    AND Ch2.check_number NOT IN (
        SELECT Ch3.check_number
        FROM `bill` AS Ch3
        WHERE Ch3.sum_total >= %s
    )
)
AND EXISTS (
    SELECT 1
    FROM `bill` AS Ch4
    WHERE Ch4.sum_total >= %s
    AND Ch4.card_number = C.card_number
    AND Ch4.id_employee = E.id_employee
);
            """
            columns = ["card number", "customer surname", "customer name", "phone number", "percent", "cashier surname"]
            self.execute_and_display(query, columns, (param, param))

    def execute_query_3(self):
        query = """
        SELECT C.category_number, C.category_name, P.id_product, P.product_name, SP.selling_price
 FROM (Category AS C
              INNER JOIN Product AS P ON C.category_number = P.category_number)
              INNER JOIN Store_product AS SP ON P.id_product = SP.id_product
WHERE 
    SP.selling_price = (SELECT MAX(SP_inner.selling_price)
                                     FROM 
                                     Store_product AS SP_inner
                                      INNER JOIN Product AS P_inner ON SP_inner.id_product = P_inner.id_product
                                     WHERE P_inner.category_number = C.category_number
                                     GROUP BY P_inner.category_number
                                     )
                                    GROUP BY C.category_number, C.category_name, P.id_product, P.product_name, SP.selling_price;
        """
        columns = ["category number", "category name", "product ID", "product name", "selling_price"]  # Задайте відповідні назви колонок
        self.execute_and_display(query, columns)

    def execute_query_2(self):
        param = simpledialog.askstring("Категорія", "Введіть назву категорії:")
        if param:
            query = """
            SELECT cc.card_number, cc.cust_name, cc.customer_surname
FROM Customer_Card AS cc
WHERE NOT EXISTS (
    SELECT p.id_product
    FROM Product p
    JOIN Category c ON p.category_number = c.category_number
    WHERE c.category_name = %s
    AND NOT EXISTS (
        SELECT 1
        FROM `bill` ch
        JOIN Sale s ON ch.check_number = s.check_number
        JOIN Store_Product sp ON s.UPC = sp.UPC
        WHERE ch.card_number = cc.card_number
        AND sp.id_product = p.id_product
    )
);
            """
            columns = ["card number", "customer name", "customer surname"]
            self.execute_and_display(query, columns, (param,))

    def execute_query_5(self):
        query = """
        SELECT Category.category_number, Category.category_name, SUM(Sale.product_number) AS count_of_products
FROM (Category LEFT JOIN Product ON Category.category_number = Product.category_number) 
LEFT JOIN (Store_product LEFT JOIN Sale ON Store_Product.UPC = Sale.UPC) ON Product.id_product = Store_product.id_product
GROUP BY Category.category_number, Category.category_name;
        """
        columns = ["category number", "category name", "count of products"]
        self.execute_and_display(query, columns)

    def execute_query_6(self):
        param = simpledialog.askstring("Прізвище клієнта", "Введіть прізвище клієнта:")
        if param:
            query = """
            SELECT e.id_employee, e.empl_name, e.empl_surname
FROM Employee AS e
WHERE NOT EXISTS (
    SELECT c.card_number
    FROM Customer_Card c
    WHERE c.customer_surname = %s
    AND NOT EXISTS (
        SELECT ch.id_employee
        FROM `bill` ch
        WHERE ch.card_number = c.card_number
        AND ch.id_employee = e.id_employee
    )
);"""
            columns = ["employee ID", "employee name", "employee surname"]
            self.execute_and_display(query, columns, (param,))

    def execute_and_display(self, query, columns, params=None):
        try:
            print(f"Executing query: {query} with params: {params}")  # Відладкове повідомлення
            result = self.db_manager.execute_query(query, params)
            print(f"Query result: {result}")  # Відладкове повідомлення
            self.update_table(result, columns)
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Помилка", f"Не вдалося виконати запит: {e}")

    def update_table(self, rows, columns):
        print(f"Updating table with columns: {columns} and rows: {rows}")  # Відладкове повідомлення
        # Очистка таблиці
        self.table.delete(*self.table.get_children())

        # Оновлення назв колонок
        self.table["columns"] = columns
        self.table["show"] = "headings"
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center")

        # Додавання рядків у таблицю
        for row in rows:
            cleaned_row = [value if value is not None else '' for value in row]
            print(f"Inserting row: {cleaned_row}")  # Відладкове повідомлення
            self.table.insert("", "end", values=cleaned_row)

        # Оновлення вікна
        self.table.update_idletasks()