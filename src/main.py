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

#парсер
def parse(tokens):
    pos = 0
    data = {}
    errors = []

    def current():
        return tokens[pos] if pos < len(tokens) else None

    def advance():
        nonlocal pos
        pos += 1

    def report_error(msg):
        errors.append(msg)

    def expect(token_type):
        tok = current()
        if tok is None:
            report_error(f"ожидался {token_type}, но достигнут конец файла")
            return None

        if tok.type != token_type:
            report_error(f"ожидался {token_type}, а получен {tok}")
            return None

        advance()
        return tok

    def synchronize():
        nonlocal pos
        while pos < len(tokens):
            if tokens[pos].type in ('SEMICOLON', 'RBRACE', 'RBRACKET'):
                pos += 1
                break
            pos += 1

    while pos < len(tokens):
        tok = current()
        if tok is None:
            break

        if tok.type == 'IDENT':
            name = tok.value
            advance()

            if not expect('IS'):
                synchronize()
                continue

            tok = current()

            #число
            if tok and tok.type == 'NUMBER':
                val = int(tok.value, 8)
                advance()

            #список
            elif tok and tok.type == 'LBRACE':
                advance()
                arr = []

                while True:
                    tok = current()
                    if tok is None:
                        report_error("не закрыта фигурная скобка { ... }")
                        break

                    if tok.type == 'NUMBER':
                        arr.append(int(tok.value, 8))
                        advance()
                        tok = current()

                        if tok and tok.type == 'COMMA':
                            advance()
                            continue
                        elif tok and tok.type == 'RBRACE':
                            break
                        else:
                            report_error(f"недопустимый токен в списке: {tok}")
                            break

                    elif tok.type == 'RBRACE':
                        break
                    else:
                        report_error(f"недопустимый элемент внутри списка: {tok}")
                        break

                if not expect('RBRACE'):
                    synchronize()
                    continue

                val = arr

            else:
                report_error(f"ожидалось число или {{...}}, а получено {tok}")
                synchronize()
                continue

            if not expect('SEMICOLON'):
                synchronize()
                continue

            data[name] = val
        
        elif tok.type == 'LBRACKET':
            advance()

            ident_tok = expect('IDENT')
            ident = ident_tok.value if ident_tok else None

            if ident and ident not in data:
                report_error(f"ссылка [{ident}] на неизвестную переменную")

            expect('RBRACKET')

        else:
            report_error(f"неожиданный токен {tok}")
            advance()

    return data, errors



def main():
    if len(sys.argv) != 3:
        print("использование: python main.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    text = read_file(input_file)
    cleaned = remove_com(text)

    tokens = tokenize(cleaned)

    print("токены:")
    for t in tokens:
        print("  ", t)

    data, errors = parse(tokens)

    print("\nрезультат парсинга:")
    print(data)

    if errors:
        print("\nошибки синтаксиса:")
        for i, e in enumerate(errors, 1):
            print(f"  {i}) {e}")
    else:
        print("\nnошибок нет.")


    # #1.чтение файла и обработка файла
    # text = read_file(input_file)
    # clean_text = remove_com(text)

    # #2. токенизация
    # tokens = tokenize(clean_text)
    
    # #3. парсер
    # parsed = parse(tokens)
    # print("\nрезультат парсинга:")
    # print(parsed)

if __name__ == "__main__":
    main()