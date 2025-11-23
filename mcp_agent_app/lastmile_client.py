import asyncio
from typing import Dict, List, Any
import random

async def run_lastmile_workflow(workflow_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async stub for running a LastMile workflow.

    Replace with actual LastMile SDK call, e.g. lastmile.run_workflow(...)

    Args:
        workflow_name: Name of the LastMile workflow to run.
        payload: Dictionary containing workflow inputs, e.g., candidates.
        
    Returns:
        Dictionary with ranked_items, pairings, and a CTA.
    """
    await asyncio.sleep(0.2)  # simulate network latency

    candidates: List[Dict[str, Any]] = payload.get("candidates", [])

    # Rank candidates by similarity (descending)
    ranked = sorted(candidates, key=lambda c: c.get("similarity", 0), reverse=True)[:5]

    ranked_items = [
        {
            "sku": c["sku"],
            "score": float(c.get("similarity", 0)),
            "title": c.get("title", c["sku"]),
            "price": c.get("price", round(random.uniform(20, 200), 2)),
            "image_url": c.get("image_url", None),
            "reason": "Visual match"
        }
        for c in ranked
    ]

    # Example pairings based on top ranked item
    pairings = []
    if ranked_items:
        pairings.append({
            "items": [ranked_items[0]["sku"]],
            "description": "Pair with minimal accessories for a clean look"
        })

    return {
        "ranked_items": ranked_items,
        "pairings": pairings,
        "cta": {
            "type": "link",
            "payload": ranked[0].get("url", "#") if ranked else "#"
        },
    }