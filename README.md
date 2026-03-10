# Solar_inventory_System

![Python](https://img.shields.io/badge/-Python-blue?logo=python&logoColor=white)

## 📝 Description

Solar_inventory_System is a robust Python-based application designed to streamline stock management and financial workflows for renewable energy businesses. This comprehensive tool simplifies the tracking of solar hardware while offering a powerful automated billing and invoice generation module. By digitizing inventory control, it reduces manual errors and ensures that essential components like photovoltaic panels and inverters are always accounted for, providing an efficient end-to-end solution for modern solar enterprises.

## 🛠️ Tech Stack

- 🐍 Python


## 📦 Key Dependencies

```
flask: latest
flask-login: latest
mysql-connector-python: latest
werkzeug: latest
```

## 📁 Project Structure

```
.
├── app.py
├── config.py
├── db.py
├── invoices
│   └── 2026
│       ├── SOL-20260124053601.pdf
│       ├── SOL-20260124053615.pdf
│       └── SOL-20260124053738.pdf
├── models.py
├── requirements.txt
├── routes
│   ├── auth.py
│   ├── dashboard.py
│   ├── inventory.py
│   ├── invoices.py
│   ├── sales.py
│   ├── settings.py
│   └── users.py
├── static
│   └── style.css
├── templates
│   ├── base.html
│   ├── dashboard.html
│   ├── inventory.html
│   ├── invoices.html
│   ├── login.html
│   ├── sales.html
│   ├── settings.html
│   └── users.html
└── utils
    └── invoice_generator.py
```

## 🛠️ Development Setup

### Python Setup
1. Install Python (v3.8+ recommended)
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`


## 👥 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/Mr-Joseph-Jo/Solar_inventory_System.git`
3. **Create** a new branch: `git checkout -b feature/your-feature`
4. **Commit** your changes: `git commit -am 'Add some feature'`
5. **Push** to your branch: `git push origin feature/your-feature`
6. **Open** a pull request

Please ensure your code follows the project's style guidelines and includes tests where applicable.

---
*This README was generated with ❤️ by ReadmeBuddy*
