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
    app = MainApp(system)
    app.mainloop()
