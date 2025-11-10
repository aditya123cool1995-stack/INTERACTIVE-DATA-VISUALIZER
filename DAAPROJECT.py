import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import mysql.connector
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random

global db_name
global db_pass
db_name = "dashboard_db"
db_pass = "Menu32sa#"

# ----------- DAA ALGORITHMS -----------
def bubble_sort(arr):
    n = len(arr)
    steps = []
    arr = arr.copy()
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
            steps.append(arr.copy())
    return arr, steps

def binary_search(arr, x):
    arr = sorted(arr)
    l, r = 0, len(arr)-1
    steps = []
    while l <= r:
        mid = (l + r) // 2
        steps.append((l, mid, r))
        if arr[mid] == x:
            return mid, steps
        elif arr[mid] < x:
            l = mid + 1
        else:
            r = mid - 1
    return -1, steps

# ----------- AUTHENTICATION -----------

def authenticate(username, password):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        connection.close()
        return user is not None
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return False

def register_user(username, password):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()
        connection.close()
        messagebox.showinfo("Success", "User registered successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")


class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interactive Data Visualization Dashboard")
        self.geometry("600x400")
        self.init_login_screen()

    def generate_captcha(self):
        self.captcha_num1 = random.randint(1, 10)
        self.captcha_num2 = random.randint(1, 10)
        self.captcha_answer = self.captcha_num1 + self.captcha_num2

    def reset_captcha(self, label_widget, entry_widget):
        self.generate_captcha()
        label_widget.config(text=f"Solve: {self.captcha_num1} + {self.captcha_num2} = ")
        entry_widget.delete(0, tk.END)

    def add_captcha_to_frame(self, frame):
        self.generate_captcha()
        label = tk.Label(frame, text=f"Solve: {self.captcha_num1} + {self.captcha_num2} = ")
        label.grid(row=3, column=0)
        entry = tk.Entry(frame)
        entry.grid(row=3, column=1)
        reset_btn = tk.Button(frame, text="Reset CAPTCHA", command=lambda: self.reset_captcha(label, entry))
        reset_btn.grid(row=4, column=1)
        self.captcha_entry = entry
        return label, entry

    def init_login_screen(self):
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(pady=50)

        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0)
        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0)

        self.username_entry = tk.Entry(self.login_frame)
        self.password_entry = tk.Entry(self.login_frame, show="*")

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        self.captcha_label, self.captcha_entry = self.add_captcha_to_frame(self.login_frame)

        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=5, column=1, pady=10)
        tk.Button(self.login_frame, text="Register", command=self.register_user_prompt).grid(row=6, column=1, pady=5)

    def login(self):
        try:
            captcha_input = int(self.captcha_entry.get())
        except ValueError:
            messagebox.showerror("CAPTCHA Error", "Please enter a valid number for CAPTCHA.")
            return

        if captcha_input != self.captcha_answer:
            messagebox.showerror("CAPTCHA Error", "Incorrect CAPTCHA answer.")
            return

        username = self.username_entry.get()
        password = self.password_entry.get()
        if authenticate(username, password):
            messagebox.showinfo("Login", "Login successful!")
            self.login_frame.destroy()
            self.init_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def register_user_prompt(self):
        reg_window = tk.Toplevel(self)
        reg_window.title("Register New User")
        reg_window.geometry("300x250")

        tk.Label(reg_window, text="Enter Username:").grid(row=0, column=0, pady=10)
        username_entry = tk.Entry(reg_window)
        username_entry.grid(row=0, column=1)

        tk.Label(reg_window, text="Enter Password:").grid(row=1, column=0, pady=10)
        password_entry = tk.Entry(reg_window, show="*")
        password_entry.grid(row=1, column=1)

        self.generate_captcha()
        captcha_label = tk.Label(reg_window, text=f"Solve: {self.captcha_num1} + {self.captcha_num2} = ")
        captcha_label.grid(row=2, column=0)
        captcha_entry = tk.Entry(reg_window)
        captcha_entry.grid(row=2, column=1)
        reset_btn = tk.Button(reg_window, text="Reset CAPTCHA", command=lambda: self.reset_captcha(captcha_label, captcha_entry))
        reset_btn.grid(row=3, column=1)

        def register():
            try:
                captcha_input = int(captcha_entry.get())
            except ValueError:
                messagebox.showerror("CAPTCHA Error", "Enter a valid number in CAPTCHA.")
                return

            if captcha_input != self.captcha_answer:
                messagebox.showerror("CAPTCHA Error", "Incorrect CAPTCHA answer.")
                return

            username = username_entry.get()
            password = password_entry.get()
            register_user(username, password)
            reg_window.destroy()

        tk.Button(reg_window, text="Register", command=register).grid(row=4, column=1, pady=20)

    def init_dashboard(self):
        self.dashboard_frame = tk.Frame(self)
        self.dashboard_frame.pack(pady=20)

        tk.Button(self.dashboard_frame, text="Load Dataset", command=self.load_dataset).pack(pady=10)
        tk.Button(self.dashboard_frame, text="Exit", command=self.destroy).pack(pady=10)
        tk.Button(self.dashboard_frame, text="DAA Algorithms", command=self.open_daa_section).pack(pady=10)

        self.stats_panel = tk.Label(self, text="", font=("Helvetica", 12))
        self.stats_panel.pack()

    def show_progress(self):
        progress = ttk.Progressbar(self, orient="horizontal", length=250, mode="determinate")
        progress.pack(pady=20)
        self.update_idletasks()
        for i in range(101):
            progress['value'] = i
            self.update_idletasks()
        progress.pack_forget()

    def load_dataset(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.show_progress()
            self.df = pd.read_csv(file_path)
            self.dashboard_frame.pack_forget()
            self.show_stats_panel()
            self.show_column_selection()

    def show_stats_panel(self):
        row_count = len(self.df)
        col_count = len(self.df.columns)
        stats = f"Rows: {row_count}, Columns: {col_count}"
        means = []
        for col in self.df.select_dtypes(include='number').columns:
            mean_val = self.df[col].mean()
            means.append(f"{col} Mean: {mean_val:.2f}")
        stats += ("\n" + "\n".join(means)) if means else ""
        self.stats_panel.config(text=stats)

    def show_column_selection(self):
        self.column_selection_frame = tk.Frame(self)
        self.column_selection_frame.pack(pady=10, expand=True, fill='both')

        selection_container = tk.Frame(self.column_selection_frame)
        selection_container.pack(expand=True)

        tk.Label(selection_container, text="Select Columns for Plotting:").pack()

        self.select_all_var = tk.IntVar(value=0)
        select_all_chk = tk.Checkbutton(selection_container, text="Select All", variable=self.select_all_var, command=self.select_all_columns)
        select_all_chk.pack(anchor=tk.W)

        self.column_vars = {}
        for col in self.df.columns:
            var = tk.IntVar()
            chk = tk.Checkbutton(selection_container, text=col, variable=var)
            chk.pack(anchor=tk.W)
            self.column_vars[col] = var

        tk.Button(selection_container, text="Next", command=self.show_plot_type_selection).pack(pady=10)

    def select_all_columns(self):
        select_all = self.select_all_var.get() == 1
        for var in self.column_vars.values():
            var.set(1 if select_all else 0)

    def show_plot_type_selection(self):
        self.selected_columns = [col for col, var in self.column_vars.items() if var.get() == 1]

        if not self.selected_columns:
            messagebox.showerror("Error", "Please select at least one column.")
            return

        self.column_selection_frame.pack_forget()

        self.plot_type_frame = tk.Frame(self)
        self.plot_type_frame.pack(pady=10, fill="both", expand=True)

        tk.Label(self.plot_type_frame, text="Choose Plot Type:").pack(pady=10)

        plot_types = ["Bar Plot", "Violin Plot", "Scatter Plot", "Line Plot", "Histogram", "Box Plot"]
        self.plot_type_var = tk.StringVar(value="Bar Plot")

        radio_frame = tk.Frame(self.plot_type_frame)
        radio_frame.pack(pady=10)

        for plot in plot_types:
            tk.Radiobutton(radio_frame, text=plot, variable=self.plot_type_var, value=plot).pack(anchor=tk.W)

        self.filter_sliders = {}
        num_cols = [col for col in self.selected_columns if pd.api.types.is_numeric_dtype(self.df[col])]
        if num_cols:
            tk.Label(self.plot_type_frame, text="Filter range for columns:").pack(pady=5)
            for col in num_cols:
                minv, maxv = int(self.df[col].min()), int(self.df[col].max())
                slider = tk.Scale(self.plot_type_frame, from_=minv, to=maxv, orient=tk.HORIZONTAL, label=f"{col} (≤ value)")
                slider.set(maxv)
                slider.pack()
                self.filter_sliders[col] = slider

        tk.Button(self.plot_type_frame, text="Generate Plot", command=self.generate_plot).pack(pady=10)

    def filter_data(self):
        data = self.df[self.selected_columns]
        for col, slider in self.filter_sliders.items():
            max_val = slider.get()
            data = data[data[col] <= max_val]
        return data

    def generate_plot(self):
        plot_type = self.plot_type_var.get()
        data_to_plot = self.filter_data() if hasattr(self, "filter_sliders") else self.df[self.selected_columns]
        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        try:
            if plot_type == "Bar Plot":
                sns.barplot(data=data_to_plot, ax=ax)
            elif plot_type == "Violin Plot":
                sns.violinplot(data=data_to_plot, ax=ax)
            elif plot_type == "Scatter Plot":
                if len(self.selected_columns) >= 2:
                    sns.scatterplot(x=self.selected_columns[0], y=self.selected_columns[1], data=data_to_plot, ax=ax)
                else:
                    messagebox.showerror("Plot Error", "Scatter plot requires at least two columns.")
                    return
            elif plot_type == "Line Plot":
                sns.lineplot(data=data_to_plot, ax=ax)
            elif plot_type == "Histogram":
                data_to_plot.hist(ax=ax, bins=15)
            elif plot_type == "Box Plot":
                sns.boxplot(data=data_to_plot, ax=ax)
            self.show_embedded_plot(fig)
        except Exception as e:
            messagebox.showerror("Plot Error", str(e))

    def show_embedded_plot(self, fig):
        plot_win = tk.Toplevel(self)
        plot_win.title("Plot Viewer")
        canvas = FigureCanvasTkAgg(fig, master=plot_win)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, plot_win)
        toolbar.update()
        canvas.get_tk_widget().pack()

    # ----------- DAA GUI SECTION -----------
    def open_daa_section(self):
        self.daa_frame = tk.Toplevel(self)
        self.daa_frame.title("Run DAA Algorithms")
        self.daa_frame.geometry("400x350")

        algo_var = tk.StringVar(value="Bubble Sort")
        tk.Label(self.daa_frame, text="Choose Algorithm:").pack(pady=5)
        tk.Radiobutton(self.daa_frame, text="Bubble Sort", variable=algo_var, value="Bubble Sort").pack(anchor=tk.W)
        tk.Radiobutton(self.daa_frame, text="Binary Search", variable=algo_var, value="Binary Search").pack(anchor=tk.W)

        tk.Label(self.daa_frame, text="Input List (comma separated):").pack(pady=5)
        arr_entry = tk.Entry(self.daa_frame)
        arr_entry.pack()

        tk.Label(self.daa_frame, text="Target (for Binary Search):").pack(pady=5)
        target_entry = tk.Entry(self.daa_frame)
        target_entry.pack()

        result_text = tk.Text(self.daa_frame, height=10, width=40)
        result_text.pack(pady=10)

        def run_algorithm():
            arr = [int(x.strip()) for x in arr_entry.get().split(',') if x.strip().isdigit()]
            result_text.delete("1.0", tk.END)
            if algo_var.get() == "Bubble Sort":
                sorted_arr, steps = bubble_sort(arr)
                result_text.insert(tk.END, f"Sorted: {sorted_arr}\n\nSteps:\n")
                for s in steps:
                    result_text.insert(tk.END, f"{s}\n")
            elif algo_var.get() == "Binary Search":
                if target_entry.get().strip().isdigit():
                    idx, steps = binary_search(arr, int(target_entry.get()))
                    msg = f"Found at index: {idx}\nSteps: {steps}" if idx != -1 else "Not found"
                    result_text.insert(tk.END, msg)
                else:
                    result_text.insert(tk.END, "Please provide a valid target value.")

        tk.Button(self.daa_frame, text="Run", command=run_algorithm).pack(pady=5)


if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
