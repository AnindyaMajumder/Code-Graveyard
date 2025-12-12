from langchain.chat_models import init_chat_model
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from agents import meal_update_agent, workout_update_agent, get_profile
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
            tools=[get_profile],
            agents=[meal_update_agent, workout_update_agent],
            prompt=(
            "You are a fitness supervisor coordinating between meal and workout planning specialists. "
            "Keep responses concise, precise and relevant.\n\n"
            "DELEGATION RULES (MUST FOLLOW):\n"
            "- MealUpdateAgent: ANY request about diet, nutrition, meal plans, recipes, food\n"
            "- WorkoutUpdateAgent: ANY request about exercise, training, workout plans, fitness\n\n"
            "CRITICAL: When user mentions ANY of these keywords about workouts or meals, you MUST IMMEDIATELY delegate:\n"
            "- 'update', 'change', 'modify', 'adjust', 'create', 'suggest', 'missed', 'make up', 'reschedule'\n"
            "- Do NOT ask clarifying questions - delegate FIRST, let the agent handle details\n"
            "- Do NOT offer options yourself - delegate to the agent immediately\n\n"
            "GUIDELINES:\n"
            "- Respond directly ONLY for greetings, pleasantries, or general inquiries unrelated to planning\n"
            "- For ANY workout/meal related request, delegate to the appropriate agent\n"
            "- Don't ask for information already in the user's profile or plans\n"
            "- For combined meal and workout requests, coordinate both agents\n"
            "- Prioritize user safety with balanced recommendations"
            ),
            output_mode="last_message",
        ).compile(checkpointer=checkpointer)

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        async for event in supervisor.astream_events(
            {"messages": [{"role": "user", "content": user_message}]},
            config,
            version="v2",
        ):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    checkpoint_ns = event["metadata"].get("checkpoint_ns", "")
                    if checkpoint_ns.startswith("supervisor"):
                        yield chunk.content
        
if __name__ == "__main__":
    import asyncio
    import sys

    thread_id = "a4f65adddddas4"  

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