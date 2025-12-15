MULTIPLE_CHOICE_PROMPT = """
You generate high quality multiple choice quiz questions.

Topic or context:
{topic}

Rules:
1. Generate exactly {num_questions} questions.
2. Each question must have exactly 4 options.
3. The answer must be exactly one of the options.
4. Keep questions clear and unambiguous.
5. Return only valid JSON that matches this schema.

Schema:
{schema}
"""

OPEN_ENDED_PROMPT = """
You generate high quality open ended quiz questions.

Topic or context:
{topic}

Rules:
1. Generate exactly {num_questions} questions.
2. Provide a short correct answer for each question.
3. Keep questions clear and unambiguous.
4. Return only valid JSON that matches this schema.

Schema:
{schema}
"""
