
import sys
import asyncio


from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

### TOOLS

# --- Fonction 1 : Lister les outils ---
async def get_tools_from_mcp():
    # Define the server parameters
    params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
    )


    # Connect to the MCP server and open a session
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # Initialize the session
            await session.initialize()

            # Ask the server what tools it provides
            response = await session.list_tools()

             # Display the available tools
            print("Connected to MCP server!")
            print("Available tools:")
            for tool in response.tools:
                print(f" - {tool.name}: {tool.description}")
                
            return response.tools

# --- Fonction 2 : Estimer les vaccins (avec argument population) ---
async def call_mcp_tool(tool_name:str, arguments:dict)->str:
    params = StdioServerParameters(
        command = sys.executable,
        args = ["mcp_server.py"]
    )        

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            # Call the oral polio vaccine estimator tool
            result = await session.call_tool(tool_name, arguments)

            # Extract and print the text content of the server response
            text_content = result.content[0].text

            print(f"OPV estimation: {text_content}")
            return text_content

        
### PROMPTS

async def list_prompts():
    """List all available prompts from the MCP server."""
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            # List available prompts
            prompts = await session.list_prompts()
            print(f"Available prompts: {[p.name for p in prompts.prompts]}")

            return prompts.prompts

async def read_prompt(user_input: str, prompt_name: str = "opv_estimator_prompt") -> str:
    """Retrieve a prompt from the MCP server with user input."""
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            # Retrieve the prompt with the user's input
            # La règle d'or pour le MCP :
            # Dans le Model Context Protocol, les clés du dictionnaire arguments côté client doivent impérativement correspondre nom pour nom aux arguments définis dans la fonction Python du serveur.
            # ici côté client arguments={"estimation_request": user_input} == côté server def opv_estimator_prompt(estimation_request:str) -> str:
            
            prompt = await session.get_prompt(prompt_name, arguments={"estimation_request": user_input})

            # Print the full prompt text (template + user request)
            text = prompt.messages[0].content.text
            print(text)
            return text

#### RESOURCES

async def list_resources():
    """List all available resources from the MCP server."""
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            # Get the list of resources
            response = await session.list_resources()

            print("Available resources:")
            # Print each resource's URI, name, and description
            for resource in response.resources:
                print(f" - {resource.uri}")
                print(f"   Name: {resource.name}")
                print(f"   Description: {resource.description}")

            return response.resources


# Define an async function for reading MCP resources
async def read_resource(resource_uri: str):
    """Read a specific resource by URI."""
    params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
    )

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            print(f"Reading resource: {resource_uri}")
            # Read the resource from the session context
            resource_content = await session.read_resource(resource_uri)

            # Print the contents of each resource
            for content in resource_content.contents:
                print(f"\nContent ({content.mime_type}):")
                print(content.text)

            return resource_content





asyncio.run(read_resource("config://vaccine-default-params-value"))
# asyncio.run(list_resources())    
# asyncio.run(list_prompts())
# asyncio.run(call_mcp_tool("polio_vaccine_estimator",{"population": 78921}))
# asyncio.run(read_prompt(user_input="Estimates the total number of oral polio vaccine for a population of 78921"))