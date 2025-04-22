import openai

def analyze_position_with_gpt(position_text: str) -> str:
    """
    Делает запрос к GPT с описанием позиции и возвращает анализ/расшифровку.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты помощник по анализу описания оборудования для школ, расшифровываешь ТЗ."},
                {"role": "user", "content": f"Объясни, что означает: {position_text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT error: {e}"
