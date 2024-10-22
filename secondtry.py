import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
import time
import json
import streamlit as st
from openai.types.beta.threads.message_create_params import (
    Attachment,
    AttachmentToolFileSearch,
)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

load_dotenv(dotenv_path)
API_KEY= os.getenv('OPENAI_API_KEY')

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=API_KEY,
)
#delete threads
# client.beta.threads.delete('thread_vJUQagGARMrkLcvPJ2rT9lGG')


my_assistants = client.beta.assistants.list(
    order="desc",
    limit="20",
)
target_assistant_name = "Keya's Personal Assistant" #keya's personal assistant

# Check if the assistant exists
assistant_exists = False

if hasattr(my_assistants, 'data') and len(my_assistants.data) > 0:
    for assistant in my_assistants.data:
        if assistant.name == target_assistant_name:
            assistant_exists = True
            break

if assistant_exists:
    print(f"Assistant with name {target_assistant_name} exists.")
    assistant_id = assistant.id
 
else:
    print(f"Assistant with name {target_assistant_name} in creation.")
    # Create a vector store called "Keya's faxx that states dacts about keya"
    vector_store = client.beta.vector_stores.create(name="keya's faxx")

    # Create an assistant
    pdf_assistant = client.beta.assistants.create(
        name="Keya's Personal Assistant",
        instructions="You are Keya's personal Assistant. You only answer questions that are related to her, circle back to her if asked any questions that doesnt concern her.",
        model="gpt-4-1106-preview",
        tools=[{"type": "file_search"}],)

    assistant = client.beta.assistants.update(
    assistant_id= pdf_assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )
    # Ready the files for upload to OpenAI
    file_paths = ["KeyaBiodata.pdf", "KeyaResume.docx"]
    file_streams = [open(path, "rb") for path in file_paths]
    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
      vector_store_id=vector_store.id, files=file_streams
    )
    print(f"Assistant:Keya's Personal Assistant created.")

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.getenv('OPENAI_API_KEY'),
)

def chat(thread_id):
    # user_messages = []
    print("Chat with the bot! Type 'exit' to stop.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        # user_messages.append({"role": "user", "content": user_input})
        
        bot_response = get_response(user_input, thread_id)
       
        print(bot_response)

        

def get_response(user_input, thread_id):
    
    # print("thread id in get_response", thread_id)
    # exit
    assistant_response = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        bot_output = messages.data[0].content[0].text.value
        return bot_output
    else:
        print(run.status)
        exit

if __name__ == "__main__":

    thread = client.beta.threads.create()
    chat(thread.id)