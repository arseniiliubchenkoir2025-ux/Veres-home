import os
import logging
from functools import wraps
import sys

LOGGER = logging.getLogger(__name__)


def setup_logging():
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler("log.txt", mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.ERROR)

    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(console_handler)
    LOGGER.addHandler(file_handler)


class FileNotFound(Exception):
    pass


class FileCorrupted(Exception):
    pass

def logged(exc_type, mode=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exc_type as e:
                LOGGER.error("Помилка у функції '%s': %s", func.__name__, str(e), exc_info=True)
                raise e

        return wrapper

    return decorator


class FileManager:
    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            raise FileNotFound(f"Файл '{self.path}' не знайдено!")

    @logged(FileCorrupted)
    def read(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return [line.strip().split(",") for line in f.readlines()]
        except PermissionError:
            raise FileCorrupted(f"Неможливо прочитати файл '{self.path}': недостатньо прав!")
        except Exception:
            raise FileCorrupted("Файл пошкоджений або недоступний!")

    @logged(FileCorrupted)
    def write(self, data: list):
        try:
            with open(self.path, mode="w", newline="", encoding="utf-8") as f:
                for row in data:
                    f.write(",".join(map(str, row)) + "\n")
        except PermissionError:
            raise FileCorrupted(f"Неможливо записати у файл '{self.path}': недостатньо прав!")
        except Exception:
            raise FileCorrupted("Не вдалося записати файл!")

    @logged(FileCorrupted)
    def append(self, row: list):
        try:
            if len(row) != 1 or not isinstance(row[0], (int, float)):
                raise FileCorrupted("Дозволено додавати лише одне число!")

            value_to_add = float(row[0])
            data = self.read()
            total = 0.0

            for r in data:
                for x in r:
                    try:
                        total += float(x)
                    except ValueError:
                        pass

            value_to_append = total + value_to_add

            with open(self.path, mode="a", encoding="utf-8") as f:
                f.write(str(value_to_append) + "\n")

        except PermissionError:
            raise FileCorrupted(f"Неможливо дописати у файл '{self.path}': недостатньо прав!")
        except Exception:
            raise FileCorrupted("Не вдалося дописати у файл данні!")


def main():
    setup_logging()

    if not os.path.exists("data.csv"):
        with open("data.csv", "w") as f:
            f.write("1,2,3\n")
            f.write("4\n")

    try:
        fm = FileManager("data.csv")
    except FileNotFound as e:
        print(e)
        return

    print("READ:")
    print(fm.read())

    fm.append([10])

    print("AFTER APPEND:")
    print(fm.read())

    fm.write([["New Data"], [101]])

    print("AFTER WRITE:")
    print(fm.read())


if __name__ == '__main__':
    main()
