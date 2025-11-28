# -*- coding: utf-8 -*-
#from os import posix_fadvise
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

#синтаксич. анализ
def parse(tokens):
    pos = 0
    data = {}

    def expect(token_type):
        nonlocal pos
        if pos >= len(tokens) or tokens[pos].type != token_type:
            raise SyntaxError(f"ожидался {token_type}, а получен {tokens[pos] if pos < len(tokens) else 'EOF'}")
        pos += 1

    while pos < len(tokens):
        tok = tokens[pos]

        if tok.type == 'IDENT':
            name = tok.value
            pos += 1
            expect('IS')

            # число
            if tokens[pos].type == 'NUMBER':
                val = int(tokens[pos].value, 8)  #перевод из octal
                pos += 1

            # список { ... }
            elif tokens[pos].type == 'LBRACE':
                pos += 1
                arr = []
                while tokens[pos].type != 'RBRACE':
                    if tokens[pos].type == 'NUMBER':
                        arr.append(int(tokens[pos].value, 8))
                        pos += 1
                    if tokens[pos].type == 'COMMA':
                        pos += 1
                expect('RBRACE')
                val = arr
            else:
                raise SyntaxError("Ожидалось число или список")

            expect('SEMICOLON')
            data[name] = val

        #ссылка: [ IDENT ]
        elif tok.type == 'LBRACKET':
            pos += 1
            if tokens[pos].type != 'IDENT':
                raise SyntaxError("Ожидалось имя в []")
            ref_name = tokens[pos].value
            pos += 1
            expect('RBRACKET')

            print(f"ссылка [{ref_name}] → {data.get(ref_name)}")

        else:
            raise SyntaxError(f"Неожиданный токен {tok}")

    return data



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
    
    #3. парсер
    parsed = parse(tokens)
    print("\nрезультат парсинга:")
    print(parsed)

if __name__ == "__main__":
    main()