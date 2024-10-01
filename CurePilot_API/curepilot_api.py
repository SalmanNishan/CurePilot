from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
from pyserini.search.lucene import LuceneSearcher
from pymilvus import Collection, connections
import torch

from database_manager_curepilot import DatabaseManager
from unixcoder import UniXcoder

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import datetime
import uvicorn
import uuid
import os

# Configurations and constants
from config import *

# Function to initialize models
def initialize_models():
    tokenizer = AutoTokenizer.from_pretrained(LLM_Model, trust_remote_code=True)
    tokenizer.pad_token, tokenizer.padding_side = tokenizer.eos_token, "right"
    
    # Determine the compute dtype based on device capabilities
    use_4bit = True
    bnb_4bit_compute_dtype = torch.float16 if use_4bit and torch.cuda.get_device_capability()[0] >= 8 else torch.float32

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=use_4bit,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=bnb_4bit_compute_dtype,
        bnb_4bit_use_double_quant=False
    )
    
    mistral_model = AutoModelForCausalLM.from_pretrained(
        LLM_Model,
        quantization_config=bnb_config,
        device_map={"": 1}
    )
    
    device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    unix_model = UniXcoder(Unix_Model)
    unix_model = unix_model.to(device)
    
    return tokenizer, mistral_model, unix_model, device

# # Function to perform search using Lucene and Milvus
# def perform_search(query, unix_model, device):
#     searcher = LuceneSearcher(Lucene_Searcher)
#     hits = searcher.search(query)
#     doc_ids = [hit.docid.rstrip(".cs") for hit in hits]
    
#     tokens_ids = unix_model.tokenize([query], max_length=512, mode="<encoder-only>")
#     tokens_embeddings, query_embedding = unix_model(torch.tensor(tokens_ids).to(device))
#     norm_query_embedding = torch.nn.functional.normalize(query_embedding, p=2, dim=1)
    
#     connections.connect("default", host = Milvus_Host, port = Milvus_Port)
#     collection = Collection(name = Milvus_Collection)
    
#     search_params = {
#         "metric_type": "IP",
#         "params": {"nprobe": 10}
#     }
#     expr = "ID in [{}]".format(", ".join(f'"{id_}"' for id_ in doc_ids))
    
#     results = collection.search(
#         data=[norm_query_embedding.squeeze().tolist()],
#         anns_field="embedding",
#         param=search_params,
#         limit=5,
#         expr=expr
#     )
    
#     relevant_documents = []
#     for hits in results:
#         for hit in hits:
#             doc_id = hit.id
#             doc_content = collection.query(f'ID == "{doc_id}"', output_fields=['text_content'])
#             relevant_documents.append(doc_content)

#     # The relevant code snippet retrieved from the Milvus vector store
#     relevant_snippet = {}
#     relevant_snippet['1'] = relevant_documents[0][0]['text_content']
#     relevant_snippet['2'] = relevant_documents[1][0]['text_content']
#     relevant_snippet['3'] = relevant_documents[2][0]['text_content']
#     relevant_snippet['4'] = relevant_documents[3][0]['text_content']
#     relevant_snippet['5'] = relevant_documents[4][0]['text_content']


#     formatted_code_snippets = ""
#     for key, snippet in relevant_snippet.items():
#         formatted_code_snippets += f"Document {key}:\n{snippet}\n\n"

#     # The directory sources of the relevant code snippet files
#     sources = {}
#     sources['Source 1'] = relevant_documents[0][0]['ID']
#     sources['Source 2'] = relevant_documents[1][0]['ID']
#     sources['source 3'] = relevant_documents[2][0]['ID']
#     sources['source 4'] = relevant_documents[3][0]['ID']
#     sources['source 5'] = relevant_documents[4][0]['ID']

#     formatted_sources = ""
#     for key, id in sources.items():
#         formatted_sources += f"{key}: \n{id}\n\n"
    
#     return [formatted_code_snippets, formatted_sources]

# Function to perform search using Lucene and Milvus
def perform_search(query, unix_model, device):
    searcher = LuceneSearcher(Lucene_Searcher)
    hits = searcher.search(query)
    doc_ids = [hit.docid.rstrip(".cs") for hit in hits]
    
    tokens_ids = unix_model.tokenize([query], max_length=512, mode="<encoder-only>")
    tokens_embeddings, query_embedding = unix_model(torch.tensor(tokens_ids).to(device))
    norm_query_embedding = torch.nn.functional.normalize(query_embedding, p=2, dim=1)
    
    connections.connect("default", host=Milvus_Host, port=Milvus_Port)
    collection = Collection(name=Milvus_Collection)
    
    search_params = {
        "metric_type": "IP",
        "params": {"nprobe": 10}
    }
    expr = "ID in [{}]".format(", ".join(f'"{id_}"' for id_ in doc_ids))
    
    results = collection.search(
        data=[norm_query_embedding.squeeze().tolist()],
        anns_field="embedding",
        param=search_params,
        limit=5,
        expr=expr
    )
    
    relevant_documents = []
    for hits in results:
        for hit in hits:
            doc_id = hit.id
            doc_content = collection.query(f'ID == "{doc_id}"', output_fields=['text_content'])
            relevant_documents.append(doc_content)

    # Ensure there are enough relevant documents before accessing them
    relevant_snippet = {}
    for i in range(min(5, len(relevant_documents))):
        relevant_snippet[str(i+1)] = relevant_documents[i][0]['text_content']

    formatted_code_snippets = ""
    for key, snippet in relevant_snippet.items():
        formatted_code_snippets += f"Document {key}:\n{snippet}\n\n"

    # The directory sources of the relevant code snippet files
    sources = {}
    for i in range(min(5, len(relevant_documents))):
        sources[f'Source {i+1}'] = relevant_documents[i][0]['ID']

    formatted_sources = ""
    for key, id in sources.items():
        formatted_sources += f"{key}: \n{id}\n\n"
    
    return [formatted_code_snippets, formatted_sources]



# Function to generate response
def generate_response(prompt, mistral_model, tokenizer):
    generator = pipeline('text-generation', model=mistral_model, tokenizer=tokenizer)
    response = generator(prompt, max_new_tokens=500, num_return_sequences=1)
    return response[0]['generated_text']


def save_chat(db_manager, user_id, chat_id, date, prompt_id, message_1, message_2, message_3):
    db_manager.add_chat(user_id, chat_id, date, prompt_id, message_1, message_2, message_3)


tokenizer, mistral_model, unix_model, device = initialize_models()
db_manager = DatabaseManager()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    userId: str
    chatId: str
    prompt: str

@app.post("/start-chat")
def read_root(chat_request: ChatRequest):
    userId = chat_request.userId
    chatId = chat_request.chatId
    query = chat_request.prompt

    if not chatId:
        chatId =str(uuid.uuid4())

    promptId =str(uuid.uuid4())
    current_datetime = datetime.datetime.now()
    unix_date = int(current_datetime.timestamp())

    documents = perform_search(query, unix_model, device)
    prompt_user = System_Prompt.format(query, documents[0])
    generated_text = generate_response(prompt_user, mistral_model, tokenizer)
    ll_response = generated_text[len(prompt_user):].strip()

    save_chat(db_manager, userId, chatId, promptId, unix_date, query, ll_response, documents[1])
    return{"userId": userId, "chatId": chatId, "promptId": promptId, "date": unix_date, "prompt": query, "response": ll_response, "sources" : documents[1]}

@app.delete("/del-chat")
def del_chat(userId: str, chatId: str):
    db_manager.delete_chat(userId, chatId)
    return("chat deleted")

@app.get("/show-chat-history")
def show_history(userId: str, chatId: str):
    chat_hist = db_manager.get_chat(userId, chatId)
    return chat_hist

@app.get("/show-user-history")
def show_history(userId: str):
    user_hist = db_manager.get_chats(userId)
    return (user_hist)

# Run the server with `uvicorn filename:app --reload`;
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8020)