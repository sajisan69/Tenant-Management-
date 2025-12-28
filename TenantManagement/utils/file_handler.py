import json
import csv
import os

class FileHandler:
    @staticmethod
    def _ensure_dir(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def save_json(filename, data):
        FileHandler._ensure_dir('data')
        filepath = os.path.join('data', filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_json(filename):
        filepath = os.path.join('data', filename)
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    @staticmethod
    def export_to_csv(filename, data, headers):
        FileHandler._ensure_dir('exports')
        filepath = os.path.join('exports', filename)
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            return True, filepath
        except Exception as e:
            return False, str(e)

    @staticmethod
    def save_receipt(filename, content):
        FileHandler._ensure_dir('receipts')
        filepath = os.path.join('receipts', filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath