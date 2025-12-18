---
title: SuperTech Store Customer Support
emoji: "🛍️"
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---
# SuperTech Store Customer Support Chatbot

AI-powered customer support chatbot for SuperTech Store, a computer products retailer.

##  Project Overview

This is Week 8 deliverable for the Andela GenAI Bootcamp - MCP Assessment.

**Task:** Build a Customer Support chatbot prototype that integrates with an MCP server.

##  Features

-  Natural language chat interface
-  Order tracking and status
-  Product catalog browsing
-  Product search
-  Customer verification (email + PIN)
-  Return policy information
-  Quick action buttons for common tasks

##  Tech Stack

- **LLM:** Groq (Llama 3.1 8B Instant)
- **Backend Tools:** MCP (Model Context Protocol) via SSE
- **UI:** Streamlit
- **Deployment:** HuggingFace Spaces

##  MCP Tools Available

| Tool | Description |
|------|-------------|
| `list_products` | Get all available products |
| `get_product` | Get details of a specific product |
| `search_products` | Search products by keyword |
| `get_customer` | Get customer information |
| `verify_customer_pin` | Verify customer identity |
| `list_orders` | Get customer's orders |
| `get_order` | Get specific order details |
| `create_order` | Create a new order |

##  Local Setup

```bash
pip install -r requirements.txt

# Windows PowerShell (example)
$env:GROQ_API_KEY = "your_groq_api_key"
$env:ENABLE_DUMMY_DATA = "1"  # optional demo mode for My Orders

streamlit run app.py
```

##  Test Data

If `ENABLE_DUMMY_DATA=1`, the app will validate PINs locally for the ** My Orders** flow.

| Email | PIN |
|-------|-----|
| donaldgarcia@example.net | 7912 |
| michellejames@example.com | 1520 |
| laurahenderson@example.org | 1488 |
| spenceamanda@example.org | 2535 |
| glee@example.net | 4582 |
| williamsthomas@example.net | 4811 |
| justin78@example.net | 9279 |
| jason31@example.com | 1434 |
| samuel81@example.com | 4257 |
| williamleon@example.net | 9928 |

##  Live Demo

**HuggingFace Spaces:** (add your link after deployment)

##  Videos

- Video 1: Problem & Plan
- Video 2: Activities, Decisions & Challenges
- Video 3: Demo & Future Improvements

##  Author

Rodrigo Wurdig - Andela GenAI Bootcamp

