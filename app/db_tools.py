import random
from app.model import Product

def seed_products(session):
    

    sample_products = [
    {"name": "Blue Pen", "category": "Stationery", "unit_price": 1.50, "quantity": 100},
    {"name": "Red Pen", "category": "Stationery", "unit_price": 1.50, "quantity": 85},
    {"name": "A4 Notebook", "category": "Stationery", "unit_price": 4.99, "quantity": 50},
    {"name": "Stapler", "category": "Office", "unit_price": 12.99, "quantity": 25},
    {"name": "Paper Clips", "category": "Office", "unit_price": 2.25, "quantity": 200},
    {"name": "Highlighter", "category": "Stationery", "unit_price": 2.75, "quantity": 75},
    {"name": "Sticky Notes", "category": "Office", "unit_price": 3.50, "quantity": 120},
    {"name": "Eraser", "category": "Stationery", "unit_price": 0.99, "quantity": 150},
    {"name": "Black Marker", "category": "Stationery", "unit_price": 2.99, "quantity": 60},
    {"name": "Ruler 12inch", "category": "Stationery", "unit_price": 1.25, "quantity": 80},
    {"name": "Scissors", "category": "Office", "unit_price": 8.75, "quantity": 35},
    {"name": "Hole Punch", "category": "Office", "unit_price": 15.50, "quantity": 20},
    {"name": "Calculator", "category": "Electronics", "unit_price": 24.99, "quantity": 30},
    {"name": "USB Drive 16GB", "category": "Electronics", "unit_price": 19.99, "quantity": 45},
    {"name": "Desk Lamp", "category": "Furniture", "unit_price": 39.99, "quantity": 15},
    {"name": "File Folder", "category": "Office", "unit_price": 1.99, "quantity": 100},
    {"name": "Whiteboard Marker", "category": "Stationery", "unit_price": 3.25, "quantity": 90},
    {"name": "Tape Dispenser", "category": "Office", "unit_price": 7.50, "quantity": 40}
]


    for product_data in sample_products:
        product = Product(
            name=product_data["name"],
            category=product_data["category"],
            unit_price=product_data["unit_price"],
            stock_quantity=product_data["quantity"],
            out_of_stock=product_data["quantity"] == 0,
            authentication_string=f"auth_{random.randint(1000, 9999)}"
        )
        session.add(product)
    
    session.commit()
    print(f"Seeded {len(sample_products)} products into database")
    return



