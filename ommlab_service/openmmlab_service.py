# openmmlab_service.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np
import hashlib
import io
from skimage.color import rgb2lab
from collections import Counter

app = FastAPI(title="OpenMMLab-stub")

def image_to_embedding(img: Image.Image, dim=256):
    """
    Deterministic pseudo-embedding by hashing scaled pixels.
    Replace this with a CLIP/OpenMMLab embedding when available.
    """
    img = img.resize((128,128)).convert("RGB")
    arr = np.array(img).astype(np.float32) / 255.0
    flat = arr.flatten()
    # Use a simple projection: take SHA256 and expand
    h = hashlib.sha256(flat.tobytes()).digest()
    vec = np.frombuffer(h, dtype=np.uint8).astype(np.float32)
    # expand to requested dim by repeating
    rep = np.tile(vec, (int(np.ceil(dim / len(vec))),))[:dim].astype(np.float32)
    # normalize
    rep = rep / (np.linalg.norm(rep) + 1e-9)
    return rep.tolist()

def dominant_colors(img: Image.Image, k=3):
    """Simple dominant color extractor using quantization"""
    img = img.convert("RGB").resize((64,64))
    arr = np.array(img).reshape(-1,3)
    # quantize by rounding
    q = (arr // 32) * 32
    counts = Counter([tuple(p) for p in q])
    top = counts.most_common(k)
    # convert to hex
    def to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)
    return [to_hex(t[0]) for t in top]

def fake_detections(img: Image.Image):
    """Produce a set of fake clothing detections (stub)"""
    # naive: if wider than tall assume full-body; else upper-body
    w, h = img.size
    if w > h:
        return [{"label": "full_body", "bbox": [0,0,w,h], "score": 0.95},
                {"label": "jacket", "bbox": [20, 20, int(w*0.6), int(h*0.6)], "score": 0.88}]
    else:
        return [{"label": "upper_body", "bbox": [0,0,w,int(h*0.7)], "score": 0.96},
                {"label": "shirt", "bbox": [10, 10, int(w*0.8), int(h*0.6)], "score": 0.90}]

@app.post("/infer")
async def infer(file: UploadFile = File(...)):
    bytes_data = await file.read()
    img = Image.open(io.BytesIO(bytes_data)).convert("RGB")
    embedding = image_to_embedding(img, dim=256)
    colors = dominant_colors(img, k=3)
    detections = fake_detections(img)
    response = {
        "detections": detections,
        "colors": colors,
        "embedding": embedding,
        # per-item embedding stubs (here only one global)
        "item_embeddings": [{"bbox": d.get("bbox"), "embedding": embedding} for d in detections],
        "meta": {"height": img.height, "width": img.width}
    }
    return JSONResponse(response)
