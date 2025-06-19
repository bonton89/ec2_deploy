import json
import boto3
import os
## We will be suing Titan Embeddings Model To generate Embedding
#from langchain_community.embeddings import BedrockEmbeddings
from langchain_aws import BedrockEmbeddings
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
## Data Ingestion
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.document_loaders import PyPDFLoader


#Vector Embedding And Vector Store

from langchain_community.vectorstores import FAISS

## LLm Models
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# ## Bedrock Clients
# bedrock=boto3.client(
#             service_name="bedrock-runtime",
#             region_name="us-east-1",
#             aws_access_key_id=os.getenv('aws_access_key_id'),  # Add access key
#             aws_secret_access_key=os.getenv('aws_secret_access_key')  # Add secret key
#             )
# bedrock_embeddings=BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0",client=bedrock)

## Bedrock Clients
bedrock=boto3.client(service_name="bedrock-runtime")
bedrock_embeddings=BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0",client=bedrock)

## Data ingestion
def data_ingestion(file_path):
    # loader=PyPDFDirectoryLoader("data")
    loader = PyPDFLoader(file_path)
    documents=loader.load()
    # Clean up the temporary file
    os.unlink(file_path)

    # - in our testing Character split works better with this PDF data set
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=10000,
                                                 chunk_overlap=1000)
    
    docs=text_splitter.split_documents(documents)
    return docs

## Vector Embedding and vector store
def get_vector_store(docs):
    vectorstore_faiss=FAISS.from_documents(
        docs,
        bedrock_embeddings
    )
    vectorstore_faiss.save_local("faiss_index")

prompt_template = """

Human: 
 - You are a specialized document analysis assistant for plans.
 - Analyze the provided context carefully to answer the question with precision.
 - Use logical reasoning and focus only on information explicitly present in the context.
 - If you are checking any information related to years or dates, ensure you check for anniversary or specific years mentioned in the context.
 - If the answer cannot be determined from the context, state "Information not available in provided context" rather than guessing.

- Your response must follow this exact structure:
    1. Direct Answer: Provide the most concise accurate answer (1-3 words maximum)
    2. Confidence: Rate your confidence from 0-100% based on how clearly the information is stated in the context
    3. Source: Cite the specific section or paragraph number where the information was found
    4. Explanation: A brief explanation (2-3 sentences maximum) clarifying your answer if needed

- YOUR RESPONSE MUST BE VALID JSON following this exact structure:

```json
{{
  "direct_answer": "Concise answer (1-3 words)",
  "confidence": 85,
  "source": "Section X, Paragraph Y",
  "explanation": "Brief explanation of your answer based on the context"
}}


<context>
{context}
</context>

Remember: Respond ONLY with valid JSON matching the structure above. No additional text before or after the JSON.

Question: {question}

Assistant:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

def get_response_llm(llm2,vectorstore_faiss,query):
    qa = RetrievalQA.from_chain_type(
    llm=llm2,
    chain_type="stuff",
    retriever=vectorstore_faiss.as_retriever(search_type="similarity", search_kwargs={"k": 3}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT},
    input_key="question"
    )
    answer=qa.invoke({"question":query})
    # answer=qa({"query":query})

    try:
        # json_result = json.loads(answer['result'])
        json_result=parse_llm_response(answer['result'])
        return json_result
    except json.JSONDecodeError:
        # If the result isn't valid JSON, return the raw result
        print("Warning: Response is not valid JSON. Returning raw response.")
        return answer['result']
    
def parse_llm_response(response):
    # If already a dictionary, return as is
    if isinstance(response, dict):
        return response
    # If response is a string, try to clean it
    if isinstance(response, str):
        # Remove Markdown code block if present
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "")
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        # Try to parse JSON
        try:
            return json.loads(cleaned)
        except Exception as e:
            raise ValueError(f"Could not parse response: {e}\nContent: {cleaned}")
        
def create_doc_chunk(file_path):
     # Data injestion
    docs = data_ingestion(file_path)
    # DO vector embedding and store it in local index
    get_vector_store(docs)
    # Loading local index where the embeddings is present
    faiss_index = FAISS.load_local(
        "faiss_index", 
        bedrock_embeddings, 
        allow_dangerous_deserialization=True
    )
    return faiss_index

def call_bedrock(faiss_index, user_question):
    # 4. Load Chat LLM for Nova Micro
    llm2 = ChatBedrock(
        model_id="eu.amazon.nova-micro-v1:0",
        client=bedrock,
    )
    resp=get_response_llm(llm2, faiss_index, user_question)
    return resp
