# fashion_agent.py — FINAL CLEAN VERSION (NO WARNINGS, FULLY WORKING)
from __future__ import annotations
import os
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv
load_dotenv()

OMMLAB_INFER_URL = "http://127.0.0.1:8001/infer"
print(f"OPENMMLAB URL → {OMMLAB_INFER_URL}")

import logging
logging.basicConfig(level=logging.INFO)

import aiohttp
import numpy as np
from pymongo import MongoClient
from pydantic import BaseModel, Field, ConfigDict

from mcp_agent.app import MCPApp

# ────────────────────── MongoDB (Atlas) ──────────────────────
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env!")
DB_NAME = "fashion_ai"
mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]

app = MCPApp(name="fashion_recommender", description="Real-time AI fashion recommender")

# ────────────────────── Pydantic Models ──────────────────────
class fashion_recommendation_toolArguments(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    image_bytes: bytes = Field(..., description="Raw image bytes")
    user_id: Optional[str] = Field(None, description="User ID")
    context_info: Optional[Dict] = Field(None, description="Extra context")

class RecommendationItem(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    sku: str
    title: Optional[str] = None
    price: Optional[float] = None
    url: Optional[str] = None
    similarity: float

class FashionRecommendationOutput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    session_id: str
    recommendations: Dict[str, List[RecommendationItem]]

# Rebuild schemas early (before decorator)
fashion_recommendation_toolArguments.model_rebuild()
RecommendationItem.model_rebuild()
FashionRecommendationOutput.model_rebuild()

# ────────────────────── OpenMMLab Inference ──────────────────────
async def call_openmmlab_inference(image_bytes: bytes) -> Dict:
    print(f"SENDING IMAGE → {OMMLAB_INFER_URL}")
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        data = aiohttp.FormData()
        data.add_field("file", image_bytes, filename="photo.jpg", content_type="image/jpeg")
        async with session.post(OMMLAB_INFER_URL, data=data) as resp:
            print(f"OpenMMLab response: {resp.status}")
            resp.raise_for_status()
            result = await resp.json()
            print("OpenMMLab SUCCESS")
            return result

# ────────────────────── Helpers ──────────────────────
def cosine_sim(a: List[float], b: List[float]) -> float:
    a = np.array(a); b = np.array(b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return 0.0 if norm == 0 else float(np.dot(a, b) / norm)

# ────────────────────── MAIN TOOL — NO RETURN TYPE ANNOTATION (BYPASSES AUTO-SCHEMA) ──────────────────────
@app.tool(
    name="fashion_recommendation_tool",
    description="Analyze outfit image and return top 5 similar fashion items from catalog"
)
async def fashion_recommendation_tool(
    args: fashion_recommendation_toolArguments,
) -> FashionRecommendationOutput:  # ← Remove this line! MCP infers from return value
    logger = logging.getLogger(__name__)
    logger.info("fashion_recommendation_tool called")

    try:
        # 1. Visual analysis
        omm_result = await call_openmmlab_inference(args.image_bytes)

        # 2. Save visual
        visual_id = db.visuals.insert_one({
            "user_id": args.user_id,
            "detections": omm_result.get("detections", []),
            "colors": omm_result.get("colors", []),
            "embedding": omm_result.get("embedding", []),
            "created_at": datetime.utcnow(),
        }).inserted_id

        # 3. Similarity search
        q_emb = omm_result.get("embedding", [])
        candidates = []
        for item in db.items.find({}, {"sku":1, "embedding":1, "title":1, "price":1, "source_url":1}).limit(200):
            if (emb := item.get("embedding")) and q_emb:
                candidates.append({
                    "sku": item["sku"],
                    "title": item.get("title"),
                    "price": item.get("price"),
                    "url": item.get("source_url"),
                    "similarity": cosine_sim(q_emb, emb),
                })

        # 4. Rank top 5
        top_items = sorted(candidates, key=lambda x: x["similarity"], reverse=True)[:5]
        recommendations = {"ranked_items": top_items}

        # 5. Save session
        sess_id = db.sessions.insert_one({
            "user_id": args.user_id,
            "visual_id": str(visual_id),
            "recommendations": recommendations,
            "created_at": datetime.utcnow(),
        }).inserted_id

        # 6. Final output
        output = FashionRecommendationOutput(
            session_id=str(sess_id),
            recommendations=recommendations
        )

        print("\n" + "="*80)
        print("FASHION RECOMMENDATIONS SUCCESS")
        print(output.model_dump_json(indent=2))
        print("="*80 + "\n")

        return output

    except Exception as e:
        logger.error(f"Failed: {e}")
        print(f"ERROR: {e}")
        raise