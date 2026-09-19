from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI()

class ItemCreate(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None


class ItemPublic(BaseModel):
    id: int
    name: str
    price: float


class ItemListResponse(BaseModel): 
    items: list[ItemPublic]
    total: int
    skip: int
    limit: int


_items: list[ItemPublic] = []
_next_id = 1


def _find(item_id: int) -> ItemPublic | None:
    return next((it for it in _items if it.id == item_id), None)


def _name_taken(name: str, exclude_id: int | None = None) -> bool:
    return any(it.name.lower() == name.lower() and it.id != exclude_id for it in _items)


# GET /items:
@app.get("/items", response_model=ItemListResponse)
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    min_price: float | None = None,
    max_price: float | None = None,
    q: str | None = Query(None, min_length=2),
    sort_by: str = Query("id", pattern="^(id|name|price)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    result = _items
    if min_price is not None:
        result = [it for it in result if it.price >= min_price]
    if max_price is not None:
        result = [it for it in result if it.price <= max_price]
    if q is not None:
        result = [it for it in result if q.lower() in it.name.lower()]
    result = sorted(result, key=lambda it: getattr(it, sort_by), reverse=(order == "desc"))

    total = len(result)                  
    page = result[skip: skip + limit]      
    return ItemListResponse(items=page, total=total, skip=skip, limit=limit)


@app.get("/items/{item_id}", response_model=ItemPublic)
def get_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(data: ItemCreate):
    global _next_id
    if _name_taken(data.name):        
        raise HTTPException(status_code=409, detail="Item with this name already exists")
    item = ItemPublic(id=_next_id, name=data.name, price=data.price)
    _items.append(item)
    _next_id += 1
    return item


@app.put("/items/{item_id}", response_model=ItemPublic)
def replace_item(item_id: int, data: ItemCreate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if data.name.lower() != item.name.lower() and _name_taken(data.name, exclude_id=item_id):
        raise HTTPException(status_code=409, detail="Item with this name already exists")
    item.name, item.price = data.name, data.price
    return item


# PATCH only touches fields the client actually sent
@app.patch("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, data: ItemUpdate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    updates = data.model_dump(exclude_unset=True)
    new_name = updates.get("name")
    if new_name is not None and new_name.lower() != item.name.lower() and _name_taken(new_name, exclude_id=item_id):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    for field, value in updates.items():
        setattr(item, field, value)
    return item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    _items.remove(item)

# Part E: bonus prediction endpoint

class HousePriceRequest(BaseModel):
    area_sqm: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    distance_to_center_km: float


class HousePricePrediction(BaseModel):
    predicted_price: float
    currency: str = "VND"


@app.post("/predict/house-price", response_model=HousePricePrediction)
def predict_house_price(data: HousePriceRequest):
    price = (
        data.area_sqm * 15_000_000
        - data.distance_to_center_km * 5_000_000
        + data.bedrooms * 20_000_000
    )
    return HousePricePrediction(predicted_price=price)


# Serve the frontend 
app.mount("/static", StaticFiles(directory="../frontend"), name="static")