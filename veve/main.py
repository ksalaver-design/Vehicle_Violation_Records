import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from database.database import Database
from features.service import VehicleService
from features.view import VehicleView
from features.search_view import SearchVehicleView

class MainWindow(QMainWindow):
    def __init__(self, service: VehicleService):
        super().__init__()
        self.setWindowTitle("Vehicle Violation System")
        self.resize(1180, 720)

        # Tab navigation container
        self.tabs = QTabWidget()
        
        # Views
        self.management_view = VehicleView(service)
        self.search_view = SearchVehicleView(service)

        # Add tabs
        self.tabs.addTab(self.management_view, "Manage Records")
        self.tabs.addTab(self.search_view, "Search Vehicles")

        # Refresh search list whenever switching tabs
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.setCentralWidget(self.tabs)

    def on_tab_changed(self, index: int) -> None:
        if index == 1:
            self.search_view.refresh()

def main():
    app = QApplication(sys.argv)
    
    db = Database()
    service = VehicleService(db)
    
    window = MainWindow(service)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()