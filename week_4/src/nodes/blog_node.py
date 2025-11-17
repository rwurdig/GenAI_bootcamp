"""Blog generation nodes"""
from src.states.blogstate import BlogState


class BlogNode:
    """Handles blog title and content generation"""

    def __init__(self, llm):
        self.llm = llm

    def create_title(self, state: BlogState) -> dict:
        """Generate SEO-friendly blog title"""
        topic = state["topic"]
        language = state.get("language", "English")

        prompt = f"""Generate ONE creative, SEO-friendly blog title for the topic: "{topic}"

Requirements:
- Engaging and click-worthy
- 50-70 characters
- Language: {language}
- NO quotes or extra formatting

Title:"""

        response = self.llm.invoke(prompt)
        title = response.content.strip().strip('"').strip("'")

        return {"blog": {"title": title, "content": "", "language": language}}

    def generate_content(self, state: BlogState) -> dict:
        """Generate detailed blog content"""
        title = state["blog"]["title"]
        topic = state["topic"]
        language = state.get("language", "English")

        prompt = f"""Write a comprehensive blog post in {language} language.

Topic: {topic}
Title: {title}

Requirements:
1. 800-1200 words
2. Professional yet conversational tone
3. Well-structured with clear sections
4. Use Markdown formatting:
   - ## for main sections
   - ### for subsections
   - **bold** for emphasis
   - Bullet points where appropriate
5. Include actionable insights
6. Conclude with key takeaways
7. WRITE EVERYTHING IN {language}

Generate the complete blog content now:"""

        response = self.llm.invoke(prompt)
        content = response.content.strip()

        return {
            "blog": {
                "title": title,
                "content": content,
                "language": language,
            }
        }
