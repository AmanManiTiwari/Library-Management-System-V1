<div align="center">

# 📚 Library Management System

**A full-stack Flask web application for managing library sections, books, issues, and member requests — with a built-in REST API and analytics dashboard.**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-07405E?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Status](https://img.shields.io/badge/Status-Academic%20Project-blue)](#)

[Overview](#-overview) •
[Features](#-features) •
[Tech Stack](#-tech-stack) •
[Getting Started](#-getting-started) •
[Usage](#-usage) •
[API Reference](#-api-reference) •
[Project Structure](#-project-structure)

</div>

---

## 📖 Overview

**Library Management System** is a role-based web application built with **Flask** and **SQLAlchemy** that digitizes the day-to-day operations of a library. It supports two types of users — **Librarians** (admins) and **Members** — each with a dedicated dashboard.

Librarians can organize the catalog into sections, manage books, review borrowing requests, track issued/returned copies, and view real-time usage statistics. Members can browse and search the catalog, request books, track their issued books, download book content as PDF, and leave feedback.

A companion project report (`Library Management System Report.pdf`) documenting the design and implementation is included in the repository root.

> ⚠️ **Note:** This project was built as an academic/learning exercise. It demonstrates core CRUD, session-based authentication, and REST API design patterns in Flask, but is **not hardened for production use** — see [Known Limitations](#-known-limitations--roadmap) before deploying it publicly.

---

## ✨ Features

### 👩‍💼 Librarian (Admin)
- Create, update, and delete **library sections**
- Add, update, and delete **books** within a section
- Review, **accept**, or **reject** book requests from members
- View and **revoke** currently issued books
- Auto-generated **statistics dashboard** with a live bar chart (Sections, Books, Requests, Issues) powered by Matplotlib

### 🙋 Member (User)
- Register and log in with a personal account
- Browse the catalog, **search books by section name or author**
- **Request** a book (capped at 5 active requests per user)
- View and **return** issued books
- **Download** book content as a generated PDF
- Submit **feedback** on a book

### 🔌 REST API
- Full CRUD API for **Sections** and **Books**, independent of the web UI, built with Flask-RESTful — ideal for integration or testing with tools like Postman.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, Flask |
| **REST API** | Flask-RESTful |
| **ORM / Database** | Flask-SQLAlchemy, SQLite |
| **PDF Generation** | ReportLab |
| **Charts / Analytics** | Matplotlib |
| **Frontend** | HTML5, CSS3, Jinja2 templates |
| **Auth** | Session-based, with custom `login_required` / `librarian_required` decorators |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- `pip`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AmanManiTiwari/Library-Management-System-V1.git
cd "Library-Management-System-V1/source code"

# 2. (Recommended) create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install flask flask-restful flask-sqlalchemy reportlab matplotlib
```

> 💡 **Tip:** Consider generating a `requirements.txt` for reproducible installs:
> ```bash
> pip freeze > requirements.txt
> ```

### Running the app

```bash
python app.py
```

The app starts in debug mode at **http://127.0.0.1:5000**. On first run, the SQLite database (`instance/db.sqlite3`) and its tables are created automatically, along with a default librarian account.

### Default Librarian Login

| Field | Value |
|---|---|
| Email | `admin@gmailcom` |
| Password | `0` |

> ⚠️ Change these credentials before any real-world use — see [Known Limitations](#-known-limitations--roadmap).

---

## 🧭 Usage

1. **Sign up** as a new member from the registration page, or log in as the default librarian to access the admin dashboard.
2. **As a librarian:** create a section → add books to it → manage incoming requests from the *Book Requests* page → monitor activity from the *Stats* page.
3. **As a member:** search the catalog → request a book → once approved by a librarian, view it under *Issued Books*, download it as a PDF, return it, or leave feedback.

---

## 📡 API Reference

The API layer runs alongside the web app and returns JSON.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api` | List all sections |
| `GET` | `/api/<section_id>` | Get a single section |
| `PUT` | `/api/<section_id>` | Update a section |
| `DELETE` | `/api/<section_id>` | Delete a section |
| `POST` | `/api/addSection` | Create a new section |
| `GET` | `/api/<section_id>/book` | List all books in a section |
| `POST` | `/api/<section_id>/book` | Add a book to a section |
| `GET` | `/api/book/<section_id>/<book_id>` | Get a single book |
| `PUT` | `/api/book/<section_id>/<book_id>` | Update a book |
| `DELETE` | `/api/book/<section_id>/<book_id>` | Delete a book |

**Example — create a section:**

```bash
curl -X POST http://127.0.0.1:5000/api/addSection \
  -d "name=Fiction" \
  -d "date=2026-07-16"
```

---

## 🗂 Project Structure

```
Library-Management-System-V1/
├── Library Management System Report.pdf   # Project documentation/report
└── source code/
    ├── app.py                             # Flask app: models, routes, REST API
    ├── instance/
    │   └── db.sqlite3                     # SQLite database (auto-generated)
    ├── static/
    │   ├── dashboard.css
    │   ├── login.css
    │   ├── addSection.css
    │   └── img1.png                       # Auto-generated stats chart
    └── templates/
        ├── admin.html
        ├── userDashboard.html
        ├── userLogin.html / userRegister.html
        ├── bookRequest.html
        ├── issuedBook.html
        ├── revokeBook.html
        ├── feedback.html
        ├── stats.html
        ├── book/                          # Add / update / delete book views
        └── section/                       # Add / update / delete / view section views
```

### Data Model

```
User ─┬─< Issue >─┬─ Book ─┬─< Section
      └─< Request >┘        │
Feedback ── User, Book
```

- **User** — email, password, name, `is_librarian` flag
- **Section** — a category grouping books
- **Book** — belongs to a Section
- **Request** — a member's pending request for a Book
- **Issue** — a Book currently checked out to a User
- **Feedback** — a member's comment on a Book

---

## ⚠️ Known Limitations & Roadmap

This project prioritizes core functionality over production hardening. Notable areas for improvement:

- [ ] **Password hashing** — passwords are currently stored in plain text; integrate `werkzeug.security` or `bcrypt`
- [ ] **Secret key management** — move `SECRET_KEY` and DB URI to environment variables instead of hardcoding
- [ ] **Input validation** — add stricter server-side validation and CSRF protection on forms
- [ ] **`requirements.txt`** — pin dependency versions for reproducible setup
- [ ] **Automated tests** — add unit/integration tests for routes and models
- [ ] **Pagination & filtering** — for large catalogs in the dashboard and API

Contributions addressing any of the above are very welcome.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project currently has no explicit license file. Consider adding an [MIT License](https://choosealicense.com/licenses/mit/) to clarify usage rights for contributors and users.

---

## 👤 Author

**Aman Mani Tiwari**
GitHub: [@AmanManiTiwari](https://github.com/AmanManiTiwari)

<div align="center">

If you found this project useful, consider giving it a ⭐!

</div>
