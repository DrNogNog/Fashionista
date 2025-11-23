import asyncio
from pathlib import Path
from mcp_agent.app import MCPApp
from fashion_agent import fashion_recommendation_tool, fashion_recommendation_toolArguments

# Initialize the MCPApp runner
app = MCPApp(name="fashion_recommender_runner", description="Run fashion tool locally")

async def main():
    # Use the MCPApp runner context to supply app_ctx to tools
    async with app.run() as agent_app:
        # Read a sample image from disk
        img_path = Path("sample.jpg")
        if not img_path.exists():
            print("Place a sample image named sample.jpg next to main.py to test.")
            return
        image_bytes = img_path.read_bytes()

        # Build arguments using the Pydantic model
        args = fashion_recommendation_toolArguments(
            image_bytes=image_bytes,
            user_id=None,
            context_info={"budget": 200}
        )

        # Call the tool
        res = await fashion_recommendation_tool(
            args=args,
            app_ctx=agent_app.context
        )
        print("Result:", res)

if __name__ == "__main__":
    asyncio.run(main())
