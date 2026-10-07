from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QDialog,
    QFrame
)
from .service import VehicleService


class TicketDialog(QDialog):
    """Custom GUI Dialog for displaying a formatted ticket."""
    def __init__(self, ticket_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Violation Citation - {ticket_data['plate_num']}")
        self.setFixedSize(420, 520)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Header Title
        title_label = QLabel("TRAFFIC VIOLATION CITATION")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #b30000;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Official Notice of Traffic Infraction")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 11px; color: #666; margin-bottom: 5px;")
        main_layout.addWidget(subtitle_label)

        # Separator Line
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line1)

        # Details Form
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setVerticalSpacing(10)

        # Plate Number
        plate_val = QLabel(ticket_data["plate_num"])
        plate_val.setStyleSheet("font-weight: bold; font-size: 14px;")
        form_layout.addRow("Plate Number:", plate_val)

        # Vehicle Type
        form_layout.addRow("Vehicle Type:", QLabel(ticket_data["vehicle_type"]))

        # Driver Name
        form_layout.addRow("Driver Name:", QLabel(ticket_data["driver_name"]))

        # License Number & Status
        lic_status = "Licensed" if ticket_data["has_license"] == "Yes" else "Unlicensed"
        form_layout.addRow("License ID:", QLabel(f"{ticket_data['license_num']} ({lic_status})"))

        # Contact Details
        form_layout.addRow("Contact Phone:", QLabel(ticket_data["phone"]))
        form_layout.addRow("Driver Email:", QLabel(ticket_data["email"]))
        form_layout.addRow("Sex / Gender:", QLabel(ticket_data["sex"]))

        # Violations Charged
        v_label = QLabel(ticket_data["violations"])
        v_label.setWordWrap(True)
        form_layout.addRow("Violations:", v_label)

        main_layout.addLayout(form_layout)

        # Separator Line
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line2)

        # Total Fine Box
        fine_box = QHBoxLayout()
        fine_title = QLabel("TOTAL FINE:")
        fine_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #b30000;")
        fine_val = QLabel(ticket_data["fine"])
        fine_val.setStyleSheet("font-size: 16px; font-weight: bold; color: #b30000;")
        fine_box.addWidget(fine_title)
        fine_box.addStretch()
        fine_box.addWidget(fine_val)
        main_layout.addLayout(fine_box)

        # Footer Notice
        footer_label = QLabel("Please settle fine payments within 7 working days.")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("font-size: 10px; color: #888; font-style: italic;")
        main_layout.addWidget(footer_label)

        # Close Button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn)


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

        # Show GUI ticket dialog when row selection changes
        self.table.itemSelectionChanged.connect(self.show_ticket)

        layout.addWidget(self.table)

    def clear_search(self) -> None:
        self.search_input.clear()
        self.refresh()

    def show_ticket(self) -> None:
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return

        row = selected_rows[0].row()

        ticket_data = {
            "has_license": self.table.item(row, 0).text(),
            "license_num": self.table.item(row, 1).text(),
            "driver_name": self.table.item(row, 2).text(),
            "phone": self.table.item(row, 3).text(),
            "email": self.table.item(row, 4).text(),
            "sex": self.table.item(row, 5).text(),
            "plate_num": self.table.item(row, 6).text(),
            "vehicle_type": self.table.item(row, 7).text(),
            "violations": self.table.item(row, 8).text(),
            "fine": self.table.item(row, 9).text()
        }

        # Open pure PyQt6 GUI dialog
        dialog = TicketDialog(ticket_data, parent=self)
        dialog.exec()

    def refresh(self) -> None:
        try:
            self.table.itemSelectionChanged.disconnect(self.show_ticket)
        except TypeError:
            pass

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

        self.table.itemSelectionChanged.connect(self.show_ticket)
