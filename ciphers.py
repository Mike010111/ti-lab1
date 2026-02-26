# -*- coding: utf-8 -*-
"""
Модуль с реализацией шифров для лабораторной работы по теории информации.
- Шифр Плейфейра (английский язык)
- Алгоритм Виженера с прогрессивным ключом (русский язык)
"""

import re
from typing import Tuple


# === ШИФР ПЛЕЙФЕЙРА (английский) ===

ENGLISH_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # J объединяется с I


def _prepare_playfair_key(key: str) -> str:
    """Подготовка ключа: только буквы, J -> I, без повторов."""
    key = re.sub(r"[^A-Za-z]", "", key.upper()).replace("J", "I")
    seen = set()
    result = []
    for c in key:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return "".join(result)


def _build_playfair_matrix(key: str) -> list:
    """Построение матрицы 5x5 для шифра Плейфейра."""
    key_clean = _prepare_playfair_key(key)
    used = set(key_clean)
    matrix = []
    row = []
    for c in key_clean:
        row.append(c)
        if len(row) == 5:
            matrix.append(row)
            row = []
    for c in ENGLISH_ALPHABET:
        if c not in used:
            row.append(c)
            used.add(c)
            if len(row) == 5:
                matrix.append(row)
                row = []
    if row:
        matrix.append(row)
    return matrix


def _playfair_find_pos(matrix: list, char: str) -> Tuple[int, int]:
    """Находит позицию символа в матрице."""
    for i, row in enumerate(matrix):
        for j, c in enumerate(row):
            if c == char:
                return (i, j)
    return (-1, -1)


def _playfair_encrypt_pair(matrix: list, a: str, b: str) -> str:
    """Шифрует пару букв по правилам Плейфейра."""
    r1, c1 = _playfair_find_pos(matrix, a)
    r2, c2 = _playfair_find_pos(matrix, b)
    if r1 == r2:  # одна строка — сдвиг вправо
        return matrix[r1][(c1 + 1) % 5] + matrix[r2][(c2 + 1) % 5]
    elif c1 == c2:  # один столбец — сдвиг вниз
        return matrix[(r1 + 1) % 5][c1] + matrix[(r2 + 1) % 5][c2]
    else:  # прямоугольник — по столбцам
        return matrix[r1][c2] + matrix[r2][c1]


def _playfair_decrypt_pair(matrix: list, a: str, b: str) -> str:
    """Расшифровывает пару букв."""
    r1, c1 = _playfair_find_pos(matrix, a)
    r2, c2 = _playfair_find_pos(matrix, b)
    if r1 == r2:
        return matrix[r1][(c1 - 1) % 5] + matrix[r2][(c2 - 1) % 5]
    elif c1 == c2:
        return matrix[(r1 - 1) % 5][c1] + matrix[(r2 - 1) % 5][c2]
    else:
        return matrix[r1][c2] + matrix[r2][c1]


def _prepare_playfair_text(text: str, for_encrypt: bool) -> list:
    """Подготовка текста: только буквы, J->I, разбиение на пары."""
    text = re.sub(r"[^A-Za-z]", "", text.upper()).replace("J", "I")
    pairs = []
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            a, b = text[i], text[i + 1]
            if a == b and for_encrypt:
                pairs.append((a, "X"))
                i += 1
            else:
                pairs.append((a, b))
                i += 2
        else:
            if for_encrypt:
                pairs.append((text[i], "X"))
            i += 1
    return pairs


def playfair_encrypt(plaintext: str, key: str) -> str:
    """Шифрование текста алгоритмом Плейфейра (английский)."""
    if not key or not re.search(r"[A-Za-z]", key):
        raise ValueError("Ключ должен содержать хотя бы одну букву английского алфавита")
    matrix = _build_playfair_matrix(key)
    pairs = _prepare_playfair_text(plaintext, for_encrypt=True)
    return "".join(_playfair_encrypt_pair(matrix, a, b) for a, b in pairs)


def playfair_decrypt(ciphertext: str, key: str) -> str:
    """Расшифрование текста алгоритмом Плейфейра."""
    if not key or not re.search(r"[A-Za-z]", key):
        raise ValueError("Ключ должен содержать хотя бы одну букву английского алфавита")
    matrix = _build_playfair_matrix(key)
    pairs = _prepare_playfair_text(ciphertext, for_encrypt=False)
    return "".join(_playfair_decrypt_pair(matrix, a, b) for a, b in pairs)


# === ШИФР ВИЖЕНЕРА (прогрессивный ключ, русский) ===

RUSSIAN_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
RUSSIAN_LEN = len(RUSSIAN_ALPHABET)


def _prepare_vigenere_key_ru(key: str) -> str:
    """Оставляет только буквы русского алфавита (ё в составе)."""
    key_upper = key.upper()
    result = []
    for c in key_upper:
        if c in RUSSIAN_ALPHABET:
            result.append(c)
    return "".join(result)


def _prepare_vigenere_text_ru(text: str) -> str:
    """Оставляет только буквы русского алфавита."""
    text_upper = text.upper()
    result = []
    for c in text_upper:
        if c in RUSSIAN_ALPHABET:
            result.append(c)
    return "".join(result)


def _vigenere_char_encrypt(char: str, key_char: str) -> str:
    """Шифрует один символ: (pos_буквы + pos_ключа) mod 33."""
    p = RUSSIAN_ALPHABET.index(char)
    k = RUSSIAN_ALPHABET.index(key_char)
    return RUSSIAN_ALPHABET[(p + k) % RUSSIAN_LEN]


def _vigenere_char_decrypt(char: str, key_char: str) -> str:
    """Расшифровывает один символ."""
    c = RUSSIAN_ALPHABET.index(char)
    k = RUSSIAN_ALPHABET.index(key_char)
    return RUSSIAN_ALPHABET[(c - k + RUSSIAN_LEN) % RUSSIAN_LEN]


def vigenere_encrypt(plaintext: str, key: str) -> str:
    """Шифрование алгоритмом Виженера с прогрессивным ключом (русский)."""
    key_clean = _prepare_vigenere_key_ru(key)
    if not key_clean:
        raise ValueError("Ключ должен содержать хотя бы одну букву русского алфавита")
    text_clean = _prepare_vigenere_text_ru(plaintext)
    result = []
    for i, char in enumerate(text_clean):
        k = key_clean[i % len(key_clean)]
        result.append(_vigenere_char_encrypt(char, k))
    return "".join(result)


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    """Расшифрование алгоритмом Виженера."""
    key_clean = _prepare_vigenere_key_ru(key)
    if not key_clean:
        raise ValueError("Ключ должен содержать хотя бы одну букву русского алфавита")
    text_clean = _prepare_vigenere_text_ru(ciphertext)
    result = []
    for i, char in enumerate(text_clean):
        k = key_clean[i % len(key_clean)]
        result.append(_vigenere_char_decrypt(char, k))
    return "".join(result)
