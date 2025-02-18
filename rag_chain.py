from langchain import hub
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv, find_dotenv
from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from pinecone import Pinecone
import os
import logging
import asyncio


load_dotenv(find_dotenv())

os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ['LANGCHAIN_PROJECT'] = 'end-to-end-rag'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/ragchain.log"),
        logging.StreamHandler()
    ]       
)

class RAGPipeline:
    def __init__(self, index_name):
        self.index_name = index_name
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama3-70b-8192",
            temperature=0
        )
        logging.info("Init LLM with: %s .", self.llm)
        
        self.rag_prompt = hub.pull("rlm/rag-prompt",
                                api_key=os.getenv("LANGSMITH_API_KEY")
                                )
        logging.info("Init Prompt form langchain prompt hub")
        
        self.rails_config = RailsConfig.from_path("./config")
        self.guardrails = RunnableRails(config=self.rails_config, llm=self.llm)
        logging.info("Init NeMo LLM Guardrails")
    
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"),
                                           model="text-embedding-3-small")
        logging.info("Initialized OpenAI Embeddings with model: %s", self.embeddings.model)
        
        self.vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings,
            pinecone_api_key=os.getenv("PINECONE_API_KEY")
        )
        
        logging.info("Pinecone Vectorstore initialized with inde name: %s",index_name)
        
        #create the retirval chain
        self.retriever = self.vectorstore.as_retriever()
        
        format_docs = lambda docs: "\n\n".join(doc.page_content for doc in docs)
        
        self.rag_chain = (
            {
                "context": self.retriever | format_docs, "question": RunnablePassthrough()
            }
            | self.rag_prompt
            | self.llm
            | StrOutputParser()
        )
        self.rag_chain = self.guardrails | self.rag_chain
        
    async def qa_async(self, query: str) -> str:
        """
        Async version of the question-answering method.
        """
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        if self.index_name in pc.list_indexes().names():
            # Use ainvoke for async operation
            response = await self.rag_chain.ainvoke(query)
            return response
        else:
            logging.error("No Index is provided")
            raise ValueError("Index not found")
    
    def qa(self, query: str) -> str:
        """
        Synchronous version of the question-answering method.
        Maintained for backward compatibility.
        """
        return asyncio.run(self.qa_async(query))


#if __name__ == "__main__":
#    chain = RAGPipeline("tvap")
#    print(chain.qa("Ab wann gelte ich arbeitnehmerähneliche Angestellte?"))