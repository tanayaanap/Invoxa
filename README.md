# Invoxa – Smart Invoice Management System

Invoxa is a web-based Invoice Management System developed using **Django**. It enables businesses to efficiently manage customers, products, invoices, payments, and sales reports through a clean and user-friendly interface.

## 🚀 Features

- User Authentication (Login & Logout)
- Dashboard
- Customer Management (CRUD)
- Product Management (CRUD)
- Invoice Management (CRUD)
- Automatic Invoice Number Generation
- GST & Total Calculation
- Payment Tracking
- PDF Invoice Generation
- Invoice Printing
- Sales & Payment Reports
- Search and Filter Functionality
- Responsive UI

---

## 🛠️ Tech Stack

- Python
- Django
- SQLite
- HTML5
- CSS3
- JavaScript
- Bootstrap 5

---

## 📁 Project Structure

```
Invoxa/
│
├── config/
├── core/
├── customers/
├── products/
├── invoices/
├── payments/
├── reports/
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/tanayaanap/Invoxa.git
cd Invoxa
```

### 2. Create a Virtual Environment

**Windows**

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**Command Prompt**

```bash
venv\Scripts\activate
```

**PowerShell**

```powershell
venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Open your browser and visit:

```
http://127.0.0.1:8000/
```

---
## 📦 Installing New Packages

If a new Python package is installed, update the requirements file:

```bash
pip install <package-name>
pip freeze > requirements.txt
```

Commit the updated `requirements.txt`.

---

## 📌 Useful Django Commands

Create a new app:

```bash
python manage.py startapp app_name
```

Create migrations:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

Collect static files (for deployment):

```bash
python manage.py collectstatic
```

---


## 📄 License

This project is developed for educational and internship purposes.
