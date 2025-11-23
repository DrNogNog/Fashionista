import requests, base64

with open("sample.jpg", "rb") as f:
    img_bytes = base64.b64encode(f.read()).decode()

resp = requests.post(
    "http://localhost:8000/mcp",
    json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "fashion_recommendation_tool",
            "arguments": {"image_bytes": img_bytes, "user_id": "web_user_123"}
        },
        "id": 1
    },
    headers={"Accept": "application/json, text/event-stream"}
)
print(resp.text)
