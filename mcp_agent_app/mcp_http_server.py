# mcp_http_server.py — FINAL WORKING VERSION (2025 mcp-agent)
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

# Import your agent and models
from fashion_agent import (
    app as mcp_app,
    fashion_recommendation_tool,           # ← Direct function import
    fashion_recommendation_toolArguments,
    FashionRecommendationOutput
)

api_app = FastAPI(title="Fashion AI API", version="1.0")

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api_app.post("/recommend", response_model=FashionRecommendationOutput)
async def get_recommendations(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    context_info: Optional[str] = Form(None)
):
    try:
        image_bytes = await file.read()
        args = fashion_recommendation_toolArguments(
            image_bytes=image_bytes,
            user_id=user_id,
            context_info={}
        )

        # THIS IS THE ONLY LINE THAT MATTERS NOW
        result = await fashion_recommendation_tool(args)   # ← Call directly!

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"error": str(e), "recommendations": {}},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api_app, host="0.0.0.0", port=8000)