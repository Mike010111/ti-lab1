import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


# Константы алфавитов
EN_ALPHABET_PLAYFAIR = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # J объединяем с I
RU_ALPHABET = "АБВГДЕËЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


# Вспомогательные функции для ключей
def _clean_key_playfair(raw_key: str) -> str:
    # Очищает ключ для шифра Плейфейра: только буквы A-Z, J -> I, без повторов
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
    # Очищает ключ для Виженера: только буквы русского алфавита
    result = []
    for ch in raw_key:
        c = ch.upper()
        if c in RU_ALPHABET:
            result.append(c)
    return "".join(result)


# Шифр Плейфейра (английский язык)

def _build_playfair_matrix(clean_key: str):
    # Строит матрицу 5x5 из очищенного ключа
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


def _is_en_letter(ch: str) -> bool:
    c = ch.upper()
    return "A" <= c <= "Z"


def _playfair_process_pairs(letters: list, matrix, encrypt: bool) -> str:
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
    clean_key = _clean_key_playfair(raw_key)
    matrix = _build_playfair_matrix(clean_key)

    # Разбиваем текст на слова (английские буквы) и разделители,
    # одновременно формируя глобальный список букв и их принадлежность словам.
    words = []
    seps = []
    letters = []
    letter_word_idx = []
    n = len(text)
    i = 0

    sep_chars = []
    while i < n and not _is_en_letter(text[i]):
        sep_chars.append(text[i])
        i += 1
    seps.append("".join(sep_chars))

    while i < n:
        word_index = len(words)
        word_chars = []
        while i < n and _is_en_letter(text[i]):
            ch = text[i]
            word_chars.append(ch)
            c = ch.upper()
            if c == "J":
                c = "I"
            letters.append(c)
            letter_word_idx.append(word_index)
            i += 1
        words.append("".join(word_chars))

        sep_chars = []
        while i < n and not _is_en_letter(text[i]):
            sep_chars.append(text[i])
            i += 1
        seps.append("".join(sep_chars))

    if not letters:
        return text

    if encrypt:
        prepared_letters = []
        prepared_word_idx = []
        j = 0
        L = len(letters)
        while j < L:
            first = letters[j]
            w_first = letter_word_idx[j]
            if j + 1 < L:
                second = letters[j + 1]
                w_second = letter_word_idx[j + 1]
                if first == second:
                    # пара одинаковых букв: вставляем X, относя X к первому слову
                    prepared_letters.append(first)
                    prepared_word_idx.append(w_first)
                    prepared_letters.append("X")
                    prepared_word_idx.append(w_first)
                    j += 1
                else:
                    prepared_letters.append(first)
                    prepared_word_idx.append(w_first)
                    prepared_letters.append(second)
                    prepared_word_idx.append(w_second)
                    j += 2
            else:
                # последняя одиночная буква — дополняем X
                prepared_letters.append(first)
                prepared_word_idx.append(w_first)
                prepared_letters.append("X")
                prepared_word_idx.append(w_first)
                j += 1
    else:
        prepared_letters = letters[:]
        prepared_word_idx = letter_word_idx[:]

    processed = _playfair_process_pairs(prepared_letters, matrix, encrypt=encrypt)

    # Распределяем зашифрованные буквы по словам
    word_cipher = [[] for _ in range(len(words))]
    for ch, widx in zip(processed, prepared_word_idx):
        if 0 <= widx < len(word_cipher):
            word_cipher[widx].append(ch)

    result_parts = []
    if seps:
        result_parts.append(seps[0])

    for idx, orig_word in enumerate(words):
        cipher_letters = word_cipher[idx]
        ci = 0
        result_word_chars = []
        for ch in orig_word:
            if ci < len(cipher_letters):
                new_c = cipher_letters[ci]
                ci += 1
                result_word_chars.append(new_c)
            else:
                result_word_chars.append(ch)

        if ci < len(cipher_letters):
            extra = cipher_letters[ci:]
            result_word_chars.extend(extra)

        result_parts.append("".join(result_word_chars))

        if idx + 1 < len(seps):
            result_parts.append(seps[idx + 1])

    if len(seps) > len(words) + 1:
        result_parts.extend(seps[len(words) + 1 :])
    return "".join(result_parts)


def playfair_encrypt(text: str, raw_key: str) -> str:
    return playfair_transform(text, raw_key, encrypt=True)


def playfair_decrypt(text: str, raw_key: str) -> str:
    return playfair_transform(text, raw_key, encrypt=False)


# Виженер с прогрессивным ключом (для русского языка)
def _shift_ru_char(ch: str, shift: int) -> str:
    idx = RU_ALPHABET.index(ch)
    return RU_ALPHABET[(idx + shift) % len(RU_ALPHABET)]


def vigenere_progressive_encrypt(text: str, raw_key: str) -> str:
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
            res.append(c)
            letter_index += 1
        else:
            res.append(ch)
    return "".join(res)


def vigenere_progressive_decrypt(text: str, raw_key: str) -> str:
    # Обратное преобразование для прогрессивного шифра Виженера
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
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

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

        key_frame = ttk.LabelFrame(main_frame, text="Ключ", padding=5)
        key_frame.pack(fill=tk.X, pady=(0, 5))
        self.key_entry = ttk.Entry(key_frame, width=60)
        self.key_entry.pack(fill=tk.X, pady=2)

        input_frame = ttk.LabelFrame(main_frame, text="Исходный текст (ввод / загрузка из файла)", padding=5)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, wrap=tk.WORD, font=("Consolas", 11))
        self.input_text.pack(fill=tk.BOTH, expand=True)

        btn_input = ttk.Frame(input_frame)
        btn_input.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btn_input, text="Загрузить из файла...", command=self._load_file).pack(side=tk.LEFT, padx=(0, 5))

        action_frame = ttk.LabelFrame(main_frame, text="Действия", padding=10)
        action_frame.pack(fill=tk.X, pady=10)
        ttk.Button(action_frame, text="Шифровать", command=self._encrypt).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_frame, text="Дешифровать", command=self._decrypt).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_frame, text="Очистить", command=self._clear).pack(side=tk.LEFT, padx=(0, 8))

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
