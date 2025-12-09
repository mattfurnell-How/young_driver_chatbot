from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

app = FastAPI(title="Young Driver Products API")

# Allow your website/app to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path("young_driver_products.json")

def load_products():
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/young-driver-products")
def get_products():
    return load_products()

@app.get("/young-driver-products/{product_id}")
def get_product(product_id: str):
    products = load_products()
    for p in products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")
