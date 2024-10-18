import json
import os

def get_sold_item_input():
    """Get user input for sold item details."""
    item_name = input("Enter the name of the sold item: ")
    quantity = input("Enter the quantity sold: ")
    price_per_unit = input("Enter the price per unit: ")
    return {'item_name': item_name, 'quantity': int(quantity), 'price_per_unit': float(price_per_unit)}

def load_sold_items(file_path):
    """Load sold items from the JSON file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

def save_sold_items(sold_items, file_path):
    """Save sold items to the JSON file."""
    with open(file_path, 'w') as file:
        json.dump(sold_items, file, indent=4)

def update_sold_items():
    """Update the list of sold items."""
    file_path = 'sold_items.json'
    new_item = get_sold_item_input()
    sold_items = load_sold_items(file_path)
    sold_items.append(new_item)
    save_sold_items(sold_items, file_path)
    print(f"Sold item registered: {new_item['item_name']} (Quantity: {new_item['quantity']}, Price per unit: {new_item['price_per_unit']})")

if __name__ == "__main__":
    update_sold_items()