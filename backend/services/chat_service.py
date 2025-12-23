from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import pandas as pd
from backend.core.settings import settings
from backend.services.file_service import get_retriever

# Initialize LLM
llm = ChatOpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL,
    model=settings.MODEL_NAME,
    temperature=0  # Temperature 0 is generally better for agents
)

class ChatService:
    @staticmethod
    def run_pandas_agent(file_path: str, message: str):
        """Run the Pandas DataFrame Agent on the given file."""
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            allow_dangerous_code=True,
            agent_type="openai-tools",
            return_intermediate_steps=True
        )
        
        response = agent.invoke({"input": message})
        
        # Format steps
        steps_log = []
        if "intermediate_steps" in response:
            for action, observation in response["intermediate_steps"]:
                steps_log.append({
                    "tool": action.tool,
                    "input": action.tool_input,
                    "log": action.log,
                    "output": str(observation)
                })

        return response["output"], steps_log

    @staticmethod
    def run_rag_chain(message: str):
        """Run the standard RAG chain using the vector store."""
        retriever = get_retriever()
        if not retriever:
            raise ValueError("Index not found. Please upload a document first.")
            
        prompt = ChatPromptTemplate.from_template("""
            Answer the following question based only on the provided context:

            <context>
            {context}
            </context>

            Question: {input}
        """)

        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        response = retrieval_chain.invoke({"input": message})
        return response["answer"]
