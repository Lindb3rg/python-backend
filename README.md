 # Inventory and Order Management API

 This is a simple RESTful API for managing products and orders, built with FastAPI and SQLModel using SQLite for data storage. The database is automatically created and seeded on startup and dropped on shutdown.

 ## Features
 - CRUD operations for products
 - CRUD operations for orders
 - Automatic database creation and seeding

 ## Requirements
 - Python 3.11 or later

 ## Installation
 1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repo-directory>
    ```
 2. Create and activate a virtual environment:
    ```bash
    python3 -m venv env
    source env/bin/activate    # On Windows: env\\Scripts\\activate
    ```
 3. Install dependencies:
    ```bash
    pip install fastapi uvicorn sqlmodel
    ```

 ## Running the application
 Start the server with:
 ```bash
 uvicorn main:app --reload
 ```
 The server will run at `http://127.0.0.1:8000`.

 ## API Documentation
 - Swagger UI: `http://127.0.0.1:8000/docs`
 - ReDoc: `http://127.0.0.1:8000/redoc`

 ## API Endpoints

 ### Products
 - `POST /products/` – Create a new product
 - `GET /products/` – Retrieve a list of products
 - `GET /products/{product_id}` – Retrieve a product by ID
 - `PATCH /products/{product_id}` – Update a product
 - `DELETE /products/{product_id}` – Delete a product

 ### Orders
 - `POST /orders/` – Create a new order
 - `GET /orders/` – Retrieve a list of orders
 - `GET /orders/{order_id}` – Retrieve an order by ID
 - `PATCH /orders/{order_id}` – Update an order
 - `DELETE /orders/{order_id}` – Delete an order

 ## Database
 - SQLite file: `database.db`
 - Schema: `db/schema/schema.sql`
 - ERD diagram: folder `ERD`

 ## Contributing
 Feel free to open issues or submit pull requests.