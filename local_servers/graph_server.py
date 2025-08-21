import os
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from mcp.server.fastmcp import FastMCP


# Create MCP server instance
mcp = FastMCP("neo4j-assistant")

@mcp.tool()
def get_data_on_llm(query: str) -> str:
    """
    Get the information on LLM releted questions.

    This tool provides information on the query related to llm.

    Args:
        Query: The question asked by the user.
    
    Returns:
        A formatted string with answer to the given query
    Example:
        get_data_on_llm("what are the actions in llm?") returns response in string format.
    """
    try:
        def run_cypher(q):
            return cypher_chain.invoke({"query": q})
        return run_cypher(query)
    except Exception as e:
        return f"Error occured {e}"

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2
)

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Only include the generated Cypher statement in your response.

Always use case insensitive search when matching strings.

Schema:
{schema}

The question is:
{question}


You will also give the schema in the response.
restrictions:
Your are not allowed to answer if there not enough info in the provided information.

"""

cypher_generation_prompt = PromptTemplate(
    template=CYPHER_GENERATION_TEMPLATE,
    input_variables=["schema", "question"],
)

cypher_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=cypher_generation_prompt,
    verbose=True,
    allow_dangerous_requests=True,
)




if __name__ == "__main__":
    print(" neo4j Assistant MCP Server Starting...")
    print("=" * 50)
    print(" Server will run on stdio (for Claude Desktop)")
    print(" Available cities: New York, London, Tokyo, San Francisco")
    print(" Available tools:")
    print("   • get_current_neo4j(city)")
    print("   • get_neo4j_forecast(city, days)")
    print("   • compare_neo4j(city1, city2)")
    print(" Available resources:")
    print("   • neo4j://cities")
    print(" Available prompts:")
    print("   • neo4j_assistant_prompt")
    print("\n To use with Claude Desktop:")
    print("   1. Add server to Claude Desktop config")
    print("   2. Restart Claude Desktop")
    print("   3. Ask about neo4j in any supported city")
    print("\n Starting server...")
    
    # Run the server using stdio transport (standard for Claude Desktop)
    mcp.run(transport="stdio")
