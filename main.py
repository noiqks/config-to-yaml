# -*- coding: utf-8 -*-
import sys
import re

#читает файл и возвращает текст
def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

#удаляет многострочные комментарии =begin ... =end
def remove_com(text):
    pattern = r"=begin.*?=end"
    return re.sub(pattern, '', text, flags=re.DOTALL)#захватывает переносы строк

def main():
    if len(sys.argv) != 3:
        print("Использование: python main.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    #1.чтение файла и обработка файла
    text = read_file(input_file)
    print("исходный текст файла:")
    print(text)

    clean_text = remove_com(text)
    print("\nтекст после удаления комментариев:")
    print(clean_text)

if __name__ == "__main__":
    main()