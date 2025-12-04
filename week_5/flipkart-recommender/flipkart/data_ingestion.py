import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from flipkart.data_converter import DataConverter
from flipkart.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class DataIngestor:
    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
        self.persist_dir = Config.CHROMA_PERSIST_DIR
        self.collection_name = Config.COLLECTION_NAME

    def ingest(self, load_existing=True):
        """Load existing vector store or create new one"""
        try:
            if load_existing and os.path.exists(self.persist_dir):
                logger.info("Loading existing vector store...")
                vstore = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embedding,
                    collection_name=self.collection_name
                )
                # Check if collection has documents
                if vstore._collection.count() > 0:
                    logger.info(f"Loaded {vstore._collection.count()} documents from existing store")
                    return vstore
                logger.info("Existing store is empty, will create sample data")
            
            # Create sample product data if no data file exists
            logger.info("Creating vector store with sample data...")
            sample_docs = self._create_sample_products()
            
            vstore = Chroma.from_documents(
                documents=sample_docs,
                embedding=self.embedding,
                persist_directory=self.persist_dir,
                collection_name=self.collection_name
            )
            
            logger.info(f"Created vector store with {len(sample_docs)} products")
            return vstore
            
        except Exception as e:
            logger.error(f"Error in data ingestion: {e}")
            raise

    def _create_sample_products(self):
        """Create sample product documents for demo"""
        from langchain_core.documents import Document
        
        products = [
            {
                "name": "iPhone 15 Pro Max",
                "category": "Smartphones",
                "price": "₹159,900",
                "review": "Amazing phone with excellent camera quality. The titanium design feels premium. A17 Pro chip is blazing fast. Best iPhone ever!",
                "rating": "4.8"
            },
            {
                "name": "Samsung Galaxy S24 Ultra",
                "category": "Smartphones",
                "price": "₹134,999",
                "review": "Galaxy AI features are revolutionary. The 200MP camera takes stunning photos. S Pen is super useful. Great battery life!",
                "rating": "4.7"
            },
            {
                "name": "Sony WH-1000XM5",
                "category": "Headphones",
                "price": "₹29,990",
                "review": "Best noise cancellation I've ever experienced. Sound quality is phenomenal. 30-hour battery is incredible. Very comfortable for long use.",
                "rating": "4.9"
            },
            {
                "name": "MacBook Air M3",
                "category": "Laptops",
                "price": "₹114,900",
                "review": "Incredible performance with M3 chip. Silent operation, no fan noise. All-day battery life. Perfect for professionals and students.",
                "rating": "4.8"
            },
            {
                "name": "Dell XPS 15",
                "category": "Laptops",
                "price": "₹149,990",
                "review": "Stunning OLED display with vibrant colors. Intel Core i7 handles everything smoothly. RTX graphics great for content creation.",
                "rating": "4.6"
            },
            {
                "name": "Apple Watch Series 9",
                "category": "Smartwatches",
                "price": "₹41,900",
                "review": "Double tap gesture is game-changing. Health tracking is comprehensive. Seamless iPhone integration. Beautiful always-on display.",
                "rating": "4.7"
            },
            {
                "name": "Samsung 65-inch Neo QLED 4K TV",
                "category": "TVs",
                "price": "₹164,990",
                "review": "Picture quality is breathtaking with Neo QLED. Gaming Hub is perfect for gamers. Smart features work flawlessly. Great for movies!",
                "rating": "4.8"
            },
            {
                "name": "Dyson V15 Detect",
                "category": "Home Appliances",
                "price": "₹62,900",
                "review": "Laser dust detection is amazing! Can see all the dust you're cleaning. Powerful suction, long battery life. Worth every penny.",
                "rating": "4.7"
            },
            {
                "name": "PlayStation 5",
                "category": "Gaming",
                "price": "₹49,990",
                "review": "Next-gen gaming at its finest. DualSense controller haptics are incredible. Load times are almost instant. Great game library!",
                "rating": "4.9"
            },
            {
                "name": "Kindle Paperwhite",
                "category": "E-Readers",
                "price": "₹16,999",
                "review": "Perfect e-reader experience. Adjustable warm light is easy on eyes. Waterproof design great for pool/beach. Battery lasts weeks!",
                "rating": "4.8"
            },
            {
                "name": "Bose QuietComfort Ultra Earbuds",
                "category": "Earbuds",
                "price": "₹29,900",
                "review": "Immersive audio experience like no other. Noise cancellation rivals over-ear headphones. Comfortable fit. Premium sound quality.",
                "rating": "4.6"
            },
            {
                "name": "GoPro HERO12 Black",
                "category": "Cameras",
                "price": "₹44,990",
                "review": "Best action camera available. 5.3K video is stunning. HyperSmooth stabilization is magical. Waterproof and rugged design.",
                "rating": "4.7"
            },
            {
                "name": "OnePlus 12",
                "category": "Smartphones",
                "price": "₹64,999",
                "review": "Flagship killer with Snapdragon 8 Gen 3. 100W fast charging is insane. Great camera with Hasselblad tuning. Smooth 120Hz display.",
                "rating": "4.6"
            },
            {
                "name": "LG C3 55-inch OLED TV",
                "category": "TVs",
                "price": "₹139,990",
                "review": "Perfect blacks with OLED technology. Dolby Vision and Atmos support. webOS is user-friendly. Best TV for movie lovers!",
                "rating": "4.8"
            },
            {
                "name": "Xiaomi Robot Vacuum X10+",
                "category": "Home Appliances",
                "price": "₹39,999",
                "review": "Cleans autonomously and efficiently. Self-emptying dock is convenient. LiDAR navigation avoids obstacles well. Great value for money.",
                "rating": "4.5"
            }
        ]
        
        docs = []
        for p in products:
            content = f"Product: {p['name']}\nCategory: {p['category']}\nPrice: {p['price']}\nRating: {p['rating']}/5\nReview: {p['review']}"
            docs.append(Document(
                page_content=content,
                metadata={"product_name": p['name'], "category": p['category'], "price": p['price']}
            ))
        
        return docs
