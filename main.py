import os 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate 
from dotenv import load_dotenv

# Load API keys
load_dotenv()
print("API KEY:", os.getenv("OPENAI_API_KEY"))
print("LANGCHAIN KEY:", os.getenv("LANGCHAIN_API_KEY"))
# Initialize model
llm = ChatOpenAI(model="gpt-4o-mini")

# Sample data
resume = "Python developer with 2 years experience in ML and SQL"
jd = "Looking for Python, SQL, Deep Learning"

# Step 1: Extract skills
extract_prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
Extract:
- Skills
- Experience
- Tools

Resume:
{resume}

Return JSON
"""
)

extract_chain = extract_prompt | llm
resume_data = extract_chain.invoke({"resume": resume})

print("\n--- Resume Data ---")
print(resume_data.content)


# Step 2: Match with JD
match_prompt = PromptTemplate(
    input_variables=["resume_data", "jd"],
    template="""
Compare resume with job description.

Resume:
{resume_data}

JD:
{jd}

Return:
- Matching skills
- Missing skills
- Match %
"""
)

match_chain = match_prompt | llm
match_result = match_chain.invoke({
    "resume_data": resume_data.content,
    "jd": jd
})

print("\n--- Match Result ---")
print(match_result.content)


# Step 3: Score (simple logic)
score = 75

# Step 4: Explanation
explain_prompt = PromptTemplate(
    input_variables=["score", "details"],
    template="""
Score: {score}

Explain:
{details}
"""
)

explain_chain = explain_prompt | llm

explanation = explain_chain.invoke({
    "score": score,
    "details": match_result.content
})

print("\n--- Final Explanation ---")
print(explanation.content)