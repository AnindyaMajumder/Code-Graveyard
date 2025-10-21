from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import uuid

from gen_models import chat
from flashcards import flashcard

workflow = StateGraph(state_schema=MessagesState)

# Define the node and edge
workflow.add_node("chatbot", chat)
workflow.add_edge(START, "chatbot")

# Add simple in-memory checkpointer
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Use a unique thread ID for each session
thread_id = str(uuid.uuid4())

all_messages = [SystemMessage(content="You are a helpful assistant. Answer all questions to the best of your ability.")]

while True:
    inp = input("User: ")
    if( inp.lower() in ["exit", "quit"]):
        break
    
    if(inp.lower() == "Generate flashcards"):
        last_5_messages = "\n".join([msg.content for msg in all_messages[1:][-5:]])
        flashcard(last_5_messages)
    
    all_messages.append(HumanMessage(content=inp))
    
    result = app.invoke(
        {"messages": all_messages},
        config={"configurable": {"thread_id": thread_id}},
    )
    all_messages.append(AIMessage(content=result["messages"][-1].content))

    print("AI:", result["messages"][-1].content)

# print(thread_id, all_messages)
print("Last 5 messages:")
print(type(all_messages[1:][-5:]))