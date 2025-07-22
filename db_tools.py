import random
from model import Product

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
    ]
    
    # Create and add products
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
