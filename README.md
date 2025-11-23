# Fashion Recommender Starter

Prereqs:
- Python 3.10+
- MongoDB running locally at mongodb://localhost:27017 (or set MONGO_URI env)
- (Optional) real OpenMMLab models & LastMile/Tavily SDKs

Steps:

1) Start the inference microservice (OpenMMLab stub):
   cd ommlab_service
   pip install -r requirements.txt
   uvicorn openmmlab_service:app --port 8001 --reload

2) Seed items into MongoDB:
   cd seeder
   pip install -r requirements.txt
   python seed_items.py

3) Run the MCP app (fashion tool):
   cd mcp_agent_app
   pip install -r requirements.txt
   # Place sample.jpg next to main.py (or change main to point to an image)
   python main.py

This will call the fashion_recommendation_tool with sample.jpg and print recommendations.

Replace stubs:
- Replace `ommlab_service/openmmlab_service.py` with real OpenMMLab inference using MMDetection / MMFashion / CLIP.
- Replace `lastmile_client.py` & `tavily_client.py` with real SDK calls.
- For caching / NN search in production, use FAISS or MongoDB Atlas Vector Search.
"# Fashionista" 
"# Fashionista" 
"# Fashionista" 
