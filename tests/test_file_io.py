import os
from file_io import store_text_as_file, restore_text_from_file


class TestFileIO:
    def test_store_text_as_file_stores_text(self, tmp_path):
        file_name = tmp_path / 'test_file.txt'
        text = 'test text'
        try:
            store_text_as_file(text, file_name)
            assert file_name.read_text() == text
        finally:
            if file_name.exists():
                os.remove(file_name)
                assert file_name.exists() == False

    def test_restore_text_from_file_restores_text(self, tmp_path):
        file_name = tmp_path / 'test_file.txt'
        text = 'test text'
        try:
            file_name.write_text(text)
            assert restore_text_from_file(file_name) == text
        finally:
            if file_name.exists():
                os.remove(file_name)
                assert file_name.exists() == False
