"""LangGraph workflow builder"""
from langgraph.graph import END, START, StateGraph

from src.nodes.blog_node import BlogNode
from src.states.blogstate import BlogState


class GraphBuilder:
    """Builds the blog generation workflow"""

    def __init__(self, llm):
        self.llm = llm
        self.blog_node = BlogNode(llm)
        self.graph = StateGraph(BlogState)

    def build(self):
        """Build the state graph"""
        self.graph.add_node("create_title", self.blog_node.create_title)
        self.graph.add_node("generate_content", self.blog_node.generate_content)

        self.graph.add_edge(START, "create_title")
        self.graph.add_edge("create_title", "generate_content")
        self.graph.add_edge("generate_content", END)

        return self.graph.compile()
