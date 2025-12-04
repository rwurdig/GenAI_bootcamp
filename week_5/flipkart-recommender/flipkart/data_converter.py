import pandas as pd
from langchain_core.documents import Document

class DataConverter:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def convert(self):
        """Convert CSV data to LangChain documents"""
        df = pd.read_csv(self.file_path)
        
        # Check for available columns and use appropriate ones
        if "product_title" in df.columns and "review" in df.columns:
            docs = [
                Document(
                    page_content=row['review'], 
                    metadata={"product_name": row["product_title"]}
                )
                for _, row in df.iterrows() if pd.notna(row['review'])
            ]
        elif "name" in df.columns and "description" in df.columns:
            docs = [
                Document(
                    page_content=f"{row['name']}: {row['description']}", 
                    metadata={"product_name": row["name"]}
                )
                for _, row in df.iterrows() if pd.notna(row['description'])
            ]
        else:
            # Fallback: use all text columns
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
            docs = [
                Document(
                    page_content=" | ".join([str(row[col]) for col in text_cols if pd.notna(row[col])]),
                    metadata={"row_id": str(idx)}
                )
                for idx, row in df.iterrows()
            ]
        
        return docs
