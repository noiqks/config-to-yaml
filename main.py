# -*- coding: utf-8 -*-
import sys
import re
from collections import namedtuple


#читает файл и возвращает текст
def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

#удаляет многострочные комментарии =begin ... =end
def remove_com(text):
    pattern = r"=begin.*?=end"
    return re.sub(pattern, '', text, flags=re.DOTALL)#захватывает переносы строк


#определяем список токенов
TOKEN_SPEC = [
    ('NUMBER', r'0[oO][0-7]+'),
    ('IS', r'is\b'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('COMMA', r','),
    ('SEMICOLON', r';'),
    ('IDENT', r'[_a-zA-Z][_a-zA-Z0-9]*'),
    ('SKIP', r'\s+'),  # пробелы и переносы строк
]
Token = namedtuple('Token', ['type', 'value'])

#преобразуем текст в список токенов
def tokenize(text):
    tokens = []
    pos = 0
    while pos < len(text):
        match = None
        for token_type, pattern in TOKEN_SPEC:
            regax = re.compile(pattern)
            match = regax.match(text, pos)
            if match:
                if token_type != 'SKIP' : #пропускаем
                    tok = Token(token_type, match.group(0))
                    tokens.append(tok)
                pos = match.end()
                break
        if not match:
            raise SyntaxError(f'неизвестный символ в позиции {pos}: {text[pos]}')
    return tokens

def main():
    if len(sys.argv) != 3:
        print("Использование: python main.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    #1.чтение файла и обработка файла
    text = read_file(input_file)
    clean_text = remove_com(text)

    #2. токенизация
    tokens = tokenize(clean_text)
    print("\nсписок токенов:")
    for t in tokens:
        print(t)

if __name__ == "__main__":
    main()