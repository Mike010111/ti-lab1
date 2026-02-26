# -*- coding: utf-8 -*-
"""
Лабораторная работа по теории информации.
Шифрование и дешифрование текста: Плейфейр (англ.) и Виженер (рус.) с прогрессивным ключом.
GUI на tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


# === Константы алфавитов ===

EN_ALPHABET_PLAYFAIR = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # J объединяем с I
RU_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


# === Вспомогательные функции для ключей ===

def _clean_key_playfair(raw_key: str) -> str:
    """Очищает ключ для шифра Плейфейра: только буквы A-Z, J -> I, без повторов."""
    result = []
    seen = set()
    for ch in raw_key:
        if ch.isalpha():
            c = ch.upper()
            if "A" <= c <= "Z":
                if c == "J":
                    c = "I"
                if c not in seen:
                    seen.add(c)
                    result.append(c)
    return "".join(result)


def _clean_key_vigenere(raw_key: str) -> str:
    """Очищает ключ для Виженера: только буквы русского алфавита."""
    result = []
    for ch in raw_key:
        c = ch.upper()
        if c in RU_ALPHABET:
            result.append(c)
    return "".join(result)


# === Шифр Плейфейра (английский) ===

def _build_playfair_matrix(clean_key: str):
    """Строит матрицу 5x5 из очищенного ключа."""
    used = set(clean_key)
    matrix = []
    row = []
    for c in clean_key:
        row.append(c)
        if len(row) == 5:
            matrix.append(row)
            row = []
    for c in EN_ALPHABET_PLAYFAIR:
        if c not in used:
            row.append(c)
            used.add(c)
            if len(row) == 5:
                matrix.append(row)
                row = []
    if row:
        matrix.append(row)
    return matrix


def _find_in_matrix(matrix, ch: str):
    for i, row in enumerate(matrix):
        for j, c in enumerate(row):
            if c == ch:
                return i, j
    return -1, -1


def _playfair_process_pairs(letters: list, matrix, encrypt: bool) -> str:
    """Обрабатывает список букв парами (без вставки X между одинаковыми)."""
    result = []
    i = 0
    # если нечётное количество букв, добавим X в конец
    if len(letters) % 2 == 1:
        letters = letters + ["X"]
    while i < len(letters):
        a = letters[i]
        b = letters[i + 1]
        r1, c1 = _find_in_matrix(matrix, a)
        r2, c2 = _find_in_matrix(matrix, b)
        if r1 == r2:
            # одна строка
            shift = 1 if encrypt else -1
            result.append(matrix[r1][(c1 + shift) % 5])
            result.append(matrix[r2][(c2 + shift) % 5])
        elif c1 == c2:
            # один столбец
            shift = 1 if encrypt else -1
            result.append(matrix[(r1 + shift) % 5][c1])
            result.append(matrix[(r2 + shift) % 5][c2])
        else:
            # прямоугольник
            result.append(matrix[r1][c2])
            result.append(matrix[r2][c1])
        i += 2
    return "".join(result)


def playfair_transform(text: str, raw_key: str, encrypt: bool) -> str:
    """
    Применяет шифр Плейфейра к английскому тексту.
    - Ключ логически очищается (только A-Z, J->I).
    - Недопустимые символы в ключе и тексте игнорируются при шифровании,
      но визуально остаются на своих местах.
    - Если очищенный ключ пуст, текст возвращается без изменений.
    """
    clean_key = _clean_key_playfair(raw_key)
    if not clean_key:
        return text

    matrix = _build_playfair_matrix(clean_key)

    # Собираем только английские буквы (J -> I), запоминаем их позиции
    chars = list(text)
    letter_positions = []
    letters = []
    for idx, ch in enumerate(chars):
        if ch.isalpha():
            c = ch.upper()
            if "A" <= c <= "Z":
                if c == "J":
                    c = "I"
                letter_positions.append(idx)
                letters.append(c)

    if not letters:
        return text

    processed = _playfair_process_pairs(letters, matrix, encrypt=encrypt)

    # Заменяем только буквы, остальные символы остаются на местах
    result_chars = chars[:]
    k = 0
    for pos in letter_positions:
        if k >= len(processed):
            break
        orig = result_chars[pos]
        new_ch = processed[k]
        # сохраняем регистр
        if orig.islower():
            new_ch = new_ch.lower()
        result_chars[pos] = new_ch
        k += 1

    # если возник лишний символ (при нечётном числе букв) — добавим его в конец
    if k < len(processed):
        extra = processed[k:]
        result_chars.extend(extra)

    return "".join(result_chars)


def playfair_encrypt(text: str, raw_key: str) -> str:
    return playfair_transform(text, raw_key, encrypt=True)


def playfair_decrypt(text: str, raw_key: str) -> str:
    return playfair_transform(text, raw_key, encrypt=False)


# === Виженер с прогрессивным ключом (русский) ===

def _shift_ru_char(ch: str, shift: int) -> str:
    idx = RU_ALPHABET.index(ch)
    return RU_ALPHABET[(idx + shift) % len(RU_ALPHABET)]


def vigenere_progressive_encrypt(text: str, raw_key: str) -> str:
    """
    Шифр Виженера с прогрессивным ключом (русский текст).
    - очищаем ключ до русских букв;
    - недопустимые символы в ключе логически отбрасываются;
    - недопустимые символы в тексте не шифруются и остаются на своих местах;
    - при каждом полном проходе ключа все его символы сдвигаются в алфавите на 1.
    """
    clean_key = _clean_key_vigenere(raw_key)
    if not clean_key:
        return text

    res = []
    letter_index = 0  # учитываем только русские буквы
    for ch in text:
        upper = ch.upper()
        if upper in RU_ALPHABET:
            key_pos = letter_index % len(clean_key)
            cycle = letter_index // len(clean_key)
            base_key_char = clean_key[key_pos]
            effective_key_char = _shift_ru_char(base_key_char, cycle)
            k = RU_ALPHABET.index(effective_key_char)
            p = RU_ALPHABET.index(upper)
            c = RU_ALPHABET[(p + k) % len(RU_ALPHABET)]
            if ch.islower():
                c = c.lower()
            res.append(c)
            letter_index += 1
        else:
            res.append(ch)
    return "".join(res)


def vigenere_progressive_decrypt(text: str, raw_key: str) -> str:
    """Обратное преобразование для прогрессивного шифра Виженера."""
    clean_key = _clean_key_vigenere(raw_key)
    if not clean_key:
        return text

    res = []
    letter_index = 0
    for ch in text:
        upper = ch.upper()
        if upper in RU_ALPHABET:
            key_pos = letter_index % len(clean_key)
            cycle = letter_index // len(clean_key)
            base_key_char = clean_key[key_pos]
            effective_key_char = _shift_ru_char(base_key_char, cycle)
            k = RU_ALPHABET.index(effective_key_char)
            c = RU_ALPHABET.index(upper)
            p = RU_ALPHABET[(c - k) % len(RU_ALPHABET)]
            if ch.islower():
                p = p.lower()
            res.append(p)
            letter_index += 1
        else:
            res.append(ch)
    return "".join(res)


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
        # Ключ может оказаться пустым после логической очистки, тогда просто возвращаем текст
        if self.algo_var.get() == "playfair":
            result = playfair_encrypt(text, key)
        else:
            result = vigenere_progressive_encrypt(text, key)
        self._set_output(result)

    def _decrypt(self):
        key = self._get_key()
        text = self._get_input()
        if not text:
            messagebox.showwarning("Внимание", "Введите текст для расшифровки.")
            return
        if self.algo_var.get() == "playfair":
            result = playfair_decrypt(text, key)
        else:
            result = vigenere_progressive_decrypt(text, key)
        self._set_output(result)

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
