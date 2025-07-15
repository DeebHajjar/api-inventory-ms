# Inventory Management System API

A comprehensive Django REST API for managing inventory, products, categories, and stock transactions. This system provides full CRUD operations with advanced filtering, search capabilities, and real-time inventory tracking.

## Features

- **Product Management**: Create, update, and manage products with detailed information
- **Category Organization**: Organize products into categories for better structure
- **Inventory Tracking**: Real-time stock level monitoring with transaction history
- **Low Stock Alerts**: Automatic detection of products requiring reorder
- **Transaction History**: Complete audit trail of all inventory movements
- **Image Support**: Product image upload and management
- **Advanced Filtering**: Search and filter products by multiple criteria
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation

## Technology Stack

- **Backend**: Django 5.1.7
- **API Framework**: Django REST Framework
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Filtering**: django-filter
- **CORS**: django-cors-headers
- **Authentication**: Token-based authentication

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/DeebHajjar/api-inventory-ms.git
   cd api-inventory-ms
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   # or
   pipenv shell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or if use pipenv sell
   pipenv install -r requirements.txt
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Base URL: `http://localhost:8000/api/`

### Products
- `GET /products/` - List all products (with pagination)
- `POST /products/` - Create new product
- `GET /products/{id}/` - Get product details
- `PUT /products/{id}/` - Update product
- `DELETE /products/{id}/` - Delete product
- `GET /products/low-stock/` - Get low stock products
- `GET /products/out-of-stock/` - Get out of stock products
- `GET /products/{id}/transactions/` - Get product transaction history

### Categories
- `GET /categories/` - List all categories
- `POST /categories/` - Create new category
- `GET /categories/{id}/` - Get category details
- `PUT /categories/{id}/` - Update category
- `DELETE /categories/{id}/` - Delete category
- `GET /categories/{id}/products/` - Get products in category

### Inventory Transactions
- `GET /transactions/` - List all transactions
- `POST /transactions/` - Create new transaction
- `GET /transactions/{id}/` - Get transaction details
- `PUT /transactions/{id}/` - Update transaction
- `DELETE /transactions/{id}/` - Delete transaction
- `GET /transactions/latest/` - Get latest 10 transactions
- `GET /transactions/summary/` - Get transaction summary statistics

## Data Models

### Product
- `name`: Product name (max 200 chars)
- `description`: Product description (optional)
- `sku`: Stock Keeping Unit (unique identifier)
- `price`: Selling price
- `cost_price`: Cost price
- `current_quantity`: Current stock level
- `min_quantity`: Minimum stock threshold
- `category`: Foreign key to Category
- `image`: Product image upload
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Category
- `name`: Category name (max 100 chars)
- `description`: Category description (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### InventoryTransaction
- `product`: Foreign key to Product
- `transaction_type`: IN/OUT/ADJ (Stock In/Stock Out/Adjustment)
- `quantity`: Transaction quantity
- `reason`: Transaction reason (optional)
- `user`: User who performed transaction
- `transaction_date`: Transaction timestamp
- `note`: Additional notes (optional)
- `previous_quantity`: Stock level before transaction

## Features in Detail

### Stock Management
- Automatic stock level updates based on transactions
- Low stock detection when quantity ≤ minimum threshold
- Out of stock identification (quantity = 0)
- Complete transaction audit trail

### Search & Filtering
- Search products by name, description, or SKU
- Filter products by category or stock level
- Sort by name, price, quantity, or creation date
- Pagination support for large datasets

### Image Management
- Product image upload to `media/products/` directory
- Automatic URL generation for images
- Support for common image formats

### Transaction Types
- **Stock In (IN)**: Adding inventory
- **Stock Out (OUT)**: Removing inventory
- **Adjustment (ADJ)**: Manual stock corrections

## Authentication

The API uses token-based authentication. Include the token in request headers:

```bash
Authorization: Token your-token-here
```

To obtain a token, authenticate through Django admin or create a custom authentication endpoint.

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Configuration

### CORS Settings
Configure allowed origins in `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React frontend
    "http://127.0.0.1:3000",
]
```

### Media Files
Media files are served from `/media/` URL path in development. For production, configure proper media serving.

### Database
Default configuration uses SQLite. For production, update `DATABASES` setting:
```python
# You can use the default database settings, but if you want to use PostgreSQL, don't forget to apply the migrations.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Example Usage

### Create a Product
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Widget A",
    "sku": "WID-001",
    "price": "19.99",
    "cost_price": "12.00",
    "current_quantity": 100,
    "min_quantity": 10,
    "category_id": 1
  }'
```

### Record Stock Transaction
```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "transaction_type": "IN",
    "quantity": 50,
    "reason": "New shipment received"
  }'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the BSD License. See LICENSE file for details.

## Support

For questions or issues, please contact: deebhajjar04@gmail.com

## Development Notes

- The system automatically updates product quantities when transactions are created
- Previous quantity is stored for audit purposes
- Category deletion is protected if products exist in the category
- All timestamps are in UTC format
- Image uploads are handled securely with proper validation
