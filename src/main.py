# -*- coding: utf-8 -*-
import sys
import re
from collections import namedtuple
import yaml


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
            regex = re.compile(pattern)
            match = regex.match(text, pos)
            if match:
                if token_type != 'SKIP':
                    tokens.append(Token(token_type, match.group(0)))
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
        tok = current()
        if tok is None:
            errors.append(f"ожидался {token_type}, но достигнут конец файла")
            return None
        if tok.type != token_type:
            errors.append(f"ожидался {token_type}, а получен {tok}")
            return None
        advance()
        return tok

    def parse_value():
        tok = current()
        if tok is None:
            errors.append("ожидалось значение, но конец файла")
            return None
        # число
        if tok.type == "NUMBER":
            advance()
            try:
                return int(tok.value, 8)
            except:
                errors.append(f"некорректное число: {tok.value}")
                return None
        # массив
        elif tok.type == "LBRACE":
            advance()
            arr = []
            while True:
                tok = current()
                if tok is None:
                    errors.append("не закрыта фигурная скобка { ... }")
                    break
                if tok.type == "RBRACE":
                    advance()
                    break
                val = parse_value()
                if val is not None:
                    arr.append(val)
                tok = current()
                if tok and tok.type == "COMMA":
                    advance()
                elif tok and tok.type == "RBRACE":
                    continue
                elif tok:
                    errors.append(f"недопустимый токен в массиве: {tok}")
                    advance()
                    break
            return arr
        # ссылка
        elif tok.type == "LBRACKET":
            advance()
            ident_tok = expect("IDENT")
            ident = ident_tok.value if ident_tok else None
            expect("RBRACKET")
            if ident is None:
                return None
            return ("ref", ident)
        else:
            errors.append(f"ожидалось число, массив или ссылку, а получено {tok}")
            advance()
            return None

    while pos < len(tokens):
        tok = current()
        if tok.type == "IDENT":
            name = tok.value
            advance()
            expect("IS")
            val = parse_value()
            expect("SEMICOLON")
            data[name] = val
        # ссылка вне присваивания
        elif tok.type == "LBRACKET":
            val = parse_value()
            ref_name = f"_ref_at_{pos}"
            data[ref_name] = val
        else:
            errors.append(f"неожиданный токен {tok}")
            advance()
    return data, errors


#константы
def resolve_constants(data):
    errors = {}
    resolved = {}

    def resolve_value(val, where):
        if isinstance(val, int):
            return val
        if isinstance(val, list):
            return [resolve_value(item, where) for item in val]
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

#подготовка к записи в файл
def write_yaml(data, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                allow_unicode=True, 
                default_flow_style=False, 
                sort_keys=False  
            )
    except Exception as e:
        print(f"ошибка при записи YAML: {e}")

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

    #6. запись в файл
    if resolve_errors:
        print("\nфайл не создан из-за ошибок констант.")
        return
    write_yaml(resolved, output_file)
    print(f"\nуспешно сохранено в {output_file}")


if __name__ == "__main__":
    main()