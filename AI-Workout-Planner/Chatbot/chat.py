from langchain.chat_models import init_chat_model
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from agents import Meal, Workout, Profile
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = init_chat_model(model="gpt-5-nano", api_key=api_key)

DB_URI = os.getenv("DB_URI")

async def chat(thread_id: str, user_message: str):
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:  
        await checkpointer.setup()
        
        # Supervisor agent
        supervisor = create_supervisor(
            model=model,
            agents=[Meal(), Workout(), Profile()],
            prompt=(
                "You are a fitness supervisor agent coordinating between meal and workout planning specialists. Keep your responses concise and relevant.\n\n"
                "Your role is to understand user requests and delegate tasks to the appropriate agents:\n\n"
                "DELEGATION RULES:\n"
                "- Use MealUpdateAgent for questions about diet, nutrition, meal plans, recipes, or food-related queries.\n"
                "- Use WorkoutUpdateAgent for questions about exercise, training routines, workout plans, or fitness activities.\n"
                "- Use ProfileAgent for questions about user fitness profiles, goals, preferences, restrictions or any related information.\n\n"
                "IMPORTANT:\n"
                "- Agents return conversational responses with awareness of user data\n"
                "- When users request plan updates, agents will provide both explanation AND structured data\n"
                "- For general queries, agents provide friendly responses about current user status\n"
                "- If the user's request involves both meal and workout planning, coordinate between both agents\n\n"
                "Always prioritize user safety and provide balanced recommendations."
            ),
            add_handoff_back_messages=True,
            output_mode="full_history",
        ).compile(checkpointer=checkpointer)

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        async for event in supervisor.astream_events(
            {"messages": [{"role": "user", "content": user_message}]},
            config,
        ):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content
        
if __name__ == "__main__":
    import asyncio
    import sys

    thread_id = "test2"  

    print("Chatbot ready. Type your messages below (Ctrl+C or 'quit' to exit).")
    try:
        while True:
            user_input = input("Human> ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if user_input:
                print("AI > ", end="", flush=True)
                async def stream_response():
                    async for token in chat(thread_id=thread_id, user_message=user_input):
                        print(token, end="", flush=True)
                    print()  # New line after response
                asyncio.run(stream_response())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)