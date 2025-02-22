# Cred Backend API Documentation

This document provides detailed instructions for setting up and using the Cred Backend API. The API allows users and employees to apply for credit cards, manage applications, and perform role-based operations.

## Table of Contents
- [Project Setup](#project-setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Database Setup](#database-setup)
  - [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [User Management](#user-management)
  - [Credit Card Management](#credit-card-management)
- [Examples](#examples)
  - [User Registration](#user-registration)
  - [Credit Card Application](#credit-card-application)
- [Error Handling](#error-handling)
- [Support](#support)

---

## Project Setup

### Prerequisites
- Python 3.8 or higher  
- pip (Python package manager)  
- SQLite (or any other database supported by Django)  
- Git (optional)  

### Installation

#### Clone the repository:
```bash
  git clone https://github.com/ArifRexa/Cred-Backend-API.git
  cd Cred-Backend-API
```

#### Create a virtual environment:
```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install dependencies:
```bash
  pip install -r requirements.txt
```

---
## Project Structure
```markdown
cred-backend/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── users/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── models.py
│   ├── managers.py
│   ├── serializers.py
│   ├── tests.py
│   ├── tokens.py
│   ├── utils.py
│   ├── urls.py
│   └── views.py
├── cards/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

## Environment Variables

Create a `.env` file in the root directory and add the following variables:
```env
STATIC_URL=static
MEDIA_URL=media
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=checkmed202@gmail.com
EMAIL_HOST_PASSWORD=yfunbtwyemoguovk
default_from_email=checkmed202@gmail.com
```

---

## Database Setup

#### Run migrations:
```bash
  python manage.py migrate
```

#### Create a superuser (Admin):
```bash
  python manage.py createsuperuser
```

---

## Running the Server

#### Start the development server:
```bash
  python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`. and the admin panel at `http://127.0.0.1:8000/admin/`.

---

## API Endpoints

### Authentication

| Endpoint                                        | Method | Description                       | Access        | Required Parameters            | Optional Parameters       | Response Example                                           |
|-------------------------------------------------|--------|-----------------------------------|---------------|--------------------------------|---------------------------|------------------------------------------------------------|
| `/api/register/`                                | `POST` | Register a new user               | Public        | `email`, `password`            | `first_name`, `last_name` | `{ "id": 1, "email": "user@example.com" }`                 |
| `/api/login/`                                   | `POST` | Login and get JWT tokens          | Public        | `email`, `password`            | -                         | `{ "access": "access_token", "refresh": "refresh_token" }` |
| `/api/token/refresh/`                           | `POST` | Refresh JWT tokens                | Authenticated | `refresh`                      | -                         | `{ "access": "new_access_token" }`                         |
| `/api/verify-otp/`                              | `POST` | Verify OTP for email verification | Public        | `email`, `otp`                 | -                         | `{ "message": "OTP verified successfully" }`               |
| `/api/resend-otp/`                              | `POST` | Resend OTP for email verification | Public        | `email`                        | -                         | `{ "message": "OTP resent successfully" }`                 |
| `/api/password-reset/`                          | `POST` | Request password reset            | Public        | `email`                        | -                         | `{ "message": "Password reset email sent" }`               |
| `/api/password-reset-confirm/<uidb64>/<token>/` | `POST` | Confirm password reset            | Public        | `password`, `password_confirm` | -                         | `{ "message": "Password reset successful" }`               |

---

### User Management

| Endpoint                                | Method  | Description                   | Access        | Required Parameters | Optional Parameters                          | Response Example                                    |
|-----------------------------------------|---------|-------------------------------|---------------|---------------------|----------------------------------------------|-----------------------------------------------------|
| `/api/user-info/`                       | `GET`   | Get current user info         | Authenticated | -                   | -                                            | `{ "id": 1, "email": "user@example.com" }`          |
| `/api/user/update/`                     | `PATCH` | Update user profile           | Authenticated | -                   | `first_name`, `last_name`, `profile_picture` | `{ "message": "Profile updated successfully" }`     |
| `/api/users/`                           | `GET`   | List all users                | Admin/Manager | -                   | -                                            | `[ { "id": 1, "email": "user@example.com" }, ... ]` |
| `/api/users/<int:pk>/`                  | `GET`   | Get user details              | Admin/Manager | -                   | -                                            | `{ "id": 1, "email": "user@example.com" }`          |
| `/api/users/<int:user_id>/update-role/` | `PATCH` | Update user role (Admin only) | Admin Only    | `role`              | -                                            | `{ "message": "User role updated successfully" }`   |

---

### Credit Card Management

| Endpoint                     | Method   | Description                                    | Access                              | Required Parameters         | Optional Parameters              | Response Example                                                                                                 |
|------------------------------|----------|------------------------------------------------|-------------------------------------|-----------------------------|----------------------------------|------------------------------------------------------------------------------------------------------------------|
| `/cards/`                    | `GET`    | List all credit cards                          | Authenticated (Owner/Admin/Manager) | -                           | -                                | `[ { "id": 1, "card_type": "VISA", "credit_limit": 5000, "status": "PENDING" }, ... ]`                           |
| `/cards/`                    | `POST`   | Apply for a new credit card                    | Authenticated (Owner)               | `card_type`, `credit_limit` | -                                | `{ "id": 1, "card_number": "4000001234567890", "card_type": "VISA", "credit_limit": 5000, "status": "PENDING" }` |
| `/cards/{id}/`               | `GET`    | Get details of a specific credit card          | Authenticated (Owner/Admin/Manager) | -                           | -                                | `{ "id": 1, "card_type": "VISA", "credit_limit": 5000, "status": "APPROVED" }`                                   |
| `/cards/{id}/`               | `DELETE` | Delete a credit card (Admin only)              | Admin Only                          | -                           | -                                | `{ "message": "Card deleted successfully" }`                                                                     |
| `/cards/{id}/update-status/` | `POST`   | Update credit card status (Admin/Manager only) | Admin/Manager Only                  | `status`                    | `rejection_reason` (if rejected) | `{ "message": "Card successfully approved", "data": { "id": 1, "status": "APPROVED" } }`                         |
| `/cards/{id}/update-limit/`  | `PATCH`  | Partially update for credit card limit         | Admin/Manager Only                  | -                           | Any field(s) that need updating  | `{ "message": "Card updated successfully" }`                                                                     |

### Key Highlights:
- **Access Levels**:
  - `Public`: Anyone can access.
  - `Authenticated`: Logged-in users.
  - `Owner`: Users can access their own resources.
  - `Admin/Manager Only`: Restricted to admins and managers.

- **Required vs Optional Parameters**:
  - Mandatory fields are listed under **Required Parameters**.
  - Additional fields that can be included are under **Optional Parameters**.

- **Response Examples**:
  - Each endpoint has an example response for better clarity.


---
## Examples

### User Registration
```bash
  curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Credit Card Application
```bash
  curl -X POST http://127.0.0.1:8000/api/cards/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "card_type": "VISA",
    "credit_limit": 5000
  }'
```

---

## Error Handling

- `400 Bad Request`: Invalid input data.
- `401 Unauthorized`: Missing or invalid JWT token.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Resource not found.

**Example Error Response:**
```json
{
  "error": "Invalid OTP."
}
```

---

## Support

| Email                         | Password      | Roll       |
|-------------------------------|---------------|------------|
| `checkmed202@gmail.com`       | `check101020` | User       |
| `dev.arifrexa@gmail.com`      | `arif101020`  | User       |
| `dawod.ibrahim2218@gmail.com` | `arif101020`  | User       |
| `arif.reza3126@gmail.com`     | `arif101020`  | Employee   |
| `mailarif3126@gmail.com`      | `arif101020`  | Manager    |
| `admin@gmail.com`             | `1234`        | Admin only |

For any issues or questions, please contact `arif.reza3126@gmail.com` or ```+8801677243126```.
