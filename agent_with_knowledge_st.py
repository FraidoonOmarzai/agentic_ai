import streamlit as st
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector

# Database URL
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Initialize Knowledge Base
knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    vector_db=PgVector(table_name="recipes", db_url=db_url)
)

# Load the knowledge base (only needed for the first run)
knowledge_base.load()

# Initialize the Agent
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge_base,
    read_chat_history=True,
    show_tool_calls=True,
    markdown=True,
)

# Streamlit UI
st.title("Recipe Assistant")
st.write("Ask me about recipes from the knowledge base!")

# User input
user_input = st.text_input("Enter your question:")
if st.button("Ask") and user_input:
    response = agent.run(user_input)
    st.write(response)