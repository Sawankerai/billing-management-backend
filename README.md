Billing Management Backend

A powerful and scalable Billing Management Backend API built using Django & Django REST Framework.
This system helps manage customers, vendors, invoices, payments, products, and reports efficiently.

🚀 Features
👤 Customer Management
🏢 Vendor Management
📦 Product Management
🧾 Invoice Generation
💳 Payment Tracking
📊 Sales & Purchase Reports
🔐 JWT Authentication
🌐 RESTful APIs
🛡️ Secure & Scalable Architecture

Tech Stack

Backend Framework: Django
API Framework: Django REST Framework
Database: SQLite (default) / PostgreSQL (recommended for production)
Authentication: JWT (SimpleJWT)
CORS Handling: django-cors-headers

📁 Project Structure

billing-management-backend/
│
├── core/                # Main Django project
├── customers/           # Customer management app
├── vendors/             # Vendor management app
├── products/            # Product management app
├── invoices/            # Invoice management app
├── payments/            # Payment management app
├── manage.py
└── requirements.txt

⚙️ Installation Guide
1️⃣ Clone the Repository

git clone https://github.com/your-username/billing-management-backend.git
cd billing-management-backend

Activate virtual environment:

Windows

venv\Scripts\activate

Mac/Linux

source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Apply Migrations
python manage.py makemigrations
python manage.py migrate
5️⃣ Create Superuser
python manage.py createsuperuser
6️⃣ Run Server
python manage.py runserver

Server will start at:

http://127.0.0.1:8000/
🔑 Authentication

This project uses JWT Authentication.

Get Token
POST /api/token/
Refresh Token
POST /api/token/refresh/

Include token in headers:

Authorization: Bearer <your_access_token>
📡 Example API Endpoints
Method	Endpoint	Description
GET	/api/customers/	Get all customers
POST	/api/customers/	Create new customer
GET	/api/vendors/	Get all vendors
POST	/api/invoices/	Create invoice
GET	/api/products/	List products

📊 Core Modules Explained
🧍 Customer Management

Store customer details, contact info, and billing history.

🏭 Vendor Management

Manage supplier information and purchase records.

🧾 Invoice Management

Generate invoices automatically with product and tax calculation.

💰 Payment Tracking

---

## 📷 API Screenshots

### Login API (JWT Token)

![Login API](screenshots/login_api.png)

### Create Product API

![Product API](screenshots/product_api.png)

### Create Invoice API

![Invoice API](screenshots/invoice_api.png)

Track paid, unpaid, and partially paid invoices.
