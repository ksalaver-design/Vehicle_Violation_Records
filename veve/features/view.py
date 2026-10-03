from datetime import datetime
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
    QListWidget,
    QListWidgetItem,
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
COMMON_VIOLATIONS = [
    "Speeding",
    "Red Light Violation",
    "Reckless Driving",
    "Illegal Parking",
    "Driving Without License",
    "Expired Registration",
    "DUI / Driving Under Influence",
    "Seatbelt Violation",
    "Failure to Yield",
    "Illegal Turn",
    "Use of Mobile Device While Driving"
]

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

        # --- Balanced Two-Column Layout ---
        forms_layout = QHBoxLayout()
        forms_layout.setSpacing(40)  # Spaced wider apart

        # 1. Left Side: Person Identification
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

        # 2. Right Side: Vehicle & Violation Details
        vehicle_widget = QWidget()
        vehicle_grid = QGridLayout(vehicle_widget)
        vehicle_grid.setContentsMargins(0, 0, 0, 0)
        vehicle_grid.setSpacing(12)

        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("e.g. ABC 1234")
        self.type_input = QComboBox()
        self.type_input.addItems(VEHICLE_TYPES)
        
        self.violation_list_widget = QListWidget()
        for v_name in COMMON_VIOLATIONS:
            item = QListWidgetItem(v_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.violation_list_widget.addItem(item)
            
        self.violation_list_widget.setFixedHeight(110)
        
        self.fine_input = QLineEdit()
        self.fine_input.setPlaceholderText("0.00")

        vehicle_grid.addWidget(QLabel("<b>Vehicle & Violation Details</b>"), 0, 0, 1, 2)
        vehicle_grid.addWidget(QLabel("Plate Number:"), 1, 0)
        vehicle_grid.addWidget(self.plate_input, 1, 1)
        vehicle_grid.addWidget(QLabel("Vehicle Type:"), 2, 0)
        vehicle_grid.addWidget(self.type_input, 2, 1)
        vehicle_grid.addWidget(QLabel("Violations:"), 3, 0, Qt.AlignmentFlag.AlignTop)
        vehicle_grid.addWidget(self.violation_list_widget, 3, 1)
        vehicle_grid.addWidget(QLabel("Fine Amount ($):"), 4, 0)
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
        
        # Smooth horizontal scrolling with auto-stretch
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)  # Give extra space to 'Violations Charged'
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        
        main_layout.addWidget(self.table)

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
        fine_text = self.fine_input.text().strip()

        if not driver_name:
            raise ValueError("Driver Name cannot be empty.")
        
        if has_lic and not license_num:
            raise ValueError("License Number is required for licensed drivers.")
            
        if not plate_num:
            raise ValueError("Plate Number cannot be empty.")

        if not fine_text:
            fine_val = 0.0
        else:
            try:
                fine_val = float(fine_text)
                if fine_val < 0:
                    raise ValueError("Fine amount cannot be negative.")
            except ValueError:
                raise ValueError("Fine amount must be a valid number (e.g., 150.00).")

        violations = []
        for index in range(self.violation_list_widget.count()):
            item = self.violation_list_widget.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                violations.append(item.text())

        if not violations:
            raise ValueError("Please check at least one violation charge.")

        driver = Driver(
            licensenum=license_num if has_lic else f"UNLICENSED-{plate_num}",
            drivername=driver_name,
            has_license=has_lic,
            phone=self.phone_input.text().strip(),
            email=self.email_input.text().strip(),
            sex=self.sex_input.currentText(),
        )

        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        violation = Violation(
            platenum=plate_num,
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
            self.clear_inputs()
            self.refresh()
        except ValueError as val_err:
            QMessageBox.warning(self, "Validation Error", str(val_err))
        except sqlite3.IntegrityError as db_err:
            if "UNIQUE constraint failed" in str(db_err) or "PRIMARY KEY" in str(db_err):
                QMessageBox.critical(self, "Database Error", "A vehicle record with this Plate Number already exists.")
            else:
                QMessageBox.critical(self, "Database Constraint Error", f"Database constraint violation: {db_err}")
        except Exception as err:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred while adding the record:\n{str(err)}")

    def update_vehicle(self) -> None:
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a record from the table to update.")
            return

        try:
            record = self.get_input_record()
            self.service.update_vehicle(record)
            QMessageBox.information(self, "Success", f"Record for plate '{record.violation.platenum}' updated successfully!")
            self.clear_inputs()
            self.refresh()
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
                self.clear_inputs()
                self.refresh()
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

            for index in range(self.violation_list_widget.count()):
                item = self.violation_list_widget.item(index)
                if item.text() in charged_list:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)

            raw_fine = items[9].text().replace("$", "").strip()
            self.fine_input.setText(raw_fine)

    def clear_inputs(self) -> None:
        self.table.blockSignals(True)
        self.has_license_checkbox.setChecked(True)
        self.license_input.clear()
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.sex_input.setCurrentIndex(0)

        self.plate_input.clear()
        self.type_input.setCurrentIndex(0)

        for index in range(self.violation_list_widget.count()):
            self.violation_list_widget.item(index).setCheckState(Qt.CheckState.Unchecked)

        self.fine_input.clear()
        self.table.clearSelection()
        self.table.blockSignals(False)
        
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