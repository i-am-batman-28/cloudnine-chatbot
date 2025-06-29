from typing import List, Dict, Optional
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
import sys

class RAGResponseGenerator:
    def __init__(self):
        load_dotenv()
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.index_name = 'cloudnine-hospital'
        self.embedding_model = 'sentence-transformers/all-MiniLM-L6-v2'

        # Initialize components
        self.embeddings = self._initialize_embeddings()
        self.retriever = self._initialize_retriever()
        self.llm = self._initialize_llm()
        self.qa_chain = self._initialize_qa_chain()

    def _initialize_embeddings(self) -> HuggingFaceEmbeddings:
        """Initialize HuggingFace embeddings"""
        try:
            return HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
            sys.exit(1)

    def _initialize_retriever(self):
        """Initialize Pinecone vector store and retriever"""
        try:
            docsearch = PineconeVectorStore.from_existing_index(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            return docsearch.as_retriever(search_type='similarity', search_kwargs={'k': 3})
        except Exception as e:
            print(f"Error connecting to Pinecone: {e}")
            sys.exit(1)

    def _initialize_llm(self):
        """Initialize Groq LLM"""
        try:
            return ChatGroq(api_key=self.groq_api_key, model_name='llama3-70b-8192')
        except Exception as e:
            print(f"Error initializing ChatGroq: {e}")
            sys.exit(1)

    def _initialize_qa_chain(self):
        """Initialize QA chain with custom prompt"""
        template = """
You are a helpful and empathetic medical assistant for CloudNine Hospitals. Follow these guidelines:

1. Be concise and clear, using complete sentences and proper formatting
2. Keep responses between 2-4 sentences for general inquiries
3. Use bullet points with seperate lines each for multiple items
4. Include relevant emojis to make the response engaging (max 2-3 emojis)
5. For medical advice or safety information, provide necessary detail while maintaining clarity
6. When scheduling appointments:
   - Acknowledge the request with a 👋 or 📅
   - Confirm specific details (date, time, doctor)
   - End with a clear next step

Context:
{context}

Question:
{question}

Answer:
"""

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )

        question_answer_chain = load_qa_chain(llm=self.llm, chain_type="stuff", prompt=prompt)
        return RetrievalQA(combine_documents_chain=question_answer_chain, retriever=self.retriever)

    def generate_response(self, query: str, context: Optional[Dict] = None,
                          conversation_history: Optional[List] = None) -> str:
        """Generate a response using RAG methodology"""
        try:
            context_str = ""

            # Handle recent conversation history
            if conversation_history and isinstance(conversation_history, list):
                recent_history = conversation_history[-3:]
                history_strings = [
                    f"User: {h['user']}\nAssistant: {h['assistant']}"
                    for h in recent_history
                    if isinstance(h, dict) and 'user' in h and 'assistant' in h
                ]
                if history_strings:
                    context_str += "Previous conversation:\n" + "\n".join(history_strings) + "\n\n"

            # Add user context
            if context and isinstance(context, dict):
                personal = context.get("personal", {})
                if personal:
                    context_str += "User Info:\n"
                    for key, value in personal.items():
                        context_str += f"{key}: {value}\n"
                    context_str += "\n"

            # Prepare final query with context
            enhanced_query = f"{context_str}Current question: {query}\n\nPlease provide a helpful and empathetic response based on the available context."

            # Run the QA chain
            response = self.qa_chain.run(enhanced_query)

            if not response:
                return "I apologize, but I couldn't generate a specific response. Could you please rephrase your question?"

            response = self._enhance_response_with_context(response, context)
            return self._format_response(response)

        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."

    def _format_response(self, response: str) -> str:
        """Format the response for better readability"""
        response = "\n".join(line for line in response.splitlines() if line.strip())

        for punct in ['.', '!', '?']:
            response = response.replace(f"{punct} ", f"{punct}\n")

        lines = response.split('\n')
        formatted_lines = [
            f"• {line[2:]}" if line.startswith("- ") else line
            for line in lines
        ]
        return "\n".join(formatted_lines)

    def _enhance_response_with_context(self, response: str, context: Optional[Dict]) -> str:
        """Add personalization and preferences"""
        enhanced_response = response

        if context:
            personal = context.get("personal", {})
            if 'name' in personal:
                enhanced_response = f"Hi {personal['name']}, {enhanced_response}"

            preferences = context.get("preferences", {})
            if 'department' in preferences:
                dept = preferences['department']
                enhanced_response += f"\n\nRegarding the {dept} department, let me know if you need specific info."

            if 'doctor' in preferences:
                doctor = preferences['doctor']
                enhanced_response += f"\n\nI can also help you book an appointment with Dr. {doctor}."

        return enhanced_response
