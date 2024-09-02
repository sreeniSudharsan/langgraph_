#Custom Tooling. Need to test it out later

# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain.tools import tool
# from typing import Optional

# @tool
# def search_tool():
#     '''    
#     Tool for searching the web using TavilySearchResults. Use this wisely
#     '''
#     if input is None:
#         return 'Sorry I did not get that! Can you please type in again'
#     tool = TavilySearchResults(max_results=2)
#     return tool


# #tool - testing
# if __name__ == "__main__":
#     result = search_tool.invoke("What's a node in langgraph?")
#     for object in result:
#         url, content = object['url'], object['content']
#         print(f'"URL": {url} \n "Content": {content}')
