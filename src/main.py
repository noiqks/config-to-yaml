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

    def expect(token_type):
        nonlocal pos
        tok = current()
        if tok is None:
            errors.append(f"ожидался {token_type}, но достигнут конец файла")
            return None

        if tok.type != token_type:
            errors.append(f"ожидался {token_type}, а получен {tok}")
            return None

        pos += 1
        return tok

    while pos < len(tokens):
        tok = current()
        if tok.type == "IDENT":
            name = tok.value
            advance()

            expect("IS")
            tok = current()

            #число
            if tok and tok.type == "NUMBER":
                try:
                    val = int(tok.value, 8)
                except:
                    val = None
                    errors.append(f"некорректное число: {tok.value}")
                advance()

            #список
            elif tok and tok.type == "LBRACE":
                advance()
                arr = []

                while True:
                    tok = current()

                    if tok is None:
                        errors.append("не закрыта фигурная скобка { ... }")
                        break

                    if tok.type == "NUMBER":
                        try:
                            arr.append(int(tok.value, 8))
                        except:
                            errors.append(f"некорректное число: {tok.value}")
                        advance()
                        tok = current()

                        if tok and tok.type == "COMMA":
                            advance()
                            continue
                        elif tok and tok.type == "RBRACE":
                            break
                        else:
                            errors.append(f"недопустимый токен в списке: {tok}")
                            advance()
                            break

                    elif tok.type == "RBRACE":
                        break

                    else:
                        errors.append(f"недопустимый элемент внутри списка: {tok}")
                        advance()
                        break

                expect("RBRACE")
                val = arr

            elif tok and tok.type == "LBRACKET":
                errors.append("ссылки [x] нельзя использовать справа от is")
                advance()
                while current() and current().type != "RBRACKET":
                    advance()
                expect("RBRACKET")
                val = None

            else:
                errors.append(f"ожидалось число или {{...}}, а получено {tok}")
                advance()
                val = None
            expect("SEMICOLON")

            data[name] = val
            continue

        elif tok.type == "LBRACKET":
            advance()

            ident_tok = expect("IDENT")
            ident = ident_tok.value if ident_tok else None

            expect("RBRACKET")

            if ident is None:
                errors.append("некорректная ссылка [???]")
                continue

            #если есть ссылка вне присваивания
            ref_name = f"_ref_at_{pos}"
            data[ref_name] = ("ref", ident)

            continue

        else:
            errors.append(f"неожиданный токен {tok}")
            advance()

    return data, errors


#константы
def resolve_constants(data):
    errors = {}
    resolved = {}

    def resolve_value(val, where):
        #число
        if isinstance(val, int):
            return val

        #список
        if isinstance(val, list):
            new_list = []
            for item in val:
                resolved_item = resolve_value(item, where)
                new_list.append(resolved_item)
            return new_list

        #ссылка
        if isinstance(val, tuple) and val[0] == "ref":
            name = val[1]
            if name not in data:
                errors.setdefault(where, []).append(f"неизвестная константа [{name}]")
                return None
            return resolve_value(data[name], name)

        return val

    for key, val in data.items():
        resolved[key] = resolve_value(val, key)

    return resolved, errors





def main():
    if len(sys.argv) != 3:
        print("использование: python main.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    #1.чтение файла и обработка файла
    text = read_file(input_file)
    clean_text = remove_com(text)

    #2. токенизация
    tokens = tokenize(clean_text)
    
    #3. парсер
    parsed, errors = parse(tokens)
    print("\nрезультат парсинга:")
    print(parsed)
    #4. ошибки синтаксиса
    if errors: 
        print("\nошибки синтаксиса:") 
        for i, err in enumerate(errors, 1): 
            print(f" {i}) {err}")

    #5. константы
    resolved, resolve_errors = resolve_constants(parsed)
    print("\nпосле разрешения констант:")
    print(resolved)
    #ошибки 
    if resolve_errors:
        print("\nошибки разрешения констант:")
        i = 1
        for var, errs in resolve_errors.items():
            for err in errs:
                print(f"  {i}) {var}: {err}")
                i += 1


if __name__ == "__main__":
    main()