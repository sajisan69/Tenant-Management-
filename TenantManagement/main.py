import os
from models.building import Building
from gui_app import MainApp
def setup_directories():
    for folder in ["data", "exports"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created directory: {folder}")

if __name__ == "__main__":
    setup_directories()
    system = Building()
    if not system.flats:
        print("🌱 First run detected. Seeding data...")
        system.add_flat("101", "1", "15000")
        system.add_flat("102", "1", "16000")
    app = MainApp(system)
    app.mainloop()
