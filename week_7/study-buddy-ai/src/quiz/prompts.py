# quiz generation prompts

MCQ_PROMPT = """Generate {num_questions} multiple choice questions about:
{topic}

Rules:
- 4 options per question
- Answer must be one of the options
- Clear, unambiguous questions
- Return valid JSON only

Schema:
{schema}"""

OPEN_PROMPT = """Generate {num_questions} open-ended questions about:
{topic}

Rules:
- Short correct answer for each
- Clear, unambiguous questions  
- Return valid JSON only

Schema:
{schema}"""
