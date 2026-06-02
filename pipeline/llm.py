import os
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def generate_content(topic: str) -> str:
    """Generate a short article for the given topic using Groq."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a professional content writer."
            },
            {
                "role": "user",
                "content": f"""Write a concise, engaging 200-word article about: {topic}

Format:
- Start with a compelling headline
- 2-3 short paragraphs
- End with a key takeaway"""
            }
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def score_content(topic: str, content: str) -> dict:
    """Score generated content on clarity, engagement, and accuracy."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a content quality evaluator. Always respond with only a JSON object, no extra text."
            },
            {
                "role": "user",
                "content": f"""Score this article about '{topic}' on a scale of 1-10 for each:
- clarity: how clear and readable it is
- engagement: how interesting and compelling it is  
- accuracy: how factually sound it appears

Article:
{content}

Respond with only this JSON format:
{{"clarity": 8, "engagement": 7, "accuracy": 9, "overall": 8}}"""
            }
        ],
        max_tokens=100
    )
    import json
    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except:
        return {"clarity": 0, "engagement": 0, "accuracy": 0, "overall": 0}