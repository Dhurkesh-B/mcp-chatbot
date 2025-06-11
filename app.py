import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from mcp_integration import MCPIntegration
from rag_integration import RAGIntegration

try:
    # Streamlit page config
    st.set_page_config(
        page_title="Dhurkesh B",
        page_icon="favicon.ico",
        layout="centered",
        initial_sidebar_state="auto",
    )

    # Load environment variables
    load_dotenv()

    # Initialize integrations
    mcp = MCPIntegration()
    rag = RAGIntegration()

    # Set up Groq LLM
    llm = ChatGroq(
        model_name="llama3-70b-8192",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ('system', '''Hi! I'm Dhurkesh's personal assistant. I have access to his information and can help answer questions about him.

            Here's what I know about Dhurkesh:
            {rag_data}

            Additional Information:
            {mcp_data}
            
            I can help you with:
            - Information about Dhurkesh's background and experience
            - Details about his projects and work
            - Any other questions you might have about him
            
            Please feel free to ask your question, and I'll provide a helpful response based on the available information.'''),
            ('human', 'Question: {question}')
        ]
    )

    def fetch_data_from_file(file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        else:
            st.error(f"File not found: {file_path}")
            return None

    st.title('Hello Friends👋')

    # Get combined context from all sources
    mcp_context = mcp.get_combined_context()
    rag_context = rag.get_context()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt_text := st.chat_input("Ask your question"):
        st.session_state.messages.append({"role": "user", "content": prompt_text})

        with st.chat_message("user"):
            st.markdown(prompt_text)

        # Search RAG content for relevant information
        rag_search = rag.search_content(prompt_text)
        rag_data = rag_search["content"] if rag_search["found"] else "No specific information found in the records."

        # Process the query with combined context
        output_parse = StrOutputParser()
        chain = prompt_template | llm | output_parse
        response = chain.invoke({
            'question': prompt_text,
            'mcp_data': mcp_context,
            'rag_data': rag_data
        })

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

except Exception as e:
    st.error(f"Error occurred: {e}") 