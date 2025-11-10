from typing import Optional
import trafilatura
from newspaper import Article

def fetch_article(url: str) -> Optional[str]:
    """Try Trafilatura first, fallback to newspaper3k."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            if text and len(text.strip()) > 300:
                return text
    except Exception:
        pass

    try:
        art = Article(url)
        art.download()
        art.parse()
        return art.text
    except Exception:
        return None