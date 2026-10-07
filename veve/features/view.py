from datetime import datetime
import re
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QCheckBox,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel
)

from .model import Driver, Violation, VehicleRecord
from .service import VehicleService

SEX_OPTIONS = ["Male", "Female", "Other", "Prefer not to say"]
VEHICLE_TYPES = ["Motorcycle", "Truck", "Bus", "Van", "Car"]

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
LICENSE_REGEX = r"^[A-Za-z]\d{2}-\d{2}-\d{6}$"
PHONE_REGEX = r"^(09|\+639)\d{9}$"
PLATE_REGEX = r"^[A-Za-z]{2,3}\s?\d{3,4}$"

VIOLATION_FINES = {
    "Speeding": {1: 1000.0, 2: 3000.0},
    "Reckless Driving": {1: 2000.0, 2: 3000.0},
    "Red Light Violation": {1: 1500.0, 2: 3000.0},
    "Illegal Parking": {1: 500.0, 2: 1000.0},
    "Driving Without License": {1: 3000.0, 2: 5000.0},
    "Expired Registration": {1: 1000.0, 2: 2000.0},
    "DUI / Driving Under Influence": {1: 5000.0, 2: 10000.0},
    "Seatbelt Violation": {1: 500.0, 2: 1000.0},
    "Failure to Yield": {1: 1000.0, 2: 2000.0},
    "Illegal Turn": {1: 750.0, 2: 1500.0},
    "Use of Mobile Device While Driving": {1: 1200.0, 2: 2500.0}
}

class VehicleView(QWidget):
    def __init__(self, service: VehicleService):
        super().__init__()
        self.service = service
        self.setWindowTitle("Vehicle Violation Management System")
        self.resize(1400, 750)
        self.build_ui()
        self.refresh()
    
    def build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        forms_layout = QHBoxLayout()
        forms_layout.setSpacing(40)

        # --- 1. Left Side: Person Identification ---
        person_widget = QWidget()
        person_grid = QGridLayout(person_widget)
        person_grid.setContentsMargins(0, 0, 0, 0)
        person_grid.setSpacing(12)

        self.name_input = QLineEdit()
        self.has_license_checkbox = QCheckBox("Driver Has Valid License")
        self.has_license_checkbox.setChecked(True)
        self.has_license_checkbox.toggled.connect(self.toggle_license_input)

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("e.g. A01-23-456789")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g. 09123456789")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. driver@example.com")
        self.sex_input = QComboBox()
        self.sex_input.addItems(SEX_OPTIONS)

        person_grid.addWidget(QLabel("<b>Person Identification</b>"), 0, 0, 1, 2)
        person_grid.addWidget(QLabel("Driver Name:"), 1, 0)
        person_grid.addWidget(self.name_input, 1, 1)
        person_grid.addWidget(QLabel("License Status:"), 2, 0)
        person_grid.addWidget(self.has_license_checkbox, 2, 1)
        person_grid.addWidget(QLabel("License Number:"), 3, 0)
        person_grid.addWidget(self.license_input, 3, 1)
        person_grid.addWidget(QLabel("Contact Phone:"), 4, 0)
        person_grid.addWidget(self.phone_input, 4, 1)
        person_grid.addWidget(QLabel("Driver Email:"), 5, 0)
        person_grid.addWidget(self.email_input, 5, 1)
        person_grid.addWidget(QLabel("Sex / Gender:"), 6, 0)
        person_grid.addWidget(self.sex_input, 6, 1)

        # --- 2. Right Side: Vehicle & Violation Details ---
        vehicle_widget = QWidget()
        vehicle_grid = QGridLayout(vehicle_widget)
        vehicle_grid.setContentsMargins(0, 0, 0, 0)
        vehicle_grid.setSpacing(12)

        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("e.g. ABC 1234")
        self.type_input = QComboBox()
        self.type_input.addItems(VEHICLE_TYPES)
        
        # Violation Selection Table
        self.violation_table = QTableWidget(len(VIOLATION_FINES), 3)
        self.violation_table.setHorizontalHeaderLabels(["Select", "Violation", "Offense Level"])
        self.violation_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.violation_table.setFixedHeight(180)

        self.violation_widgets = {}

        for row, (v_name, f_rates) in enumerate(VIOLATION_FINES.items()):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            self.violation_table.setItem(row, 0, chk_item)

            name_item = QTableWidgetItem(v_name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.violation_table.setItem(row, 1, name_item)

            combo = QComboBox()
            combo.addItem(f"1st Offense (${f_rates[1]:.0f})", 1)
            combo.addItem(f"2nd Offense (${f_rates[2]:.0f})", 2)
            combo.currentIndexChanged.connect(self.calculate_total_fine)
            self.violation_table.setCellWidget(row, 2, combo)

            self.violation_widgets[v_name] = {"chk_item": chk_item, "combo": combo}

        self.violation_table.itemChanged.connect(self.calculate_total_fine)

        # Read-Only Total Fine Display
        self.fine_input = QLineEdit("0.00")
        self.fine_input.setReadOnly(True)

        vehicle_grid.addWidget(QLabel("<b>Vehicle & Violation Details</b>"), 0, 0, 1, 2)
        vehicle_grid.addWidget(QLabel("Plate Number:"), 1, 0)
        vehicle_grid.addWidget(self.plate_input, 1, 1)
        vehicle_grid.addWidget(QLabel("Vehicle Type:"), 2, 0)
        vehicle_grid.addWidget(self.type_input, 2, 1)
        vehicle_grid.addWidget(QLabel("Violations:"), 3, 0, Qt.AlignmentFlag.AlignTop)
        vehicle_grid.addWidget(self.violation_table, 3, 1)
        vehicle_grid.addWidget(QLabel("Total Fine ($):"), 4, 0)
        vehicle_grid.addWidget(self.fine_input, 4, 1)

        forms_layout.addWidget(person_widget, 1, Qt.AlignmentFlag.AlignTop)
        forms_layout.addWidget(vehicle_widget, 1, Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(forms_layout)

        # --- Action Buttons ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        add_button = QPushButton("Add Record")
        add_button.clicked.connect(self.add_vehicle)
        button_layout.addWidget(add_button)

        update_button = QPushButton("Update Selected")
        update_button.clicked.connect(self.update_vehicle)
        button_layout.addWidget(update_button)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_vehicle)
        button_layout.addWidget(delete_button)

        main_layout.addLayout(button_layout)
        
        # --- Results Table ---
        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels([
            "Has License", "License No / ID", "Driver Name", "Phone No", "Email", "Sex", "Plate Num", "Vehicle Type", "Violations Charged", "Fine ($)", "Date Created"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        
        main_layout.addWidget(self.table)

    def calculate_total_fine(self) -> None:
        total = 0.0
        for v_name, widgets in self.violation_widgets.items():
            if widgets["chk_item"].checkState() == Qt.CheckState.Checked:
                offense_level = widgets["combo"].currentData()
                total += VIOLATION_FINES[v_name][offense_level]
        self.fine_input.setText(f"{total:.2f}")

    def toggle_license_input(self, checked: bool) -> None:
        self.license_input.setEnabled(checked)
        if not checked:
            self.license_input.clear()
            self.license_input.setPlaceholderText("Unlicensed Driver")
        else:
            self.license_input.setPlaceholderText("e.g. A01-23-456789")

    def get_input_record(self) -> VehicleRecord:
        driver_name = self.name_input.text().strip()
        has_lic = self.has_license_checkbox.isChecked()
        license_num = self.license_input.text().strip()
        plate_num = self.plate_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()

        # 1. Driver Name Validation
        if not driver_name:
            raise ValueError("Driver Name cannot be empty.")

        # 2. Driver Email Validation
        if not email:
            raise ValueError("Driver Email cannot be empty.")
        elif not re.match(EMAIL_REGEX, email):
            raise ValueError("Invalid email format (e.g. driver@example.com).")

        # 3. Contact Phone Validation (if provided)
        if phone and not re.match(PHONE_REGEX, phone):
            raise ValueError("Invalid contact phone format (e.g. 09123456789 or +639123456789).")

        # 4. License Number Validation
        if has_lic:
            if not license_num:
                raise ValueError("License Number is required for licensed drivers.")
            elif not re.match(LICENSE_REGEX, license_num):
                raise ValueError("Invalid License Number format (e.g. A01-23-456789).")

        # 5. Plate Number Validation
        if not plate_num:
            raise ValueError("Plate Number cannot be empty.")
        elif not re.match(PLATE_REGEX, plate_num):
            raise ValueError("Invalid Plate Number format (e.g. ABC 1234 or AB 123).")

        # 6. Violations Check
        violations = []
        for v_name, widgets in self.violation_widgets.items():
            if widgets["chk_item"].checkState() == Qt.CheckState.Checked:
                offense_level = widgets["combo"].currentData()
                offense_str = "1st Offense" if offense_level == 1 else "2nd Offense"
                violations.append(f"{v_name} ({offense_str})")

        if not violations:
            raise ValueError("Please check at least one violation charge.")

        fine_val = float(self.fine_input.text())

        driver = Driver(
            licensenum=license_num.upper() if has_lic else f"UNLICENSED-{plate_num.upper()}",
            drivername=driver_name,
            has_license=has_lic,
            phone=phone,
            email=email,
            sex=self.sex_input.currentText(),
        )

        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        violation = Violation(
            platenum=plate_num.upper(),
            licensenum=driver.licensenum,
            vehicletype=self.type_input.currentText(),
            violations=violations,
            fine=fine_val,
            date_created=current_timestamp
        )

        return VehicleRecord(driver=driver, violation=violation)

    def add_vehicle(self) -> None:
        try:
            record = self.get_input_record()
            self.service.add_Vehicle(record)
            QMessageBox.information(self, "Success", f"Record for plate '{record.violation.platenum}' added successfully at {record.violation.date_created}!")
            self.refresh()
            self.clear_inputs()
        except ValueError as val_err:
            QMessageBox.warning(self, "Validation Error", str(val_err))

    def update_vehicle(self) -> None:
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a record from the table to update.")
            return

        try:
            record = self.get_input_record()
            self.service.update_vehicle(record)
            QMessageBox.information(self, "Success", f"Record for plate '{record.violation.platenum}' updated successfully!")
            self.refresh()
            self.clear_inputs()
        except ValueError as error:
            QMessageBox.warning(self, "Validation Error", str(error))
        except Exception as err:
            QMessageBox.critical(self, "Update Error", f"Failed to update record:\n{str(err)}")

    def delete_vehicle(self) -> None:
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a row to delete.")
            return

        row = selected_rows[0].row()
        platenum = self.table.item(row, 6).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the record for plate number '{platenum}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_vehicle(platenum)
                self.refresh()
                self.clear_inputs()
            except Exception as err:
                QMessageBox.critical(self, "Delete Error", f"Failed to delete record:\n{str(err)}")

    def on_row_selected(self) -> None:
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        items = [self.table.item(row, col) for col in range(11)]

        if all(items):
            is_licensed = items[0].text() == "Yes"
            self.has_license_checkbox.setChecked(is_licensed)
            
            if is_licensed:
                self.license_input.setText(items[1].text())
            else:
                self.license_input.clear()

            self.name_input.setText(items[2].text())
            self.phone_input.setText(items[3].text())
            self.email_input.setText(items[4].text())

            sex_idx = self.sex_input.findText(items[5].text())
            if sex_idx >= 0:
                self.sex_input.setCurrentIndex(sex_idx)

            self.plate_input.setText(items[6].text())

            type_idx = self.type_input.findText(items[7].text())
            if type_idx >= 0:
                self.type_input.setCurrentIndex(type_idx)

            raw_violations = items[8].text().split(",")
            charged_list = [v.strip() for v in raw_violations]

            self.violation_table.blockSignals(True)
            for v_name, widgets in self.violation_widgets.items():
                is_checked = False
                for charged in charged_list:
                    if v_name in charged:
                        is_checked = True
                        if "2nd Offense" in charged:
                            widgets["combo"].setCurrentIndex(1)
                        else:
                            widgets["combo"].setCurrentIndex(0)
                        break
                
                widgets["chk_item"].setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            self.violation_table.blockSignals(False)

            self.calculate_total_fine()

    def clear_inputs(self) -> None:
        try:
            self.table.itemSelectionChanged.disconnect(self.on_row_selected)
        except TypeError:
            pass

        self.table.clearSelection()

        self.has_license_checkbox.setChecked(True)
        self.license_input.clear()
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.sex_input.setCurrentIndex(0)

        self.plate_input.clear()
        self.type_input.setCurrentIndex(0)

        self.violation_table.blockSignals(True)
        for widgets in self.violation_widgets.values():
            widgets["chk_item"].setCheckState(Qt.CheckState.Unchecked)
            widgets["combo"].setCurrentIndex(0)
        self.violation_table.blockSignals(False)

        self.fine_input.setText("0.00")

        self.table.itemSelectionChanged.connect(self.on_row_selected)
        
    def refresh(self) -> None:
        self.table.blockSignals(True)
        records = self.service.get_Vehicle()
        self.table.setRowCount(len(records))
        
        for row, rec in enumerate(records):
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
                f"${rec.violation.fine:.2f}",
                rec.violation.date_created
            ]
            for column, value in enumerate(values):
                self.table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )
        self.table.blockSignals(False)
