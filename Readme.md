# Credit Card Apply Backend API Documentation
This document provides detailed instructions for setting up and using the Cred Backend API. The API allows users and employees to apply for credit cards, manage applications, and perform role-based operations.

## Table of Contents
- Project Setup

      1. Prerequisites
      2. Installation
      3. Environment Variables
      4. Database Setup
      5. Running the Server

- API Endpoints

      1. Authentication
      2. User Management
      3. Credit Card Management

- Examples

      1. User Registration
      2. Credit Card Application

- Error Handling

- Testing

## Project Setup
**Prerequisites**

    Python 3.8 or higher
    pip (Python package manager)
    SQLite (or any other database supported by Django)
    Git (optional)

## Installation
**Clone the repository:**

```bash
git clone https://github.com/your-repo/cred-backend.git
cd cred-backend
```
**Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
**Install dependencies:**

```bash
pip install -r requirements.txt
```

## Environment Variables
**Create a .env file in the root directory and add the following variables:**

```env
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```
## Database Setup

**Run migrations:**

```bash
python manage.py migrate
```

**Create a superuser (Admin):**

```bash
python manage.py createsuperuser
```

## Running the Server
**Start the development server:**

bash
Copy
python manage.py runserver
The API will be available at http://127.0.0.1:8000/.

API Endpoints
Authentication
All endpoints (except registration and login) require JWT authentication. Include the token in the Authorization header:

http
Copy
Authorization: Bearer <access_token>
User Management
1. Register a New User
URL: /api/register/

Method: POST

Request Body:

json
Copy
{
  "email": "user@example.com",
  "password": "securepassword123"
}
Response:

json
Copy
{
  "id": 1,
  "email": "user@example.com"
}
2. Login (Obtain JWT Tokens)
URL: /api/login/

Method: POST

Request Body:

json
Copy
{
  "email": "user@example.com",
  "password": "securepassword123"
}
Response:

json
Copy
{
  "access": "access_token",
  "refresh": "refresh_token"
}
3. Refresh JWT Token
URL: /api/token/refresh/

Method: POST

Request Body:

json
Copy
{
  "refresh": "refresh_token"
}
Response:

json
Copy
{
  "access": "new_access_token"
}
Credit Card Management
1. Submit a Credit Card Application
URL: /api/cards/

Method: POST

Request Body:

json
Copy
{
  "card_type": "VISA",
  "credit_limit": 5000
}
Response:

json
Copy
{
  "id": 1,
  "card_number": "4000001234567890",
  "card_type": "VISA",
  "credit_limit": 5000,
  "status": "PENDING"
}
2. Retrieve Credit Card Details
URL: /api/cards/<int:pk>/

Method: GET

Response:

json
Copy
{
  "id": 1,
  "card_number": "4000001234567890",
  "card_type": "VISA",
  "credit_limit": 5000,
  "status": "APPROVED",
  "user_email": "user@example.com",
  "approved_by_email": "admin@example.com"
}
3. Update Credit Card Status (Admin/Manager Only)
URL: /api/cards/<int:pk>/update-status/

Method: POST

Request Body:

json
Copy
{
  "status": "APPROVED"
}
Response:

json
Copy
{
  "message": "Card successfully approved",
  "data": {
    "id": 1,
    "card_number": "4000001234567890",
    "card_type": "VISA",
    "credit_limit": 5000,
    "status": "APPROVED"
  }
}
Examples
User Registration
bash
Copy
curl -X POST http://127.0.0.1:8000/api/register/ \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "password": "securepassword123"
}'
Credit Card Application
bash
Copy
curl -X POST http://127.0.0.1:8000/api/cards/ \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{
  "card_type": "VISA",
  "credit_limit": 5000
}'
Error Handling
400 Bad Request: Invalid input data.

401 Unauthorized: Missing or invalid JWT token.

403 Forbidden: Insufficient permissions.

404 Not Found: Resource not found.

Example Error Response:

json
Copy
{
  "error": "Invalid OTP."
}