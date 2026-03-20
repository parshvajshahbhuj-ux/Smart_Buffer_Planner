# 🍽️ Smart Buffer Planner

> **Plan Smart, Waste Less** — An intelligent buffet planning platform for event organizers, caterers, and individuals across India.

---

## 📌 Overview

Smart Buffer Planner is a full-stack web application that eliminates food waste and simplifies catering management. It auto-calculates food quantities based on guest count, supports role-based workflows, generates professional PDF reports, and integrates with real hotel venues via OpenStreetMap — all without any paid API.

---

## ✨ Features

- 🧮 **Smart Quantity Calculator** — auto-computes exact food quantities per guest with a configurable safety buffer %
- 👥 **Role-Based System** — separate dashboards and tools for Organizers, Caterers, and Individuals
- 🏨 **Venue-Specific Menus** — search real hotels via OpenStreetMap; auto-creates venue with smart default menu
- 📊 **Analytics Dashboard** — category distribution, cost breakdown, monthly event trends with charts
- 📄 **PDF Report Generation** — professional downloadable buffet plans with quantities, costs, and waste risk
- ☀️ **Seasonal Suggestions** — dish recommendations based on Summer / Monsoon / Winter season
- 💰 **Caterer Tools** — per-event markup %, service charge %, itemized shopping list
- 🎯 **Individual Tools** — personal budget cap, live budget tracker, dietary preference filtering
- 🌱 **Waste Risk Indicator** — Low / Medium / High waste risk based on buffer percentage
- 🔐 **JWT Authentication** — secure login, register, and token refresh flow
- 🛠️ **Admin Panel** — manage dishes, categories, venues, and users

---

## 🖥️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2, Django REST Framework 3.14 |
| Auth | SimpleJWT |
| PDF | ReportLab |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Fonts | Playfair Display, Space Grotesk |
| Venue Search | OpenStreetMap Nominatim API (free, no key) |
| Database | SQLite (dev) |
| Static Files | WhiteNoise |
| CORS | django-cors-headers |

---

## 📁 Project Structure

```
smart_buffet_planner/
└── backend/
    ├── accounts/        # User model, roles, auth (JWT)
    ├── events/          # Event CRUD, calculations, menu items
    ├── menu/            # Dishes, categories, venues
    ├── analytics/       # Dashboard stats and charts data
    ├── reports/         # PDF report generation
    ├── config/          # Django settings, URLs, WSGI
    ├── templates/       # All HTML pages
    ├── static/          # CSS and JS
    ├── manage.py
    ├── setup.py         # One-command setup script
    └── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/smart-buffer-planner.git
cd smart-buffer-planner/smart_buffet_planner/backend
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the setup script** *(migrates DB, seeds dishes, creates users)*
```bash
python setup.py
```

**5. Start the development server**
```bash
python manage.py runserver
```

**6. Open in browser**
```
http://127.0.0.1:8000
```

---

## 🔑 Default Credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@buffet.com` | `Admin@123` |
| Demo Caterer | `demo@buffet.com` | `Demo@123` |

> Admin panel: `http://127.0.0.1:8000/admin/`

---

## 👤 User Roles

### 🧑‍💼 Event Organizer
- Store client name, email, phone
- Track confirmed RSVPs vs planned guest count
- View RSVP gap and download PDF plans for clients

### 👨‍🍳 Caterer
- Set per-event markup % and service charge %
- Auto-calculate client total and profit margin
- Generate itemized shopping lists by category

### 👤 Individual
- Set a personal budget cap per event
- Live budget tracker — warns when menu exceeds budget
- Dietary preference filtering (Vegetarian / Vegan)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/accounts/register/` | Register new user |
| POST | `/api/accounts/login/` | Login, returns JWT tokens |
| GET/POST | `/api/events/` | List / create events |
| GET | `/api/events/:id/calculations/` | Get quantity & cost calculations |
| GET/POST | `/api/menu/dishes/` | List / manage dishes |
| GET/POST | `/api/menu/venues/` | List / manage venues |
| POST | `/api/menu/venues/from_osm/` | Auto-create venue from OpenStreetMap |
| GET | `/api/analytics/dashboard/` | Dashboard stats |
| GET | `/api/reports/:id/pdf/` | Download PDF report |

---

## 🗺️ Pages

| URL | Page |
|---|---|
| `/` | Landing page |
| `/register/` | Sign up |
| `/login/` | Login |
| `/dashboard/` | Main dashboard |
| `/events/create/` | Create new event |
| `/events/:id/menu/` | Menu selection |
| `/events/:id/result/` | Buffet result & calculations |
| `/analytics/` | Analytics & charts |
| `/profile/` | User profile |
| `/admin-panel/` | Admin management panel |

---

## 📸 Screenshots

> *(Add screenshots of your landing page, dashboard, menu selection, and PDF report here)*

---

## 🌱 Future Improvements

- [ ] PostgreSQL support for production
- [ ] Email notifications for event reminders
- [ ] Multi-language support (Hindi, Tamil, etc.)
- [ ] Mobile app (React Native)
- [ ] AI-powered dish quantity learning from past events

---

## 📄 License

This project is for educational and portfolio purposes.

---

## 🙋‍♂️ Author

Built with ❤️ in Mumbai, India 🇮🇳

> *Smart Buffer Planner — Reduce Waste, Plan Smart*
