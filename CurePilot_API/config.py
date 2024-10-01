LLM_Model = '/mnt/sda/Mistral_v0.2/'
Lucene_Searcher = '/mnt/nvme1n1/Aamir/Data/indices/PreAuth/'
Unix_Model = "microsoft/unixcoder-base-nine"
Milvus_Host = "127.0.0.1"
Milvus_Port = "19530"
Milvus_Collection = "PreAuth"
System_Prompt = """You are an expert in c# code explanation. Please answer the Question as thoroughly and accurately as possible using the 
c# code provided under the code snippet heading. Every Code snippet contains two classes which start with "Document:", only use
the class that is indicated in the Question. Only use the code provided in the code snippet and don't answer the quesion based on any other 
knowledge.

Question: 
{}
Code Snippet:
{}

Response:
"""