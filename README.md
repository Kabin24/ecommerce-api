# Django E-Commerce Backend API

A production-grade E-Commerce Backend built with Django REST Framework, PostgreSQL, JWT authentication, and Stripe payment processing.

## Features

✨ **Core Features:**
- Custom User model with email authentication
- JWT-based authentication with token refresh
- Email verification system
- Product catalog with categories (nested support)
- Shopping cart management
- Order processing with status tracking
- Stripe payment integration (test mode)
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
- **Database**: PostgreSQL (SQLite for dev)
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
- PostgreSQL 12+ (optional, SQLite for development)
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
# - Database credentials (for PostgreSQL)
# - Stripe keys (get from https://dashboard.stripe.com)
```

### 4. Database Setup

**Option A: SQLite (Development)**
```bash
# Already configured in dev settings
python manage.py migrate
```

**Option B: PostgreSQL (Production-like)**

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

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register/` | Register new user |
| POST | `/login/` | Login and get JWT tokens |
| POST | `/logout/` | Logout (blacklist token) |
| POST | `/refresh/` | Refresh access token |
| GET | `/profile/` | Get current user profile |
| PUT | `/profile/` | Update user profile |
| POST | `/change-password/` | Change password |
| POST | `/verify-email/` | Verify email with token |

#### Categories (`/api/categories/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all categories |
| POST | `/` | Create category (admin) |
| GET | `/{slug}/` | Get category details |
| PUT | `/{slug}/` | Update category (admin) |
| DELETE | `/{slug}/` | Delete category (admin) |
| GET | `/tree/` | Get categories as tree |
| GET | `/{slug}/children/` | Get category children |
| GET | `/{slug}/ancestors/` | Get category ancestors |

#### Products (`/api/products/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List products (with filters) |
| POST | `/` | Create product (admin) |
| GET | `/{slug}/` | Get product details |
| PUT | `/{slug}/` | Update product (admin) |
| DELETE | `/{slug}/` | Delete product (admin) |
| POST | `/{slug}/upload_image/` | Upload product image |
| DELETE | `/{slug}/delete_image/` | Delete product image |
| POST | `/{slug}/reduce_stock/` | Reduce stock (admin) |
| POST | `/{slug}/increase_stock/` | Increase stock (admin) |

**Query Parameters:**
- `?category=<id>` - Filter by category
- `?min_price=<price>` - Filter by minimum price
- `?max_price=<price>` - Filter by maximum price
- `?search=<term>` - Search products

#### Cart (`/api/cart/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | View cart |
| POST | `/add/` | Add item to cart |
| PUT | `/items/{id}/` | Update item quantity |
| DELETE | `/items/{id}/` | Remove item from cart |
| DELETE | `/clear/` | Clear entire cart |

#### Orders (`/api/orders/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List user's orders |
| GET | `/{id}/` | Get order details |
| POST | `/checkout/` | Create order from cart |
| POST | `/{id}/update-status/` | Update status (admin) |
| POST | `/{id}/cancel/` | Cancel order |
| GET | `/{id}/status-history/` | Get status history |

#### Payments (`/api/payments/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/create_intent/` | Create Stripe PaymentIntent |
| POST | `/confirm_payment/` | Confirm payment |
| GET | `/status/` | Get payment status |
| POST | `/webhook/stripe/` | Stripe webhook (internal) |

## Example API Usage

### 1. Register User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

Response includes `access` and `refresh` tokens.

### 3. Get Products

```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Add to Cart

```bash
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### 5. Checkout

```bash
curl -X POST http://localhost:8000/api/orders/checkout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": "123 Main St",
    "shipping_city": "New York",
    "shipping_postal_code": "10001",
    "shipping_country": "USA",
    "shipping_cost": 10.00,
    "tax": 5.50
  }'
```

### 6. Create Payment Intent

```bash
curl -X POST http://localhost:8000/api/payments/create_intent/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1
  }'
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Module

```bash
pytest tests/test_accounts.py
pytest tests/test_products.py
pytest tests/test_cart.py
pytest tests/test_orders.py
```

### Run with Coverage

```bash
pytest --cov=apps tests/
```

### Test Files

- `tests/test_accounts.py` - User registration, login, authentication
- `tests/test_categories.py` - Category CRUD and hierarchy
- `tests/test_products.py` - Product CRUD, images, stock
- `tests/test_cart.py` - Cart operations, item management
- `tests/test_orders.py` - Checkout, order creation, status tracking
- `tests/test_payments.py` - Payment intent creation, webhook handling

## Admin Panel

Access Django admin at: **http://localhost:8000/admin**

All models are registered with useful filters, search, and inline editing.

## Environment Variables

Key variables to configure:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key
ENVIRONMENT=development

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe (get from https://dashboard.stripe.com)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Media
MEDIA_URL=/media/
MEDIA_ROOT=media/
```

## Key Design Decisions

1. **Custom User Model**: Extends AbstractUser with email as primary identifier for better UX
2. **Transaction Safety**: Checkout uses database transactions to ensure consistency
3. **Stock Snapshot**: OrderItem stores price_at_purchase to maintain accurate order history
4. **Nested Categories**: Self-referencing FK for flexible hierarchy support
5. **Modular Settings**: Separate settings for dev/prod with environment variable overrides
6. **Image Validation**: Client-side + server-side validation for security
7. **Status History**: Tracks order changes for audit trail
8. **Cart Auto-Create**: Cart created automatically on first access

## Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Update `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure PostgreSQL with strong credentials
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Configure CORS for frontend domain
- [ ] Set up email backend (Gmail, SendGrid, etc.)
- [ ] Get Stripe keys from production environment
- [ ] Run `python manage.py collectstatic`
- [ ] Use HTTPS with SSL certificate
- [ ] Set up backup for PostgreSQL
- [ ] Configure logging and monitoring
- [ ] Run tests: `pytest`
- [ ] Use production WSGI server (Gunicorn, uWSGI)

## Support & Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Stripe API Reference](https://stripe.com/docs/api)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

## License

This project is provided as-is for educational and commercial use.

---

**Happy building!** 🚀
