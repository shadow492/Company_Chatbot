

from uuid import UUID
import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import ChatMessage
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
import os
from langchain import PromptTemplate,LLMChain
from langchain.chains import ConversationChain
import requests
from langchain_community.utilities import SerpAPIWrapper
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain import hub

import getpass
import os


st.set_page_config(page_title="Work Assist")
st.header("Welcome to Work Assist, your intelligent Enterprise Assistant")

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

system = '''Respond to the human as helpfully and accurately as possible. You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format and donot iterate too much over a topic have little urgency in answering the question:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}

Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation'''

human = '''{input}

{agent_scratchpad}

(reminder to respond in a JSON blob no matter what)'''

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human),
    ]
)

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
api_key = "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"
HugginngFaceAPI = api_key




if HugginngFaceAPI:
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

    llm = HuggingFaceEndpoint(
            repo_id="HuggingFaceH4/zephyr-7b-beta",
            task="text-generation",
            max_new_tokens=512,
            do_sample=False,
            repetition_penalty=1.03,
            huggingfacehub_api_token="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"

    )

    memory = ConversationBufferMemory(memory_key='chat_history',
                                  return_messages=False,
                                  output_key="output")


    from langchain.agents import AgentType,initialize_agent
    from langchain.tools import StructuredTool, Tool,tool,BaseTool
    from langchain.agents.agent_toolkits import create_retriever_tool
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import ChatMessage
    from langchain.prompts import load_prompt

    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    class StreamHandler(BaseCallbackHandler):
        def __init__(self,container,initial_text=""):
            self.container = container
            self.text = initial_text
        def on_llm_new_token(self, token: str,**kwargs) -> None:
            self.text +=token
            self.container.markdown(self.text)

    tools = []

    

    agent = create_structured_chat_agent(llm, tools,prompt=prompt)
    agent_executor = AgentExecutor(agent=agent,tools=tools,memory_key="chat_history",verbose=True,return_only_output=True,handle_parsing_errors=True,early_stopping_method='generate')

    #bad language filtering
    import re
    import pandas as pd

    # Define dataset paths
    dataset_en = 'https://raw.githubusercontent.com/shadow492/Company_Chatbot/main/en.txt?token=GHSAT0AAAAAACXDNKR66RHWGC7ZNKRKPOEQZW2V6EA'
    dataset_hi = 'https://raw.githubusercontent.com/shadow492/Company_Chatbot/main/hi.txt?token=GHSAT0AAAAAACXDNKR7DDYGGW675P3EZULGZW2WAKQ'

    # Load and combine datasets
    df_en = pd.read_csv(dataset_en)
    df_hi = pd.read_csv(dataset_hi)

    # Convert to string and handle missing values
    df_en['Column_1'] = df_en['Column_1'].astype(str).str.lower().str.strip()
    df_hi['Column_1'] = df_hi['aand'].astype(str).str.lower().str.strip()

    # Combine dataframes
    df_result = pd.concat([df_en, df_hi], ignore_index=True)

    # Create a set of bad words
    bad_words = set(df_result['Column_1'])

    def preprocess_text(text):
        # Convert to lowercase and remove punctuation
        return re.sub(r'[^\w\s]', '', text.lower())

    def contains_bad_language(statement, bad_words):
        # Check if the statement contains any bad words
        processed_statement = preprocess_text(statement)
        return any(bad_word in processed_statement for bad_word in bad_words)

    def filter_statements(statements, bad_words):
        filtered_statements = []
        for statement in statements:
            if not contains_bad_language(statement, bad_words):
                filtered_statements.append(statement)
            else:
                filtered_statements.append("This statement has been filtered due to inappropriate content. Please Use Proper Language.")
        return filtered_statements

    # Example usage
    # user inp into input_text var

    if "messages" not in st.session_state:
        st.session_state["messages"] = [ChatMessage(role= "assistant", content= "How can I help you?")]

    if "memory" not in st.session_state:
        st.session_state['memory'] = memory

    for message in st.session_state["messages"]:
        st.chat_message(message.role).write(message.content)


    if prompt := st.chat_input():

        input_text = prompt
        statements = [s.strip() for s in input_text.split('.') if s.strip()]
        filtered_statements = filter_statements(statements, bad_words)
        bad_prompt = '. '.join(filtered_statements)

        st.session_state.messages.append(ChatMessage(role="user", content=prompt))
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container())
            Stream_handler = StreamHandler(st.empty())
            response = agent_executor.invoke({"input":st.session_state.messages},return_only_outputs=True,)
            if isinstance(response, dict):
                content = response.get('output', str(response))
            else:
                content = str(response)
            if bad_prompt == "This statement has been filtered due to inappropriate content. Please Use Proper Language.":
                st.session_state.messages.append(ChatMessage(role="assistant", content= response.get("output")))
                st.write("Query removed, contains offensive and abusive words(Bad Language)")
              

            else:
                st.session_state.messages.append(ChatMessage(role="assistant", content= response.get("output")))
                st.write(response.get("output"))
