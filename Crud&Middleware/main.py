from fastapi import FastAPI, Request
from pydantic import BaseModel
from db import engine, SessionLocal
from models import Base, Item
import time
import json

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def log_request_data(request: Request, call_next):
    start_time = time.time()
    
    method = request.method
    url = str(request.url)

    query_params = dict(request.query_params)

    # Request body
    try:
        body_bytes = await request.body()
        body = body_bytes.decode("utf-8")
        if body:
            body = json.loads(body)  # JSON bo'lsa dictga o'tkazamiz
    except Exception:
        body = None

    response = await call_next(request)

    process_time = time.time() - start_time
    status_code = response.status_code

    print(f"Method: {method}")
    print(f"URL: {url}")
    print(f"Query params: {query_params}")
    print(f"Body: {body}")
    print(f"Status: {status_code}")
    print(f"Processed in: {process_time:.4f}s\n")

    return response


class ItemSchema(BaseModel):
    name : str 
    price : float
    quantity : int

@app.post('/items')
async def create_item(item: ItemSchema):
    db = SessionLocal()
    existing_item = db.query(Item).filter(Item.name == item.name).first()
    if existing_item:
        db.close()
        return {"error": "Item with this name already exists"}
    db_item = Item(name=item.name, price=item.price, quantity=item.quantity)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.get('/items/{item_id}')
async def get_item(item_id : int):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    db.close()
    if not db_item:
        return {"error" : "Item not found"}
    return db_item

@app.put('/item/{item_id}')
async def put_item(item_id : int, item : ItemSchema):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        db.close()
        return {"error" : "Item not found"}
    db_item.name = item.name
    db_item.price = item.price
    db_item.quantity = item.quantity
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.delete('/item/{item_id}')
async def delete_item(item_id : int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        return {"error" : "Item not found"}
    db.delete(item)
    db.commit()
    db.close()
    return {"message": "Item successfully deleted"}