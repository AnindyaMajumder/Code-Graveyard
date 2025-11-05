from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver  
import uuid

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = init_chat_model(model="gpt-3.5-turbo", api_key=api_key)

DB_URI = "postgresql://postgres:123456@localhost:5432/postgres?sslmode=disable"

async def chat(thread_id: str, user_message: str):
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:  
        await checkpointer.setup()

        async def call_model(state: MessagesState):
            response = await model.ainvoke(state["messages"])
            return {"messages": response}

        builder = StateGraph(MessagesState)
        builder.add_node(call_model)
        builder.add_edge(START, "call_model")

        graph = builder.compile(checkpointer=checkpointer)  

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        async for chunk in graph.astream(
            {"messages": [{"role": "user", "content": user_message}]},
            config,  
            stream_mode="values"
        ):
            chunk["messages"][-1].pretty_print()
        
if __name__ == "__main__":
    # import asyncio
    # asyncio.run(chat(thread_id="1", user_message="Hello, I'm Bob!"))  
    
    import asyncio
    import sys

    thread_id = "terminal-test"  

    print("Chatbot ready. Type your messages below (Ctrl+C or 'quit' to exit).")
    try:
        while True:
            user_input = input("\n> ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if user_input:
                asyncio.run(chat(thread_id=thread_id, user_message=user_input))
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)