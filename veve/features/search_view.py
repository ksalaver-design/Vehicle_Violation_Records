from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel
)
from .service import VehicleService

class SearchVehicleView(QWidget):
    def __init__(self, service: VehicleService):
        super().__init__()
        self.service = service
        self.build_ui()
        self.refresh()

    def build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # --- Search Control ---
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Plate Number, Driver Name, or License No...")
        self.search_input.textChanged.connect(self.refresh)

        clear_btn = QPushButton("Clear Search")
        clear_btn.clicked.connect(self.clear_search)

        search_layout.addWidget(QLabel("Search Vehicle:"))
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(clear_btn)

        layout.addLayout(search_layout)

        # --- Search Results Table ---
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels([
            "Has License", "License No / ID", "Driver Name", "Phone No", "Email", "Sex", "Plate Num", "Vehicle Type", "Violations Charged", "Fine ($)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        layout.addWidget(self.table)

    def clear_search(self) -> None:
        self.search_input.clear()
        self.refresh()

    def refresh(self) -> None:
        query = self.search_input.text().strip().lower()
        records = self.service.get_Vehicle()
        
        filtered_records = []
        for rec in records:
            matches_query = (
                not query
                or query in rec.violation.platenum.lower()
                or query in rec.driver.drivername.lower()
                or query in rec.driver.licensenum.lower()
            )

            if matches_query:
                filtered_records.append(rec)

        self.table.setRowCount(len(filtered_records))
        for row, rec in enumerate(filtered_records):
            violations_text = ", ".join(rec.violation.violations) if rec.violation.violations else "None"
            values = [
                "Yes" if rec.driver.has_license else "No",
                rec.driver.licensenum,
                rec.driver.drivername,
                rec.driver.phone,
                rec.driver.email,
                rec.driver.sex,
                rec.violation.platenum,
                rec.violation.vehicletype,
                violations_text,
                f"${rec.violation.fine:.2f}"
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(str(value)))