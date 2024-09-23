import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from difflib import Differ
import re


class JSONCompareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Comparison Tool")
        self.root.geometry("1200x800")

        self.compare_mode = tk.StringVar(value="full")
        self.ignore_whitespace = tk.BooleanVar(value=False)
        self.create_widgets()
        self.json1_text.tag_configure('search', background='yellow')
        self.json2_text.tag_configure('search', background='yellow')
        self.set_light_theme()

    def create_widgets(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load JSON 1", command=lambda: self.load_json(1))
        file_menu.add_command(label="Load JSON 2", command=lambda: self.load_json(2))
        file_menu.add_command(label="Save Comparison", command=self.save_comparison)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Input frames
        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # JSON 1 input
        json1_frame = ttk.LabelFrame(input_frame, text="JSON 1")
        json1_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        self.json1_text = tk.Text(json1_frame, wrap=tk.WORD, height=15)
        self.json1_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.json1_text.bind('<Control-f>', self.handle_ctrl_f)

        # JSON 2 input
        json2_frame = ttk.LabelFrame(input_frame, text="JSON 2")
        json2_frame.pack(side=tk.RIGHT, padx=5, fill=tk.BOTH, expand=True)
        self.json2_text = tk.Text(json2_frame, wrap=tk.WORD, height=15)
        self.json2_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.json2_text.bind('<Control-f>', self.handle_ctrl_f)

        # Compare options
        options_frame = ttk.Frame(self.root)
        options_frame.pack(pady=5)

        ttk.Radiobutton(options_frame, text="Full Compare", variable=self.compare_mode, value="full").pack(side=tk.LEFT)
        ttk.Radiobutton(options_frame, text="Different Fields", variable=self.compare_mode, value="diff").pack(side=tk.LEFT)
        ttk.Radiobutton(options_frame, text="Matching Fields", variable=self.compare_mode, value="match").pack(side=tk.LEFT)

        ttk.Checkbutton(options_frame, text="Ignore Whitespace", variable=self.ignore_whitespace).pack(side=tk.LEFT, padx=10)

        # Buttons frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=5)

        ttk.Button(buttons_frame, text="Compare", command=self.compare_json).pack(side=tk.LEFT, padx=5)

        # Dark mode toggle
        self.dark_mode = tk.BooleanVar(value=False)
        dark_mode_toggle = ttk.Checkbutton(options_frame, text="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode)
        dark_mode_toggle.pack(side=tk.LEFT, padx=10)

        self.format_var = tk.StringVar(value="Both")
        format_menu = ttk.OptionMenu(buttons_frame, self.format_var, "Both", "JSON 1", "JSON 2", "Both")
        format_menu.pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Format JSON", command=self.format_json).pack(side=tk.LEFT, padx=5)

        ttk.Button(buttons_frame, text="Validate JSON", command=self.validate_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Copy Results", command=self.copy_results).pack(side=tk.LEFT, padx=5)

        # Result frame
        result_frame = ttk.Frame(self.root)
        result_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Result text widgets
        self.result1_text = tk.Text(result_frame, wrap=tk.WORD, height=20)
        self.result1_text.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        self.result2_text = tk.Text(result_frame, wrap=tk.WORD, height=20)
        self.result2_text.pack(side=tk.RIGHT, padx=5, fill=tk.BOTH, expand=True)

        # Statistics label
        self.stats_label = ttk.Label(self.root, text="")
        self.stats_label.pack(pady=5)

    def preprocess_json(self, json_str):
        json_str = re.sub(r'ObjectId\("(\w+)"\)', r'"\1"', json_str)
        json_str = re.sub(r'ISODate\("([^"]+)"\)', r'"\1"', json_str)
        json_str = re.sub(r'NumberInt\((\d+)\)', r'\1', json_str)
        return json_str

    def compare_json(self):
        try:
            json1_str = self.preprocess_json(self.json1_text.get("1.0", tk.END))
            json2_str = self.preprocess_json(self.json2_text.get("1.0", tk.END))

            json1 = json.loads(json1_str)
            json2 = json.loads(json2_str)

            def format_json(obj):
                return json.dumps(obj, indent=2, sort_keys=True).splitlines()

            json1_lines = format_json(json1)
            json2_lines = format_json(json2)

            if self.ignore_whitespace.get():
                json1_lines = [line.strip() for line in json1_lines]
                json2_lines = [line.strip() for line in json2_lines]

            differ = Differ()
            diff = list(differ.compare(json1_lines, json2_lines))

            self.result1_text.delete("1.0", tk.END)
            self.result2_text.delete("1.0", tk.END)

            if self.dark_mode.get():
                self.result1_text.tag_configure("diff", background="#4f3232")
                self.result2_text.tag_configure("diff", background="#324f32")
            else:
                self.result1_text.tag_configure("diff", background="light coral")
                self.result2_text.tag_configure("diff", background="light green")

            mode = self.compare_mode.get()
            additions = 0
            deletions = 0
            modifications = 0

            for line in diff:
                if line.startswith("  "):
                    if mode in ["full", "match"]:
                        self.result1_text.insert(tk.END, line[2:] + "\n")
                        self.result2_text.insert(tk.END, line[2:] + "\n")
                elif line.startswith("- "):
                    if mode in ["full", "diff"]:
                        self.result1_text.insert(tk.END, line[2:] + "\n", "diff")
                        deletions += 1
                elif line.startswith("+ "):
                    if mode in ["full", "diff"]:
                        self.result2_text.insert(tk.END, line[2:] + "\n", "diff")
                        additions += 1

            modifications = max(additions, deletions)
            self.stats_label.config(text=f"Additions: {additions}, Deletions: {deletions}, Modifications: {modifications}")

            self.result1_text.tag_configure("diff", background="light coral")
            self.result2_text.tag_configure("diff", background="light green")

        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_json(self, text_widget_num):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    json_content = file.read()
                if text_widget_num == 1:
                    self.json1_text.delete("1.0", tk.END)
                    self.json1_text.insert(tk.END, json_content)
                else:
                    self.json2_text.delete("1.0", tk.END)
                    self.json2_text.insert(tk.END, json_content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load JSON: {str(e)}")

    def save_comparison(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write("JSON 1:\n")
                    file.write(self.result1_text.get("1.0", tk.END))
                    file.write("\nJSON 2:\n")
                    file.write(self.result2_text.get("1.0", tk.END))
                messagebox.showinfo("Success", "Comparison saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save comparison: {str(e)}")

    def format_json(self):
        def format_single_json(text_widget):
            try:
                json_str = self.preprocess_json(text_widget.get("1.0", tk.END))
                json_data = json.loads(json_str)
                formatted_json = json.dumps(json_data, indent=2)
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, formatted_json)
                return True
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Invalid JSON input: {str(e)}")
                return False

        format_option = self.format_var.get()
        success = True

        if format_option in ["JSON 1", "Both"]:
            success &= format_single_json(self.json1_text)

        if format_option in ["JSON 2", "Both"]:
            success &= format_single_json(self.json2_text)

        if success:
            messagebox.showinfo("Success", "JSON formatted successfully.")

    def validate_json(self):
        def validate_single_json(text_widget, name):
            try:
                json_str = self.preprocess_json(text_widget.get("1.0", tk.END))
                json.loads(json_str)
                return True
            except json.JSONDecodeError as e:
                messagebox.showerror("Validation Error", f"Invalid JSON in {name}: {str(e)}")
                return False

        json1_valid = validate_single_json(self.json1_text, "JSON 1")
        json2_valid = validate_single_json(self.json2_text, "JSON 2")

        if json1_valid and json2_valid:
            messagebox.showinfo("Validation", "Both JSON inputs are valid.")

    def copy_results(self):
        result = f"JSON 1:\n{self.result1_text.get('1.0', tk.END)}\nJSON 2:\n{self.result2_text.get('1.0', tk.END)}"
        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        messagebox.showinfo("Success", "Comparison results copied to clipboard.")

    def create_search_window(self, text_widget):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search")
        search_window.geometry("300x100")

        if self.dark_mode.get():
            search_window.configure(bg='#2b2b2b')
        else:
            search_window.configure(bg='white')

        search_frame = ttk.Frame(search_window)
        search_frame.pack(padx=10, pady=10)

        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.focus_set()

        def search():
            keyword = search_entry.get()
            text_widget.tag_remove('search', '1.0', tk.END)
            if keyword:
                start_pos = '1.0'
                while True:
                    start_pos = text_widget.search(keyword, start_pos, stopindex=tk.END)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(keyword)}c"
                    text_widget.tag_add('search', start_pos, end_pos)
                    start_pos = end_pos
                text_widget.tag_config('search', background='yellow')

        search_button = ttk.Button(search_frame, text="Search", command=search)
        search_button.pack(side=tk.LEFT, padx=5)

        search_window.bind('<Return>', lambda event: search())

        # Add this part to remove highlights when the window is closed
        def on_closing():
            self.remove_search_highlights(text_widget)
            search_window.destroy()

        search_window.protocol("WM_DELETE_WINDOW", on_closing)

        # Apply the current theme to the search window
        self.apply_theme_to_widget(search_window)
        self.apply_theme_to_widget(search_frame)
        self.apply_theme_to_widget(search_entry)
        self.apply_theme_to_widget(search_button)

    def apply_theme_to_widget(self, widget):
        if self.dark_mode.get():
            widget.configure(bg='#2b2b2b', fg='white')
        else:
            widget.configure(bg='white', fg='black')

    def handle_ctrl_f(self, event):
        if event.widget in (self.json1_text, self.json2_text):
            self.create_search_window(event.widget)

    def remove_search_highlights(self, text_widget):
        text_widget.tag_remove('search', '1.0', tk.END)

    def toggle_dark_mode(self):
        if self.dark_mode.get():
            self.set_dark_theme()
        else:
            self.set_light_theme()

    def set_dark_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#2b2b2b', foreground='white')
        style.configure('TLabel', background='#2b2b2b', foreground='white')
        style.configure('TButton', background='#3c3f41', foreground='white')
        style.configure('TCheckbutton', background='#2b2b2b', foreground='white')
        style.configure('TRadiobutton', background='#2b2b2b', foreground='white')
        style.configure('TLabelframe', background='#2b2b2b', foreground='white')
        style.configure('TLabelframe.Label', background='#2b2b2b', foreground='white')

        self.root.configure(bg='#2b2b2b')
        self.json1_text.configure(bg='#2b2b2b', fg='white', insertbackground='white')
        self.json2_text.configure(bg='#2b2b2b', fg='white', insertbackground='white')
        self.result1_text.configure(bg='#2b2b2b', fg='white', insertbackground='white')
        self.result2_text.configure(bg='#2b2b2b', fg='white', insertbackground='white')
        self.stats_label.configure(background='#2b2b2b', foreground='white')

        self.result1_text.tag_configure("diff", background="#4f3232")
        self.result2_text.tag_configure("diff", background="#324f32")

    def set_light_theme(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('.', background='white', foreground='black')
        style.configure('TLabel', background='white', foreground='black')
        style.configure('TButton', background='white', foreground='black')
        style.configure('TCheckbutton', background='white', foreground='black')
        style.configure('TRadiobutton', background='white', foreground='black')
        style.configure('TLabelframe', background='white', foreground='black')
        style.configure('TLabelframe.Label', background='white', foreground='black')

        self.root.configure(bg='white')
        self.json1_text.configure(bg='white', fg='black', insertbackground='black')
        self.json2_text.configure(bg='white', fg='black', insertbackground='black')
        self.result1_text.configure(bg='white', fg='black', insertbackground='black')
        self.result2_text.configure(bg='white', fg='black', insertbackground='black')
        self.stats_label.configure(background='white', foreground='black')

        self.result1_text.tag_configure("diff", background="light coral")
        self.result2_text.tag_configure("diff", background="light green")


if __name__ == "__main__":
    root = tk.Tk()
    app = JSONCompareApp(root)
    root.mainloop()
