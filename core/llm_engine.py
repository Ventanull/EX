import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

def generate_cold_email(domain: str, vulnerabilities: list) -> str:
    """Generate a concise, hyper‑personalized cold email for the given domain.
    Uses OpenAI's gpt‑4o‑mini model via LangChain.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "ERROR: OPENAI_API_KEY missing from environment."

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6, openai_api_key=api_key)

    template = """
You are a technical web‑infrastructure specialist. Write a highly personalized, concise cold email to the owner of {domain}.

During a routine sweep, we found the following technical vulnerabilities bleeding revenue on their site:
{vuln_list}

Goal: Pitch a quick 10‑minute audit call with our web development agency partner to patch these and capture lost leads.
Rules: Keep it under 100 words. No fluff. Direct, technical, and value‑driven. Provide the Subject Line and the Body.

Subject:
Body:
"""
    prompt = PromptTemplate(input_variables=["domain", "vuln_list"], template=template)
    formatted = prompt.format(domain=domain, vuln_list="\n- ".join(vulnerabilities))
    response = llm.invoke(formatted)
    return response.content

