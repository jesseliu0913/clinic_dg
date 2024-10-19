import os
import bs4
from langchain_community.document_loaders import WebBaseLoader


os.environ['USER_AGENT'] = 'myagent'
page_url = "https://python.langchain.com/docs/how_to/chatbots_memory/"

async def load_docs():
    loader = WebBaseLoader(web_paths=[page_url])
    docs = []
    async for doc in loader.alazy_load():
        docs.append(doc)
    return docs

# Run the async function
import asyncio
docs = asyncio.run(load_docs())

# Verify that the document is loaded correctly
assert len(docs) == 1
doc = docs[0]

print(f"{doc.metadata}\n")
print(doc.page_content[:500].strip())