import os
import logging
from functools import wraps

class FileNotFound(Exception):
    pass

class FileCorrupted(Exception):
    pass

def logged(exc_type, mode="console"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exc_type as e:
                logger = logging.getLogger(func.__name__)
                logger.setLevel(logging.ERROR)

                handler = logging.StreamHandler() if mode == "console" else logging.FileHandler("log.txt", mode="a", encoding="utf-8")
                handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

                logger.addHandler(handler)
                logger.error(str(e))
                handler.close()
                logger.removeHandler(handler)
                raise e
        return wrapper
    return decorator


class FileManager:
    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            raise FileNotFound(f"Файл '{self.path}' не знайдено!")
        if not os.access(self.path, os.R_OK):
            raise FileCorrupted("Неможливо прочитати файл!")

    @logged(FileCorrupted, mode="file")
    def read(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return [line.strip().split(",") for line in f.readlines()]
        except:
            raise FileCorrupted("Файл пошкоджений або недоступний!")

    @logged(FileCorrupted, mode="console")
    def write(self, data: list):
        try:
            with open(self.path, mode="w", newline="", encoding="utf-8") as f:
                for row in data:
                    f.write(",".join(map(str, row)) + "\n")
        except:
            raise FileCorrupted("Не вдалося записати файл!")

    @logged(FileCorrupted, mode="file")
    def append(self, row: list):
        try:
            if len(row) != 1 or not isinstance(row[0], (int, float)):
                raise FileCorrupted("Дозволено додавати лише одне число!")
            new_value = row[0]
            data = self.read()
            if data:
                total = 0
                for r in data:
                    for x in r:
                        if x.replace('.', '', 1).isdigit():
                            total += float(x)
                new_value = total + new_value
            row = [new_value]
            with open(self.path, mode="a", newline="", encoding="utf-8") as f:
                f.write(",".join(map(str, row)) + "\n")
        except:
            raise FileCorrupted("Не вдалося дописати у файл!")

def main():
    fm = FileManager("data.csv")

    print("READ:")
    print(fm.read())

    fm.append([10])

    print("AFTER APPEND:")
    print(fm.read())



    print("AFTER WRITE:")
    print(fm.read())

main()
