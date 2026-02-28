# Identity Reconciliation API

## Overview

This project implements an Identity Reconciliation service as part of the BiteSpeed Backend Task.

The service links multiple contact records that belong to the same customer based on shared email addresses or phone numbers. It ensures that all related contacts are consolidated under a single primary identity.

---

## Problem Statement

Customers may place orders using different email addresses and phone numbers.
If any contact information overlaps, those records must be linked together and treated as a single identity.

Rules implemented:

* If no existing contact matches → create a new primary contact.
* If email or phone matches → link to existing identity.
* If new information is introduced → create a secondary contact.
* If two primary contacts become connected → merge them.
* The oldest contact always remains the primary.

---

## Tech Stack

* Python
* Django
* MySQL
* Django ORM

---

## Project Structure

```
bitespeed/
│
├── bitespeed/        # Django project settings
├── contacts/         # Identity reconciliation logic
├── manage.py
└── requirements.txt
```

---

## Database Schema

Model: `Contact`

| Field          | Type     | Description                |
| -------------- | -------- | -------------------------- |
| id             | Integer  | Primary key                |
| email          | String   | Customer email             |
| phoneNumber    | String   | Customer phone             |
| linkedId       | Integer  | References primary contact |
| linkPrecedence | String   | "primary" or "secondary"   |
| createdAt      | DateTime | Record creation time       |
| updatedAt      | DateTime | Last updated time          |
| deletedAt      | DateTime | Soft delete (nullable)     |

---

## API Endpoint

### POST `/identify`

### Request Body (JSON)

```
{
  "email": "string (optional)",
  "phoneNumber": "string (optional)"
}
```

At least one field (email or phoneNumber) must be provided.

---

## Response Format

```
{
  "contact": {
    "primaryContactId": number,
    "emails": string[],
    "phoneNumbers": string[],
    "secondaryContactIds": number[]
  }
}
```

### Response Rules

* `primaryContactId` → ID of the oldest linked contact
* `emails` → All unique emails linked to this identity (primary email first)
* `phoneNumbers` → All unique phone numbers linked (primary phone first)
* `secondaryContactIds` → IDs of all secondary contacts

---

## How to Run Locally

### 1. Clone the repository

```
git clone <your-repository-url>
cd <project-folder>
```

### 2. Create virtual environment

```
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Configure Database

Update `settings.py` with your MySQL credentials:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bitespeed_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 5. Run Migrations

```
python manage.py migrate
```

### 6. Start Server

```
python manage.py runserver
```

API will be available at:

```
http://127.0.0.1:8000/identify
```

---

## Deployment

The application is deployed at:

```
<your-hosted-endpoint-url>
```

Example:

```
https://your-app-name.onrender.com/identify
```

---

## Test Scenarios Covered

* New primary contact creation
* Linking secondary contacts
* Merging two primary contacts
* Consolidated response generation
* Order preservation for primary email and phone

---

## Author

Vishwas B
B.Tech Computer Science

---


