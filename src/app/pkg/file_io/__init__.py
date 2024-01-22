from exceptions import FileException
from const import SHOULD_REQUEST_WITH_STORE_FLAG_STR


def store_text_as_file(html: str, file_name: str):
    with open(file_name, 'w') as file:
        file.write(html)

def restore_text_from_file(file_name: str) -> str:
    try:
        with open(file_name, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileException(f"Stored file does not exist. Please run this function with {SHOULD_REQUEST_WITH_STORE_FLAG_STR} to create it.")
