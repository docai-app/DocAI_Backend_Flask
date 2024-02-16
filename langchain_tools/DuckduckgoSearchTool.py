from langchain.tools import DuckDuckGoSearchResults, DuckDuckGoSearchRun
from langchain.utilities import DuckDuckGoSearchAPIWrapper

duckduckgo_search = DuckDuckGoSearchResults(
    name="duckduckgo_search",
    description=("當需要通過網絡去查找資料的時候，就使用這個功能"),
    api_wrapper=DuckDuckGoSearchAPIWrapper(max_results=8)
)
