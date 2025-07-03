
# 🩺 Diabetes/Hypertension Tracker App

## 📘 Project Overview

A full-stack mobile health-tracking application designed to assist patients managing **diabetes** and/or **hypertension**. The app enables users to log their health metrics, monitor trends, and receive smart AI-driven lifestyle recommendations.

🛠 Built With:
- **Flutter** – clean, cross-platform frontend UI
- **Django + Django REST Framework** – secure backend API with scalable architecture
- **AI/ML (coming soon)** – personalized health recommendations based on user data

---

## 🎯 Purpose

Millions of individuals living with chronic conditions like diabetes and hypertension often lack reliable tools to track and manage their health. This app empowers users to:

✅ Log **blood pressure** and **blood sugar** readings  
📈 Visualize trends using graphs and dashboards  
🤖 Get **AI-powered recommendations**  
🔐 Maintain secure access to their health logs  
📲 Enjoy a seamless, mobile-first experience  

---

## 👥 Team Roles

### 👨‍💻 Muhammad Abdullah – Lead Developer
- Designed and implemented the **Django backend**
- Building the **Flutter frontend**
- Created user model, health reading model, and REST API endpoints
- Handling authentication, registration, and user serialization

### 🤖 Ahmed – AI/ML Lead
- Designing ML models for:
  - Health pattern recognition
  - Personalized recommendations
- Working on integration plans for backend deployment

### 🧠 Waffa – Medical/Bio Research Lead
- Researching evidence-based guidelines on:
  - Diabetes & hypertension management
  - Diet, exercise, and medication protocols
- Writing content logic for recommendation system
- Defining clinical thresholds for vital signs

---

## ✅ Features Completed

### ✅ User Authentication
- Custom user model
- Registration with password validation
- Full validation for age, weight, height, and more
- Unique email with proper formatting checks

### ✅ Readings Model & API
- Systolic and diastolic blood pressure readings
- Glucose level readings (mg/dL and mmol/L supported)
- Notes field for user logs
- Automatic categorization of BP level (e.g., Normal, Stage 1 Hypertension)
- Conversion between glucose units
- Automatic timestamps for `created_at` and `updated_at`

### ✅ User & Reading APIs (DRF)
- `UserViewSet` (GET, PATCH, DELETE current user)
- `ReadingViewSet` (create, list, update, delete readings)
- `recent_readings` (past 7 days)
- `abnormal_readings` (based on clinical thresholds)

### ✅ Registration API
- Rate-limited (max 10 per hour)
- Email + password validation
- Returns user details upon successful registration

---

## 🚧 In Progress / Next Features

- 🔐 Token-based authentication (or JWT)
- 📬 Password reset via email
- 📈 Graphs in Flutter frontend
- 🤖 AI/ML logic integration
- 📑 Recommendation content upload (Waffa)
- 🔄 Flutter-Django integration
- 🧪 Testing + Postman collection

---

## 📁 Folder Structure

```
app_name/
├── backend/
│   ├── health_backend/        # Main Django project settings/urls
│   ├── tracker/               # Django app: models, views, serializers, etc.
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers/
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── ...
│   ├── db.sqlite3
│   └── manage.py
├── frontend/                  # (To be implemented using Flutter)
└── README.md
```

---

## 💡 Next Steps

- 🔧 Finalize token-based authentication setup
- 📈 Create visual graphs for readings (Flutter)
- 🤖 Build first version of the recommendation engine
- 🔗 Integrate Flutter frontend with Django REST API
- 📥 Add support for password reset via email
- 🧪 Test all endpoints and user flows

---
