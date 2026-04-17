# ☀️ Solar Inventory System

A full-featured **Flask-based inventory and billing system** designed for solar businesses.
It supports inventory management, sales tracking, GST invoicing, user roles, and audit logging — all packaged with Docker for easy deployment.

---

## 🚀 Features

### 🔐 Authentication & Roles

* Secure login/logout system
* Role-based access:

  * **Owner** – full access
  * **Admin** – inventory + settings
  * **Sales** – create sales & view invoices

### 📦 Inventory Management

* Add, edit, delete items
* Track stock levels
* Low-stock alerts
* GST rate per item

### 💰 Sales & Billing

* Create multi-item sales
* Automatic GST calculation
* Discount (round-off) support
* Generates **professional PDF invoices**

### 🧾 Invoice System

* Download invoices anytime
* Organized storage (year-wise)
* GST-compliant format

### ⚙️ Settings

* Company profile (GSTIN, address, bank details)
* Dynamic GST rate management

### 👥 User Management

* Create users (admin/sales)
* Enable/disable accounts
* Password hashing

### 📊 Dashboard

* Total sales & revenue
* Inventory insights
* Recent transactions

### 🕵️ Audit Logs

* Tracks:

  * Logins/logouts
  * Inventory changes
  * Sales
  * User actions

### 🐳 Docker Support

* One-command deployment with:

  * Flask app (Gunicorn)
  * MySQL database

---

## 🏗️ Tech Stack

* **Backend:** Flask, Flask-Login, Flask-WTF
* **Database:** MySQL (with connection pooling)
* **PDF Generation:** ReportLab
* **Frontend:** Jinja2 + CSS
* **Testing:** Pytest
* **Deployment:** Docker + Docker Compose

---

## 📁 Project Structure

```
solar_inventory_system/
├── app.py               # Main Flask app
├── config.py            # Environment config
├── db.py                # DB connection pooling
├── models.py            # User model
├── routes/              # Application routes
├── templates/           # HTML templates
├── static/              # CSS
├── utils/               # Helpers (audit, invoice)
├── tests/               # Unit tests
├── Dockerfile
├── docker-compose.yml
└── setup.sql            # Database schema
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd solar_inventory_system
```

---

### 2. Configure Environment

Copy `.env.example`:

```bash
cp .env.example .env
```

Edit `.env`:

```
SECRET_KEY=your-secret-key
DB_HOST=db
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=solar_inventory
```

---

### 3. Run with Docker (Recommended)

```bash
docker-compose up --build
```

App will be available at:

👉 [http://localhost:5000](http://localhost:5000)

---

### 4. Initialize Database

Run inside MySQL container:

```bash
docker exec -it <db_container> mysql -u root -p
```

Then:

```sql
SOURCE /docker-entrypoint-initdb.d/setup.sql;
SOURCE /docker-entrypoint-initdb.d/seed_company.sql;
```

---

## 🔑 Default Login

```
Username: owner
Password: changeme123
```

⚠️ **Important:** Change this immediately after first login.

---

## 🧪 Running Tests

```bash
pytest
```

* Uses **mocked DB (SQLite-style)**
* No real database required

---

## 📦 API / Routes Overview

| Route        | Description            |
| ------------ | ---------------------- |
| `/`          | Login                  |
| `/dashboard` | Dashboard              |
| `/inventory` | Manage inventory       |
| `/sales`     | Create sale            |
| `/invoices`  | View/download invoices |
| `/settings`  | Company & GST settings |
| `/users`     | User management        |
| `/audit`     | Audit logs             |

---

## 🛡️ Security Features

* CSRF protection (Flask-WTF)
* Password hashing (Werkzeug)
* Role-based access control
* SQL injection protection (parameterized queries)
* DB connection pooling

---

## 📄 Invoice Features

* GST breakdown (IGST / CGST / SGST)
* Amount in words
* Bank details
* Vehicle & dispatch info
* Clean printable format

---

## 🔧 Customization Ideas

* Add **reports (monthly sales, GST reports)**
* Add **barcode/QR support**
* Integrate **payment gateways**
* Multi-branch support
* Export to Excel

---

## 📌 Health Check

```
GET /health
```

Returns:

```json
{ "status": "ok" }
```

---

## 🧠 Design Highlights

* Modular **Blueprint architecture**
* Clean separation:

  * Routes
  * DB
  * Utilities
* Production-ready:

  * Gunicorn
  * Dockerized
  * Connection pooling

---

## 📜 License

MIT License (or your preferred license)

---

## 🙌 Acknowledgements

Built for real-world solar business workflows with GST compliance in mind.
