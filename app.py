import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine ## help to map the output coming from sql database
import sqlite3
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase


import os
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(page_title = "Langchain: Chat with SQL DB", page_icon = "🦜")
st.title("🦜 Langchain: Chat with SQL DB")

# INJECTION_WARNING = """ 
  #                   SQL agent can be vulnerable to prompt injection. Use a DB with limited privileges
#"""


LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQlite3 Database- Student.db", "Connect to you SQL Database"]

selected_opt = st.sidebar.radio (label = "Choose the DB which you want to chat to",
                 options = radio_opt,
                 
)

if radio_opt.index(selected_opt) == 1: #index start from 0 
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type = "password")
    mysql_db = st.sidebar.text_input("MySQL Database")

else:
    db_uri=LOCALDB


api_key = st.sidebar.text_input(label = "Groq API Key", type = "password")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please enter the Groq API Key")


## LLM Model

llm=ChatGroq(groq_api_key = api_key, model_name ="Llama3-8b-8192", streaming = True)


### Connecting to Database

@st.cache_resource(ttl ="2h")
def configure_db(db_uri, mysql_host = None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:

        # db_engine = create_engine('sqlite:///student.db')
        db_file_path = (Path(__file__).parent/"students.db").absolute()
        print(db_file_path)

        creator = lambda : sqlite3.connect(f"file:{db_file_path}? mode =ro", uri=True)

        return SQLDatabase(create_engine("sqlite:///", creator=creator))

    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):

            st.error("Please specify all the MySQL connection details")
            st.stop()  

        return SQLDatabase(create_engine(f'mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}')) 

   # else:
        #db_engine = create_engine(f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}')

if db_uri == MYSQL:
    db = configure_db(
    db_uri,
    mysql_host,
    mysql_password,
    mysql_db
    )
else:
    db = configure_db(db_uri)


## Now we develop Toolkit (llm model will craete a query and interact with the database (work of toolkit))



toolkit = SQLDatabaseToolkit(db = db, llm = llm)

agent = create_sql_agent(
    llm = llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)


# For Chat history  (chat history management and interaction flow in a Streamlit app)

if "messages" not in st.session_state or st.sidebar.button("Clear message hsitory"):
        st.session_state["messages"] = [

            {
                "role": "assistant", "content": "Hi! How can I help you?"
            },
        ]



for msg in st.session_state.messages:
    st.chat_message (
        msg["role"]).write(msg['content']
        
    )
      

user_query = st.chat_input(placeholder="Ask anything from the database")


if user_query:
    st.session_state.messages.append(
        {
            "role": "user", "content": user_query
        }  
    )

    st.chat_message("user").write(user_query)

    ## To display the chain of thoughts
    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(
            st.container(),
            # expand_new_thoughts= False
            )

        response = agent.run(
            user_query,
            callbacks=[streamlit_callback]
            ) 

        st.session_state.messages.append(
            {
                "role": "assistant", "content": response
            }
            )
        st.write(response)

        