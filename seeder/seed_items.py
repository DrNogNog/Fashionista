# seed_items.py
import os
import random
import numpy as np
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://g90531451_db_user:HcaVBBdxxZAyoSg4@cluster0.4evpyak.mongodb.net/?appName=Cluster0"
)
DB_NAME = os.getenv("DB_NAME", "fashion_ai")
NUM_ITEMS = 1000

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def make_embedding(seed):
    rng = np.random.RandomState(seed)
    vec = rng.randn(256).astype(float)
    vec = vec / (np.linalg.norm(vec) + 1e-9)
    return vec.tolist()

def seed():
    items = []
    for i in range(NUM_ITEMS):
        sku = f"SKU-{100000 + i}"
        emb = make_embedding(i)
        item = {
            "sku": sku,
            "title": f"Sample Item {i}",
            "brand": random.choice(["BrandA","BrandB","BrandC"]),
            "price": round(random.uniform(30, 400), 2),
            "source_url": f"https://example.com/product/{sku}",
            "embedding": emb,
            "tags": random.sample(["jacket","shirt","dress","casual","formal","summer","winter"], k=3),
            "created_at": datetime.utcnow()
        }
        items.append(item)
    db.items.delete_many({})
    db.items.insert_many(items)
    print(f"Seeded {NUM_ITEMS} items in {DB_NAME}.items")

if __name__ == "__main__":
    seed()
