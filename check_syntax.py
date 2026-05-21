#!/usr/bin/env python3
"""Проверка синтаксиса Python файлов после рефакторинга"""

import os
import sys
import subprocess

def check_python_syntax(filepath):
    """Проверяет синтаксис Python файла"""
    try:
        # Пытаемся выполнить компиляцию файла
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, filepath, 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error in {filepath}: {e}"
    except Exception as e:
        return False, f"Error reading {filepath}: {e}"

def main():
    # Файлы для проверки
    files_to_check = [
        "services/Auth/crud.py",
        "services/Auth/auth_logic.py",
        "services/Auth/routers/auth.py",
        "services/Auth/routers/users.py",
        "services/Auth/dependencies.py",
        "services/Memory/crud.py",
        "database/models/auth.py",
        "database/models/memory.py",
        "database/models/access.py"
    ]
    
    print("Проверка синтаксиса файлов после рефакторинга моделей...")
    print("=" * 60)
    
    all_ok = True
    for filepath in files_to_check:
        if os.path.exists(filepath):
            ok, error = check_python_syntax(filepath)
            if ok:
                print(f"OK: {filepath}")
            else:
                print(f"ERROR: {error}")
                all_ok = False
        else:
            print(f"! Файл не найден: {filepath}")
            all_ok = False
    
    print("=" * 60)
    if all_ok:
        print("Все файлы прошли проверку синтаксиса!")
    else:
        print("Обнаружены ошибки синтаксиса.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())