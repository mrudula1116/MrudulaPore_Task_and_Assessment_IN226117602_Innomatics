from fastapi import FastAPI,Query,Response,status
from pydantic import BaseModel ,Field
from typing import Optional,List
app = FastAPI()
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)
feedback=[]
class NewProduct(BaseModel):                            # Day 4
    name:     str  = Field(..., min_length=2, max_length=100)
    price:    int  = Field(..., gt=0)
    category: str  = Field(..., min_length=2)
    in_stock: bool = True
class CustomerFeedback(BaseModel):
    customer_name: str            = Field(..., min_length=2, max_length=100)
    product_id:   int            = Field(..., gt=0)
    rating:       int            = Field(..., ge=1, le=5)
    comment:      Optional[str]  = Field(None, max_length=300)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name:  str           = Field(..., min_length=2)
    contact_email: str           = Field(..., min_length=5)
    items:         List[OrderItem] = Field(..., min_items=1)

# ── Temporary data — acting as our database for now ──────────
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub',         'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',          'price':  49, 'category': 'Stationery',  'in_stock': True },
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
     {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True}, 
     {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
     { "id":8,"name": "Sticky Notes", "price": 49, "category": "Stationery", "in_stock": True},
     {"id":9,"name":"smart watch","price":3999,"category":"Electronics","in_stock":False} ]
orders = []
order_counter = 1


# Fixed routes (/filter /compare /audit /discount) BEFORE variable (/{product_id})
# ── Endpoint 0 — Home ────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
# ── Endpoint 1 — Return all products ──────────────────────────
@app.get('/products')
def get_all_products(): 
    
    return {'products': products, 'total': len(products)}

    
#endpoint 4
@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only'),
    min_price: int = Query(None, description='Minimum price'),
):
    result = products          # start with all products
 
    if category:
        result = [p for p in result if p['category'] == category]
 
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
 
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    if min_price:
        result = [p for p in result if p['price'] >= min_price]
 
    return {'filtered_products': result, 'count': len(result)}

   
#-Endpoint 3 category
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str): 
    result = [p for p in products if p["category"] == category_name] 
    if not result: 
        return {"error": "No products found in this category"} 
    return {"category": category_name, "products": result, "total": len(result)}
#- Endpoint 5 IN STOCK
@app.get("/products/instock") 
def get_instock(): 
    available = [p for p in products if p["in_stock"] == True] 
    return {"in_stock_products": available, "count": len(available)}
#end point store summary
@app.get("/store/summary") 
def store_summary(): 
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count 
    categories = list(set([p["category"] for p in products])) 
    return { "store_name": "My E-commerce Store", "total_products": len(products), "in_stock": in_stock_count, "out_of_stock": out_stock_count, "categories": categories, }
#end point search
@app.get("/products/search/{keyword}")
def search_products(keyword: str): 
    results = [ p for p in products if keyword.lower() in p["name"].lower() ] 
    if not results: return {"message": "No products matched your search"}
    return {"keyword": keyword, "results": results, "total_matches": len(results)}

#endpoint product price
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}
    #pydantic endpoint 

@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    product = find_product(order_data.product_id)
    if not product:
        return {'error': 'Product not found'}
    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}
    total = calculate_total(product, order_data.quantity)
    order = {
    'order_id':order_counter,
    'customer_name':order_data.customer_name,
    'product':product['name'],
    'quantity':order_data.quantity,
    'delivery_address':order_data.delivery_address,
    'total_price':total,
    'status':'pending'}
    orders.append(order)
    order_counter += 1 
    return {"message": "Order placed successfully", "order": order}
def find_product(product_id: int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None
 
def calculate_total(product: dict, quantity: int) -> int:
    return product['price'] * quantity
 
def filter_products_logic(category=None, min_price=None,
                          max_price=None, in_stock=None):
    result = products
    if category  is not None: result = [p for p in result if p['category']==category]
    if min_price is not None: result = [p for p in result if p['price']>=min_price]
    if max_price is not None: result = [p for p in result if p['price']<=max_price]
    if in_stock  is not None: result = [p for p in result if p['in_stock']==in_stock]
    return result
@app.get("/orders")
def get_orders():
    return {"orders": orders}
# New GET by order ID:
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}
    return {"error": "Order not found"}

# PATCH to confirm:
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {"message": "Order confirmed", "order": order}
    return {"error": "Order not found"}
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message":        "Feedback submitted successfully",
        "feedback":       data.dict(),
        "total_feedback": len(feedback)
    }
#product summary endpoint
@app.get("/products/summary")
def product_summary():
    in_stock   = [p for p in products if     p["in_stock"]]
    out_stock  = [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))
    return {
        "total_products":     len(products),
        "in_stock_count":     len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive":     {"name": expensive["name"], "price": expensive["price"]},
        "cheapest":           {"name": cheapest["name"],  "price": cheapest["price"]},
        "categories":         categories,
    }
#bulk order
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})

    return {"company": order.company_name, "confirmed": confirmed,
            "failed": failed, "grand_total": grand_total}
#endpoint audit summary
@app.get('/products/audit') 
def product_audit(): 
    in_stock_list = [p for p in products if p['in_stock']] 
    out_stock_list = [p for p in products if not p['in_stock']] 
    stock_value = sum(p['price'] * 10 for p in in_stock_list) 
    priciest = max(products, key=lambda p: p['price']) 
    return { 'total_products': len(products), 'in_stock_count': len(in_stock_list), 'out_of_stock_names': [p['name'] for p in out_stock_list], 'total_stock_value': stock_value, 'most_expensive': {'name': priciest['name'], 'price': priciest['price']}, }
@app.put('/products/discount')
def bulk_discount(
    category: str = Query(..., description='Category to discount'),
    discount_percent: int = Query(..., ge=1, le=99, description='% off')
):

    updated = []

    for p in products:
        if p['category'] == category:
            p['price'] = int(p['price'] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {'message': f'No products found in category: {category}'}

    return {
        'message': f'{discount_percent}% discount applied to {category}',
        'updated_count': len(updated),
        'updated_products': updated}
# ── Endpoint 2 — Return one product by its ID ──────────────────
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
#post product endpoint
@app.post('/products')
def add_product(new_product: NewProduct, response: Response):
    # Check for duplicate name (case-insensitive)
    existing_names = [p['name'].lower() for p in products]
    if new_product.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Product with this name already exists'}
 
    # Auto-generate next ID
    next_id = max(p['id'] for p in products) + 1
 
    product = {
        'id':       next_id,
        'name':     new_product.name,
        'price':    new_product.price,
        'category': new_product.category,
        'in_stock': new_product.in_stock,
    }
    products.append(product)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Product added', 'product': product}
    #update
@app.put('/products/{product_id}')
def update_product(
    product_id: int,
    response:   Response,
    in_stock:   bool = Query(None, description='Update stock status'),
    price:      int  = Query(None, description='Update price'),
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
 
    if in_stock is not None:     # must use 'is not None' — False is a valid value
        product['in_stock'] = in_stock
    if price is not None:
        product['price'] = price
 
    return {'message': 'Product updated', 'product': product}
# ── DAY 4 — Step 20: Delete a product (DELETE) ────────────────────
 
@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
 
    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}
 
 