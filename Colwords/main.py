from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from chat import call_model

workflow = StateGraph(state_schema=MessagesState)

# Define the node and edge
workflow.add_node("model", call_model)
workflow.add_edge(START, "model")

# Add simple in-memory checkpointer
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

all_messages = [SystemMessage(content="You are a helpful assistant. Answer all questions to the best of your ability.")]

while True:
    inp = input("User: ")
    if( inp.lower() in ["exit", "quit"]):
        break
    
    all_messages.append(HumanMessage(content=inp))
    
    result = app.invoke(
        {"messages": all_messages},
        config={"configurable": {"thread_id": "1"}},
    )
    all_messages.append(AIMessage(content=result["messages"][-1].content))

    print("AI:", result["messages"][-1].content)