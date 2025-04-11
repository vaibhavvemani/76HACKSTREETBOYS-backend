from groq import Groq
import json
def llm_based_match(query):
    prompt = f"""
        You are a finance assistant. A user asked: "{query}"

        Return the most relevant fund ticker. 
        Prioritize replying with a ticker if exists for the company or fund.
        If no specific fund is mentioned, return a sector name instead.

        Only respond with the ticker or company name,
        do not include the company or fund name.

        Choose the most relavent match even if a company has many
        Respond strictly in this JSON format:
        {{
            "type": "fund" or "sector",
            "value": "ticker or sector name"
        }}
    """
    client = Groq(
        api_key = "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"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    message = (chat_completion.choices[0].message.content)
    parsed_content = json.loads(message)
    return parsed_content["value"]
