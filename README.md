# Django E-Commerce Backend API

A E-Commerce Backend built with Django REST Framework, PostgreSQL, JWT authentication, and Stripe payment processing.

## Features

✨ **Core Features:**

- Custom User model with email authentication
- JWT-based authentication with token refresh
- Email verification system
- Product catalog with categories 
- Shopping cart management
- Order processing with status tracking
- Stripe payment integration
- Automatic stock management
- Complete API documentation with Swagger

🔒 **Security:**

- JWT token blacklisting
- Role-based permissions (user, admin)
- Rate limiting on auth endpoints
- CORS configuration
- CSRF protection
- Environment-based secrets management

## Tech Stack

- **Python**: 3.11+
- **Django**: 5.x
- **Database**: PostgreSQL
- **API**: Django REST Framework
- **Authentication**: djangorestframework-simplejwt
- **Image Processing**: Pillow
- **Payments**: Stripe
- **API Docs**: drf-spectacular (Swagger/OpenAPI)
- **Testing**: pytest, pytest-django

## Project Structure

```
ecommerce_backend/
├── ecommerce_backend/          # Main Django project
│   ├── settings/
│   │   ├── base.py            # Shared settings
│   │   ├── dev.py             # Development settings
│   │   └── prod.py            # Production settings
│   ├── urls.py
│   └── wsgi.py
├── apps/                        # Django apps
│   ├── core/                   # Shared utilities, permissions, pagination
│   ├── accounts/               # User authentication
│   ├── categories/             # Product categories
│   ├── products/               # Product management
│   ├── cart/                   # Shopping cart
│   ├── orders/                 # Order management
│   └── payments/               # Stripe integration
├── tests/                       # Test suite
├── media/                       # User uploads
├── requirements.txt
├── .env.example
├── manage.py
└── README.md
```

## Installation & Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 12+ 
- pip & virtualenv

### 1. Clone and Setup Virtual Environment

```bash
cd ecommerce_backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy example file
cp .env.example .env

# Edit .env with your settings
# At minimum, update:
# - SECRET_KEY
# - Database credentials 
# - Stripe keys (get from https://dashboard.stripe.com)
```

### 4. Database Setup

**PostgreSQL**

First, create PostgreSQL database:

```bash
# macOS/Linux
createdb ecommerce_db

# Windows (via psql)
psql -U postgres
CREATE DATABASE ecommerce_db;
```

Then update `.env`:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

Run migrations:

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Server will be available at `http://localhost:8000`

## API Documentation

### Access Swagger UI

Navigate to: **http://localhost:8000/api/docs/**

### API Endpoints

#### Authentication (`/api/auth/`)

| Method | Endpoint            | Description              |
| ------ | ------------------- | ------------------------ |
| POST   | `/register/`        | Register new user        |
| POST   | `/login/`           | Login and get JWT tokens |
| POST   | `/logout/`          | Logout (blacklist token) |
| POST   | `/refresh/`         | Refresh access token     |
| GET    | `/profile/`         | Get current user profile |
| PUT    | `/profile/`         | Update user profile      |
| POST   | `/change-password/` | Change password          |
| POST   | `/verify-email/`    | Verify email with token  |

#### Categories (`/api/categories/`)

| Method | Endpoint             | Description             |
| ------ | -------------------- | ----------------------- |
| GET    | `/`                  | List all categories     |
| POST   | `/`                  | Create category (admin) |
| GET    | `/{slug}/`           | Get category details    |
| PUT    | `/{slug}/`           | Update category (admin) |
| DELETE | `/{slug}/`           | Delete category (admin) |
| GET    | `/tree/`             | Get categories as tree  |
| GET    | `/{slug}/children/`  | Get category children   |
| GET    | `/{slug}/ancestors/` | Get category ancestors  |

#### Products (`/api/products/`)

| Method | Endpoint                  | Description                  |
| ------ | ------------------------- | ---------------------------- |
| GET    | `/`                       | List products (with filters) |
| POST   | `/`                       | Create product (admin)       |
| GET    | `/{slug}/`                | Get product details          |
| PUT    | `/{slug}/`                | Update product (admin)       |
| DELETE | `/{slug}/`                | Delete product (admin)       |
| POST   | `/{slug}/upload_image/`   | Upload product image         |
| DELETE | `/{slug}/delete_image/`   | Delete product image         |
| POST   | `/{slug}/reduce_stock/`   | Reduce stock (admin)         |
| POST   | `/{slug}/increase_stock/` | Increase stock (admin)       |

**Query Parameters:**

- `?category=<id>` - Filter by category
- `?min_price=<price>` - Filter by minimum price
- `?max_price=<price>` - Filter by maximum price
- `?search=<term>` - Search products

#### Cart (`/api/cart/`)

| Method | Endpoint       | Description           |
| ------ | -------------- | --------------------- |
| GET    | `/`            | View cart             |
| POST   | `/add/`        | Add item to cart      |
| PUT    | `/items/{id}/` | Update item quantity  |
| DELETE | `/items/{id}/` | Remove item from cart |
| DELETE | `/clear/`      | Clear entire cart     |

#### Orders (`/api/orders/`)

| Method | Endpoint                | Description            |
| ------ | ----------------------- | ---------------------- |
| GET    | `/`                     | List user's orders     |
| GET    | `/{id}/`                | Get order details      |
| POST   | `/checkout/`            | Create order from cart |
| POST   | `/{id}/update-status/`  | Update status (admin)  |
| POST   | `/{id}/cancel/`         | Cancel order           |
| GET    | `/{id}/status-history/` | Get status history     |

#### Payments (`/api/payments/`)

| Method | Endpoint            | Description                 |
| ------ | ------------------- | --------------------------- |
| POST   | `/create_intent/`   | Create Stripe PaymentIntent |
| POST   | `/confirm_payment/` | Confirm payment             |
| GET    | `/status/`          | Get payment status          |
| POST   | `/webhook/stripe/`  | Stripe webhook (internal)   |



**Happy building!** 🚀
