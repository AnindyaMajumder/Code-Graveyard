from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver  
import uuid

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = init_chat_model(model="gpt-3.5-turbo", api_key=api_key)

DB_URI = os.getenv("DB_URI")

async def chat(thread_id: str, user_message: str):
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:  
        await checkpointer.setup()

        async def call_model(state: MessagesState):
            system_msg = SystemMessage("You are a fitness expert specializing in creating personalized workout and meal plans. Provide suggestions based on user preferences, fitness levels, and goals. Don't include any out of the context information. Be concise and to the point.")
            response = await model.ainvoke([system_msg] + state["messages"])
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
        
        messages = []
        async for chunk in graph.astream(
            {"messages": [{"role": "user", "content": user_message}]},
            config,  
            stream_mode="values"
        ):
            messages = chunk["messages"]
        
        return messages[-1] if messages else None
        
if __name__ == "__main__":
    import asyncio
    import sys

    thread_id = "terminal-test"  

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