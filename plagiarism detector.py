import os
import difflib
from difflib import SequenceMatcher
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


class PlagiarismCheckerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Plagiarism Detector & Diff Analyzer")
        self.root.geometry("900x650")

        # FIX: Changed self.root.minimum_size(800, 500) to self.root.minsize(800, 500)
        self.root.minsize(800, 500)

        # File path storage
        self.file1_path = ""
        self.file2_path = ""

        self.create_widgets()

    def create_widgets(self):
        # --- Top File Selection Panel ---
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=15)

        # File 1 Selection
        f1_btn = tk.Button(
            top_frame,
            text="Select Document 1",
            command=self.load_file1,
            width=18,
            font=("Arial", 9, "bold"),
        )
        f1_btn.grid(row=0, column=0, padx=5, pady=5)
        self.f1_label = tk.Label(
            top_frame, text="No file selected...", fg="gray", anchor="w"
        )
        self.f1_label.grid(row=0, column=1, sticky="ew", padx=5)

        # File 2 Selection
        f2_btn = tk.Button(
            top_frame,
            text="Select Document 2",
            command=self.load_file2,
            width=18,
            font=("Arial", 9, "bold"),
        )
        f2_btn.grid(row=1, column=0, padx=5, pady=5)
        self.f2_label = tk.Label(
            top_frame, text="No file selected...", fg="gray", anchor="w"
        )
        self.f2_label.grid(row=1, column=1, sticky="ew", padx=5)

        top_frame.columnconfigure(1, weight=1)

        # --- Control & Results Dashboard Panel ---
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=15)

        self.compare_btn = tk.Button(
            control_frame,
            text="Analyze Plagiarism",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.analyze_documents,
            height=2,
            width=20,
        )
        self.compare_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = tk.Button(
            control_frame,
            text="Export HTML Report",
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.export_html,
            height=2,
            width=20,
            state="disabled",
        )
        self.export_btn.pack(side=tk.LEFT, padx=10)

        # Results Display Labels
        self.result_label = tk.Label(
            control_frame,
            text="Similarity: --%",
            font=("Arial", 14, "bold"),
            fg="#2c3e50",
        )
        self.result_label.pack(side=tk.RIGHT, padx=20)

        # --- Side-by-Side Text Comparison Area ---
        text_frame = tk.Frame(self.root)
        text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left Text Window (Doc 1)
        lbl_frame1 = tk.LabelFrame(text_frame, text="Document 1 View")
        lbl_frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.txt_view1 = scrolledtext.ScrolledText(
            lbl_frame1, wrap=tk.WORD, font=("Courier New", 10)
        )
        self.txt_view1.pack(fill=tk.BOTH, expand=True)

        # Right Text Window (Doc 2)
        lbl_frame2 = tk.LabelFrame(text_frame, text="Document 2 View")
        lbl_frame2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.txt_view2 = scrolledtext.ScrolledText(
            lbl_frame2, wrap=tk.WORD, font=("Courier New", 10)
        )
        self.txt_view2.pack(fill=tk.BOTH, expand=True)

        # Setup Highlight Tags for Text Coloring
        self.txt_view1.tag_config("match", background="#ffcccc", foreground="black")
        self.txt_view2.tag_config("match", background="#ccffcc", foreground="black")

    def load_file1(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            self.file1_path = path
            self.f1_label.config(text=os.path.basename(path), fg="black")
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                self.txt_view1.delete("1.0", tk.END)
                self.txt_view1.insert(tk.END, content)

    def load_file2(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            self.file2_path = path
            self.f2_label.config(text=os.path.basename(path), fg="black")
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                self.txt_view2.delete("1.0", tk.END)
                self.txt_view2.insert(tk.END, content)

    def analyze_documents(self):
        data1 = self.txt_view1.get("1.0", tk.END).strip()
        data2 = self.txt_view2.get("1.0", tk.END).strip()

        if not data1 or not data2:
            messagebox.showwarning(
                "Missing Data",
                "Please make sure both document views contain text before checking.",
            )
            return

        self.txt_view1.tag_remove("match", "1.0", tk.END)
        self.txt_view2.tag_remove("match", "1.0", tk.END)

        # Calculate similarity ratio
        matcher = SequenceMatcher(None, data1, data2)
        ratio = matcher.ratio()
        percentage = ratio * 100

        self.result_label.config(text=f"Similarity: {percentage:.2f}%")
        if percentage > 50:
            self.result_label.config(fg="#c0392b")
        elif percentage > 20:
            self.result_label.config(fg="#d35400")
        else:
            self.result_label.config(fg="#27ae60")

        # Highlight matching blocks
        matching_blocks = matcher.get_matching_blocks()

        for block in matching_blocks:
            if block.size == 0:
                continue

            start_pos_f1 = self.index_to_tk_position(data1, block.a)
            end_pos_f1 = self.index_to_tk_position(data1, block.a + block.size)

            start_pos_f2 = self.index_to_tk_position(data2, block.b)
            end_pos_f2 = self.index_to_tk_position(data2, block.b + block.size)

            self.txt_view1.tag_add("match", start_pos_f1, end_pos_f1)
            self.txt_view2.tag_add("match", start_pos_f2, end_pos_f2)

        self.export_btn.config(state="normal")
        messagebox.showinfo(
            "Analysis Complete",
            f"Scan finished.\nOverall overlap similarity metric: {percentage:.2f}%",
        )

    def index_to_tk_position(self, text_content, string_index):
        substring = text_content[:string_index]
        lines = substring.split("\n")
        line_num = len(lines)
        char_num = len(lines[-1])
        return f"{line_num}.{char_num}"

    def export_html(self):
        data1 = self.txt_view1.get("1.0", tk.END).splitlines()
        data2 = self.txt_view2.get("1.0", tk.END).splitlines()

        save_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Report", "*.html")],
            title="Save Plagiarism Analysis Report",
            initialfile="plagiarism_report.html",
        )

        if save_path:
            try:
                html_diff_engine = difflib.HtmlDiff()
                html_table = html_diff_engine.make_file(
                    data1,
                    data2,
                    fromdesc="Original Document (1)",
                    todesc="Suspect Document (2)",
                )

                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(html_table)

                messagebox.showinfo(
                    "Success", f"Interactive HTML report saved to:\n{save_path}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Export Failed", f"An error occurred:\n{str(e)}"
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = PlagiarismCheckerApp(root)
    root.mainloop()