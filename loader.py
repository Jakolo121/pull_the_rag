from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAIEmbeddings
import os
import re
import time
import logging

from pinecone import Pinecone, ServerlessSpec

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/dataloader.log"),
        logging.StreamHandler()
    ]       
)

load_dotenv(find_dotenv())

def extract_index_name(file_path):
    pattern = r'/([^/]+)\.\w+$'
    match = re.search(pattern, file_path)
    
    if match:
        return match.group(1).lower()
    else:
        raise ValueError(f"No valid filename found in {file_path}")
    
class DataLoader:
    def __init__(self,file_path):
        self.vectorstore_index_name = extract_index_name(file_path)
        logging.info("Extracted index name: %s", self.vectorstore_index_name)
        
        self.loader = PyMuPDFLoader(file_path=file_path)
        self.embeddings = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-3-small"
        )
        logging.info("Initialized OpenAI Embeddings with model: %s", self.embeddings.model)
        
        self.text_splitter =  RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=100
        )
        self.pcvs = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))    
        self.config = ServerlessSpec(cloud="aws", region="us-east-1")
        
        try:
            if self.vectorstore_index_name in [index.name for index in self.pcvs.list_indexes()]:
                logging.error("Already created an Index with the name %s", self.vectorstore_index_name)
            else:
                logging.info("Creating Pinecone index %s", self.vectorstore_index_name)
                self.pcvs.create_index(
                    self.vectorstore_index_name,
                    dimension=1536,
                    metric="cosine",
                    spec=self.config
                )
                while not self.pcvs.describe_index(self.vectorstore_index_name).status["ready"]:
                    logging.info("Wait for the Index to be created...")
                    time.sleep(1)
                logging.info("Pinecone Vectorstore %s is ready", self.vectorstore_index_name)
        except Exception as e:
            logging.error(f"Error creating Pinecone Vectorstore: {e}")
            
        # Initialize the VectorStore after creating the index if it doesn't already exist
        self.vectorstore = PineconeVectorStore(
            index_name=self.vectorstore_index_name,
            embedding=self.embeddings,
            pinecone_api_key=os.getenv("PINECONE_API_KEY")
        )
        logging.info("Pinecone Vectorstore initialized with index name: %s", self.vectorstore_index_name)
          
    def load_docs_into_pcvs(self):
            self.docs = []
            try:
                logging.info("Loading Documents into Pincone Index")
                for doc in self.loader.lazy_load():
                    self.docs.append(doc)
                    logging.info(f"Loaded {len(self.docs)} documents")
                self.split_docs = self.text_splitter.split_documents(self.docs)
                logging.info(f"Splitted docuemts into {len(self.split_docs)} smaller documents.")
                self.vectorstore.add_documents(self.split_docs)
                logging.info("Documents added to the Vectorstore")
            except Exception as e:
                logging.error(f"An error occurred while loading documents: {e}")

if __name__=="__main__":
    try:
        loader= DataLoader("./TVaP.pdf")
        loader.load_docs_into_pcvs()
    except Exception as e:
        logging.error(f"An error occurred:{e}")