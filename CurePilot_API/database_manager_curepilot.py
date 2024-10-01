from pymongo import MongoClient
 
class DatabaseManager:
    def __init__(self):
        self.connection = MongoClient("mongodb://localhost:27017")
        self.db = self.connection['CurePilot']
        self.collection = self.db['CurePilot']
 
    def add_chat(self, user_id, chat_id, prompt_id, date, new_chat_message_1, new_chat_message_2, new_chat_message_3):
        # Define the filter for finding the existing document with the given user_id and chat_id
        filter = {"userId": user_id, "chatId": chat_id}
 
        # Check if a document with the given user_id and chat_id already exists
        existing_document = self.collection.find_one(filter)

        # Append the new chat message to the existing 'chat' list
        update_data = {
            "chatId": chat_id,
            "promptId": prompt_id,
            "promptDate": date,
            "prompt": new_chat_message_1,
            "response": new_chat_message_2,
            "sources": new_chat_message_3
        }
        
        if existing_document:
            self.collection.update_one(filter, {"$push": {"All_Chat_Data": update_data}})
            
        else:
            # Create a new document with user_id, chat_id, and a new 'chat' list containing the new_chat_message
            new_document = {
                "userId": user_id,
                "chatId": chat_id,
                "promptId": prompt_id,
                "date": date,
                "topic": new_chat_message_1[:40],
                "prompt": new_chat_message_1, 
                "response": new_chat_message_2, 
                "sources": new_chat_message_3,
                "All_Chat_Data": [update_data]
            }
            self.collection.insert_one(new_document)
 
    def get_chat(self, user_id, chat_id):
        chat = self.collection.find_one({"userId": user_id, "chatId": chat_id})
        if chat:
            return chat["All_Chat_Data"]
        else:
            return []
       
    def delete_chat(self, user_id, chat_id):
        self.collection.delete_one({"userId": user_id, "chatId": chat_id})
 
    def get_chats(self, user_id):
        result = self.collection.find(
                        { "userId": user_id },
                        { "userId":1, "chatId": 1, "topic": 1, "date": 1, "_id": 0}
                    )
        user_hist =  list(result)
        return user_hist