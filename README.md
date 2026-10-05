# 🚔 Vehicle Violation Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green?logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Package Manager](https://img.shields.io/badge/Package_Manager-uv-purple)](https://github.com/astral-sh/uv)

A desktop application designed to record, track, and manage traffic citations and driver records with real-time dynamic search and persistent SQLite storage.

---

## 📌 Project Overview

### Problem Statement
Manual traffic citation logging often leads to duplicate entries, missing driver records, inconsistent fine calculations, and slow data retrieval during roadside audits.

## Project Description
The **Vehicle Violation Management System** is a desktop-based application developed using Python, PyQt6, and SQLite.
It provides a centralized digital solution for traffic enforcement officers and administrative personnel to record, manage, and query vehicle traffic citations and driver records.

Manual traffic enforcement record-keeping often suffers from misplaced physical citations, duplicate data entry, difficulty tracking unpaid fines, and slow search retrieval during roadside or administrative audits.
This system addresses these issues by offering a structured, digitized workflow with real-time dynamic search, multi-selection citation logging, and data constraint enforcement.

---

## ✨ Features

- 👤 **Driver Profile Management**: Logs full driver names, license validity status, contact numbers, email addresses, and sex/gender.
- 🚘 **Citation Logging**: Tracks vehicle types, plate numbers, fine amounts, and automatically records creation timestamps (`date_created`).
- 🔘 **Multi-Violation Selection**: Allows selection of single or multiple infractions per ticket using interactive checkboxes.
- ⚡ **Full CRUD Capabilities**: Create, Read, Update, and Delete citation entries seamlessly.
- 🔍 **Real-Time Dynamic Search**: Instantly filters table records as queries are typed into the search bar.
- 🛡️ **Robust Error Handling**: Prevents empty field submissions, negative fine amounts, and duplicate primary key collisions via interactive modal alerts.

---

## 🛠️ Technologies Used

| Technology | Role / Usage |
| :--- | :--- |
| **Python 3.10+** | Primary Programming Language |
| **PyQt6** | Graphical User Interface (GUI) Framework |
| **SQLite 3** | Local Relational Database Storage |
| **uv / pip** | Virtual Environment & Dependency Management |
| **Architecture** | Model-View-Service-Repository (Layered Pattern) |

---

## 📁 Project Structure

```text
veve/
├── 📂 database/
│   └── database.py       # SQLite connection & schema initialization
├── 📂 features/
│   ├── model.py          # Dataclass models (Driver, Violation, VehicleRecord)
│   ├── repository.py     # SQL CRUD query implementations
│   ├── service.py        # Domain business logic layer
│   ├── view.py           # Primary PyQt6 management GUI (1400x750 layout)
│   └── search_view.py    # Real-time search interface
├── main.py               # Main window initialization & tab routing
├── pyproject.toml        # Environment configuration and dependencies
└── README.md             # Project documentation
```
🚀 Installation & Setup

Ensure you have Python 3.10+ and PyQt6 installed on your system.

How to Use the System

- Add a Record: Fill in the Driver Identification form on the left, pick vehicle details and check violations on the right, enter a fine amount, and click Add Record.
- Update a Record: Select a row from the database table to auto-populate the form, modify the desired fields, and click Update Selected.
- Delete a Record: Click a row in the table, press Delete Selected, and confirm the deletion dialog prompt.
- Search Records: Navigate to the Search tab and type any name, license ID, or plate number into the search bar for live table filtering.

🏗️ OOP Implementation

- Encapsulation: Input validation rules, timestamp calculations, and SQL queries are encapsulated within dedicated service and repository classes.
- Inheritance: Views (VehicleView and SearchVehicleView) inherit directly from PyQt6's QWidget to utilize window layout and signal capabilities.
- Abstraction: VehicleService abstracts raw SQL database interactions from the GUI, ensuring view components handle high-level dataclass objects rather than SQL queries.
- Polymorphism: Qt event loops, widget paint calls, and signal-slot connections are overridden contextually across different view components.

🗄️ Database Design
The system interacts with a local SQLite database (vehicle_violations.db) comprising two linked tables:

Schema Overview
drivers Table

- licensenum (TEXT, PRIMARY KEY) — Unique driver license or auto-generated ID
- drivername (TEXT) — Full driver name
- has_license (BOOLEAN) — License validity flag
- phone (TEXT) — Driver contact phone number
- email (TEXT) — Driver email address
- sex (TEXT) — Driver gender selection

violations Table
- platenum (TEXT, PRIMARY KEY) — Vehicle plate number
- licensenum (TEXT, FOREIGN KEY) — References drivers(licensenum)
- vehicletype (TEXT) — Vehicle type classification
- violations (TEXT) — Comma-separated violation charges
- fine (REAL) — Monetary fine amount
- date_created (TEXT) — Auto-generated timestamp (YYYY-MM-DD HH:MM:SS)

Main Application

Shows the dual-column input layout (Driver Identification & Citation Details), multi-select check list, and the primary 11-column table.

<img width="1177" height="742" alt="Image" src="https://github.com/user-attachments/assets/6d9d7d18-690b-4bd6-a992-bc8938762f1b" />

Search View Tab

Demonstrates dynamic record filtering as the user types queries in the search bar.

<img width="1176" height="742" alt="Image" src="https://github.com/user-attachments/assets/fce1e016-f118-45ef-9cd7-600133bcd0a4" />

🧪 Testing & Verification

| Test Case | Input/Action | Expected Result | Result |
|--------|--------|--------|--------|
| Add Record | Complete form details & click "Add Record" | Record saved; success message displayed; creation date timestamped. | Passed|
| Missing Driver Name | Leave name field empty and click "Add Record" | Blocked by UI validation alert: "Driver Name cannot be empty." | Passed |
| Invalid Fine Format | Input string "five hundred" into Fine Amount | Blocked by alert: "Fine amount must be a valid number." | Passed |
| Duplicate Plate | Submit a plate number that already exists | Blocked by SQLite constraint dialog alerting primary key conflict. | Passed |
| Update Record | Select row, change fine to 200.00, click "Update" | Record modified in SQLite DB and refreshed in table view. | Passed |
| Delete Record | Select row, click "Delete Selected" & confirm | Citation deleted from table and violations database table. | Passed |
| Dynamic Search | Type plate segment into Search field | Results instantly filtered down to matching rows in real time. | Passed |


⚠️ Known Limitations

- Registered Vehicle not fully implementing
- Violation Fine Filter not fully implementing

👤 Author

Name: Kobe Jacob M. Salaver

Section: CS26L(3581)
