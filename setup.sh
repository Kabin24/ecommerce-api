#!/bin/bash
# Setup script for E-Commerce Backend Development

set -e

echo "🚀 E-Commerce Backend - Development Setup"
echo "=========================================="

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate || . venv/Scripts/activate
else
    echo "✓ Virtual environment already exists, activating..."
    source venv/bin/activate || . venv/Scripts/activate
fi

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file..."
    cp .env.example .env
    echo "  Please edit .env with your configuration"
else
    echo "✓ .env file already exists"
fi

# Run migrations
echo "✓ Running database migrations..."
python manage.py migrate

# Create superuser prompt
echo ""
echo "✓ Create superuser for admin access"
python manage.py createsuperuser

# Create test data (optional)
read -p "Create sample test data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✓ Creating sample test data..."
    python manage.py shell << EOF
from apps.categories.models import Category
from apps.products.models import Product

# Create sample categories
electronics = Category.objects.create(
    name='Electronics',
    slug='electronics',
    description='Electronic devices'
)

phones = Category.objects.create(
    name='Phones',
    slug='phones',
    description='Mobile phones',
    parent=electronics
)

# Create sample product
Product.objects.create(
    name='iPhone 13',
    slug='iphone-13',
    description='Latest iPhone model with advanced features',
    price=999.99,
    discount_price=799.99,
    stock_quantity=50,
    category=phones,
    sku='IPHONE13'
)

print("✓ Sample data created!")
EOF
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the development server: python manage.py runserver"
echo "2. Visit Swagger docs: http://localhost:8000/api/docs/"
echo "3. Visit admin panel: http://localhost:8000/admin/"
echo ""
echo "For production setup, see README.md"
