<div align="center">

<img src="https://images.unsplash.com/photo-1544383835-bda2bc66a55d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80" width="500" alt="Database Architecture" style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);">

# 🛡️ Integrated Database Management & Analytics Engine
**Architecting Relational Integrity and High-Performance Data Logic**

[![Language](https://img.shields.io/badge/Language-Python%203.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/System-SQL-orange?style=flat-square&logo=postgresql&logoColor=white)]()
[![Backend](https://img.shields.io/badge/Framework-Flask--Logic-red?style=flat-square&logo=flask&logoColor=white)]()
[![Normalization](https://img.shields.io/badge/Design-3NF--Compliant-brightgreen?style=flat-square)]()

---

### 🗺️ Project Navigation

[![Vision](https://img.shields.io/badge/-Project%20Vision-005571?style=for-the-badge&logo=target&logoColor=white)](#-project-vision)
[![Architecture](https://img.shields.io/badge/-Technical%20Design-4B0082?style=for-the-badge&logo=diagram.net&logoColor=white)](#-technical-design--normalization)
[![Logic](https://img.shields.io/badge/-Business%20Logic-D2691E?style=for-the-badge&logo=python&logoColor=white)](#-business-logic--backend-integration)
[![Benchmarks](https://img.shields.io/badge/-Benchmarks-B22222?style=for-the-badge&logo=speedtest&logoColor=white)](#-performance--reliability)
[![Setup](https://img.shields.io/badge/-Deployment-006400?style=for-the-badge&logo=terminal&logoColor=white)](#-deployment--setup)

---

</div>

## 🌐 Project Vision
In modern software engineering, data is the most valuable asset. This project serves as a comprehensive **Database Management System (DBMS)** designed to handle complex relational data with zero redundancy. It demonstrates the bridge between raw SQL schemas and dynamic application layers, ensuring that every byte of data is stored securely and retrieved efficiently.

## 🏗️ Technical Design & Normalization
The core engine is built on rigorous mathematical foundations of relational algebra:

* **Normalization Mastery:** The schema is optimized up to **3rd Normal Form (3NF)** to eliminate transitive dependencies and update anomalies.
* **Integrity Constraints:**
    * **Referential Integrity:** Strictly enforced foreign keys to ensure consistent data relationships.
    * **Entity Integrity:** Unique primary key indexing for $O(1)$ search complexity.
* **ACID Compliance:** Designed to support **Atomicity, Consistency, Isolation, and Durability**, ensuring the database remains stable even during unexpected failures.



---

## 🐍 Business Logic & Backend Integration
The application, powered by the `app.py` engine, translates business requirements into optimized SQL queries:

* **Security-First Approach:** Implementation of **Parameterized Queries** to provide absolute protection against **SQL Injection** attacks.
* **Complex Data Retrieval:** Leveraging advanced **JOIN** operations (Inner, Left, and Self-Joins) to aggregate multi-dimensional data into actionable insights.
* **Dynamic CRUD Interface:** A modular backend structure that allows for scalable Create, Read, Update, and Delete operations without direct database exposure.



---

## 📂 System Architecture
The repository follows a clean-code directory structure to ensure modularity:

```bash
DATABASE_PROJECT/
│
├── 📁 Database Project/      # Core Application Layer
│   ├── app.py                # Central Business Logic (Flask Engine)
│   ├── utils/                # Database connection handlers
│   └── templates/            # Frontend View components
│
├── 📁 SQL_Logic/             # Data Layer
│   ├── build_schema.sql      # DDL Scripts (Tables, Constraints)
│   └── seed_data.sql         # DML Scripts (Initial Data)
│
└── README.md                 # Technical Documentation

```

<div align="center">

## 📈 Performance & Reliability
Continuous testing for high-load scenarios

| Feature | Implementation | Performance |
| :--- | :--- | :---: |
| **Data Retrieval** | B-Tree Indexing | ⚡ High |
| **Consistency** | Transaction Management | 🛡️ Stable |
| **Logic Layer** | Python 3.9+ Backend | 🚀 Scalable |
| **Security** | Parameterized Input | 🔒 Secure |

</div>

## 🚀 Deployment & Setup

### 1. Database Initialization

Deploy the physical schema to your SQL server instance:

```bash

-- Execute via your SQL CLI or IDE
SOURCE SQL_Logic/build_schema.sql;

```

### 2. Backend Configuration

Install the required dependencies and initialize the application logic:

```bash
# Navigate to the core directory
cd "Database Project"

# Install libraries
pip install flask mysql-connector-python pandas

# Launch the system
python app.py
```
<div align="center">

👤 Author & Database Architect

Berat Erol Çelik Software Engineering Student | Data Engineering Enthusiast

Developed with a passion for clean data and efficient architecture. If you find this helpful, please give it a ⭐!

</div>










