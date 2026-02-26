# -*- coding: utf-8 -*-
"""
Лабораторная работа по теории информации.
Шифрование и дешифрование текста: Плейфейр (англ.) и Виженер (рус.).
GUI на tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import ciphers


class CipherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Шифрование текста — Теория информации")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)

        self._build_ui()

    def _build_ui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === Выбор алгоритма ===
        algo_frame = ttk.LabelFrame(main_frame, text="Алгоритм шифрования", padding=5)
        algo_frame.pack(fill=tk.X, pady=(0, 5))
        self.algo_var = tk.StringVar(value="playfair")
        ttk.Radiobutton(
            algo_frame,
            text="Шифр Плейфейра (английский язык)",
            variable=self.algo_var,
            value="playfair",
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            algo_frame,
            text="Алгоритм Виженера, прогрессивный ключ (русский язык)",
            variable=self.algo_var,
            value="vigenere",
        ).pack(anchor=tk.W)

        # === Ключ ===
        key_frame = ttk.LabelFrame(main_frame, text="Ключ", padding=5)
        key_frame.pack(fill=tk.X, pady=(0, 5))
        self.key_entry = ttk.Entry(key_frame, width=60)
        self.key_entry.pack(fill=tk.X, pady=2)

        # === Исходный текст ===
        input_frame = ttk.LabelFrame(main_frame, text="Исходный текст (ввод / загрузка из файла)", padding=5)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, wrap=tk.WORD, font=("Consolas", 11))
        self.input_text.pack(fill=tk.BOTH, expand=True)

        btn_input = ttk.Frame(input_frame)
        btn_input.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btn_input, text="Загрузить из файла...", command=self._load_file).pack(side=tk.LEFT, padx=(0, 5))

        # === Действия ===
        action_frame = ttk.LabelFrame(main_frame, text="Действия", padding=10)
        action_frame.pack(fill=tk.X, pady=10)
        ttk.Button(action_frame, text="Шифровать", command=self._encrypt).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_frame, text="Дешифровать", command=self._decrypt).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_frame, text="Очистить", command=self._clear).pack(side=tk.LEFT, padx=(0, 8))

        # === Результат ===
        output_frame = ttk.LabelFrame(main_frame, text="Результат", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.output_text = scrolledtext.ScrolledText(output_frame, height=8, wrap=tk.WORD, font=("Consolas", 11))
        self.output_text.pack(fill=tk.BOTH, expand=True)

        btn_output = ttk.Frame(output_frame)
        btn_output.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btn_output, text="Сохранить в файл...", command=self._save_result).pack(side=tk.LEFT, padx=(0, 5))

    def _get_input(self) -> str:
        return self.input_text.get("1.0", tk.END).strip()

    def _set_output(self, text: str):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)

    def _get_key(self) -> str:
        return self.key_entry.get().strip()

    def _encrypt(self):
        key = self._get_key()
        text = self._get_input()
        if not text:
            messagebox.showwarning("Внимание", "Введите текст для шифрования.")
            return
        if not key:
            messagebox.showwarning("Внимание", "Введите ключ.")
            return
        try:
            if self.algo_var.get() == "playfair":
                result = ciphers.playfair_encrypt(text, key)
            else:
                result = ciphers.vigenere_encrypt(text, key)
            self._set_output(result)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _decrypt(self):
        key = self._get_key()
        text = self._get_input()
        if not text:
            messagebox.showwarning("Внимание", "Введите текст для расшифровки.")
            return
        if not key:
            messagebox.showwarning("Внимание", "Введите ключ.")
            return
        try:
            if self.algo_var.get() == "playfair":
                result = ciphers.playfair_decrypt(text, key)
            else:
                result = ciphers.vigenere_decrypt(text, key)
            self._set_output(result)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _clear(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.key_entry.delete(0, tk.END)

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Выберите файл с текстом",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", content)
            messagebox.showinfo("Загрузка", "Файл загружен. Текст можно отредактировать.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")

    def _save_result(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Внимание", "Нет результата для сохранения.")
            return
        path = filedialog.asksaveasfilename(
            title="Сохранить результат",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Сохранение", "Результат сохранён.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CipherApp()
    app.run()
