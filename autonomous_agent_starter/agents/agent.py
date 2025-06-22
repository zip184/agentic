import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()  # This will load the .env file

def run_agent(goal: str) -> str:
    llm = OpenAI(temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(input_variables=["goal"], template="Your goal is: {goal}")
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(goal)
