from langchain.chat_models import init_chat_model
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from agents import Meal, Workout
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
            agents=[Meal(), Workout()],
            prompt=(
                "You are a fitness supervisor agent coordinating between meal and workout planning specialists. "
                "Your role is to understand user requests and delegate tasks to the appropriate agents:\n\n"
                "- Use MealUpdateAgent for questions about diet, nutrition, meal plans, recipes, or food-related queries.\n"
                "- Use WorkoutUpdateAgent for questions about exercise, training routines, workout plans, or fitness activities.\n\n"
                "If the user's request involves both meal and workout planning, coordinate between both agents. "
                "Synthesize their responses into a comprehensive fitness plan. "
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
        
        messages = []
        async for chunk in supervisor.astream(
            {"messages": [{"role": "user", "content": user_message}]},
            config,  
            stream_mode="values"
        ):
            messages = chunk["messages"]
        
        return messages[-1] if messages else None
        
if __name__ == "__main__":
    import asyncio
    import sys

    thread_id = "test"  

    print("Chatbot ready. Type your messages below (Ctrl+C or 'quit' to exit).")
    try:
        while True:
            user_input = input("Human> ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if user_input:
                response = asyncio.run(chat(thread_id=thread_id, user_message=user_input))
                print(f"AI > {response.content}")
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)