from langchain_core.messages import HumanMessage

from app.agents.graph import graph


def main():
    for i in [
        "How many trips started between 8am and 9am?",
        "What modes of transport are in this dataset?",
        "How many trips pass through the area between longitude 116.3-116.4 and latitude 39.9-40.0?",
        "What's the average speed of bike trips?",
    ]:
        result = graph.invoke({"messages": [HumanMessage(content=i)]})
        print(result["messages"][-1].content)
        print()
        print("=======================")
        print()


if __name__ == "__main__":
    main()
