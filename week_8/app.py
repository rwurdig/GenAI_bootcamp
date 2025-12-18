import asyncio
import json
import os

import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from mcp import ClientSession
from mcp.client.sse import sse_client


# ============================================
# 1. SETUP & CONFIGURATION
# ============================================
load_dotenv()  # Load .env file for local development
nest_asyncio.apply()


def _env_flag(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


ENABLE_DUMMY_DATA = _env_flag("ENABLE_DUMMY_DATA", default=False)

st.set_page_config(
    page_title="SuperTech Store Support",
    page_icon="🛍️",
    layout="centered",
)


def _get_api_key() -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = None
    return (api_key or "").strip()


api_key = _get_api_key()
client = None
if not api_key:
    if ENABLE_DUMMY_DATA:
        st.warning(
            "Demo mode enabled (ENABLE_DUMMY_DATA=1): GROQ_API_KEY is missing, so LLM chat is disabled. Use 👤 My Orders to test mock data."
        )
    else:
        st.error(
            "⚠️ Missing GROQ_API_KEY. Please set it in Streamlit secrets or environment variables."
        )
        st.stop()
else:
    client = Groq(api_key=api_key)
MCP_SERVER_URL = "https://vipfapwm3x.us-east-1.awsapprunner.com/mcp"
MODEL_ID = "llama-3.1-8b-instant"  # Fast and free

# Demo-only customer verification data (for local testing).
# NOTE: Keep this behind ENABLE_DUMMY_DATA so it cannot accidentally bypass real verification.
DUMMY_CUSTOMER_PINS = {
    "donaldgarcia@example.net": "7912",
    "michellejames@example.com": "1520",
    "laurahenderson@example.org": "1488",
    "spenceamanda@example.org": "2535",
    "glee@example.net": "4582",
    "williamsthomas@example.net": "4811",
    "justin78@example.net": "9279",
    "jason31@example.com": "1434",
    "samuel81@example.com": "4257",
    "williamleon@example.net": "9928",
}

# Minimal demo orders so you can test the My Orders UI end-to-end.
DUMMY_ORDERS = {
    "donaldgarcia@example.net": [
        {"order_id": "ST-10001", "status": "Delivered", "items": 2},
    ],
    "michellejames@example.com": [
        {"order_id": "ST-10002", "status": "Shipped", "items": 1},
    ],
    "laurahenderson@example.org": [
        {"order_id": "ST-10003", "status": "Processing", "items": 3},
    ],
    "spenceamanda@example.org": [
        {"order_id": "ST-10004", "status": "Delivered", "items": 1},
    ],
    "glee@example.net": [
        {"order_id": "ST-10005", "status": "Cancelled", "items": 1},
    ],
    "williamsthomas@example.net": [
        {"order_id": "ST-10006", "status": "Shipped", "items": 2},
    ],
    "justin78@example.net": [
        {"order_id": "ST-10007", "status": "Delivered", "items": 4},
    ],
    "jason31@example.com": [
        {"order_id": "ST-10008", "status": "Processing", "items": 1},
    ],
    "samuel81@example.com": [
        {"order_id": "ST-10009", "status": "Shipped", "items": 2},
    ],
    "williamleon@example.net": [
        {"order_id": "ST-10010", "status": "Delivered", "items": 1},
    ],
}


# ============================================
# 2. SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """
You are a friendly Customer Support Agent for SuperTech Store, a company that sells computer products like monitors, printers, keyboards, and accessories.

WHEN TO USE TOOLS:
- Use 'list_products' or 'search_products' when the user asks about products, availability, or pricing.
- Use 'get_order' or 'list_orders' when the user asks about order status or tracking.
- Use 'get_customer' when you need customer information.
- Use 'verify_customer_pin' to verify customer identity if needed.
- Use 'create_order' only when the user explicitly wants to place an order.

SECURITY / CUSTOMER VERIFICATION:
- If the user asks to view their orders and they provide an email, ask for their 4-digit PIN.
- If a PIN is provided, verify it with 'verify_customer_pin' before calling 'list_orders'.
- Never repeat the PIN back to the user.

WHEN NOT TO USE TOOLS:
- For return policy questions, answer directly: "Our return policy allows returns within 30 days of purchase with original receipt. Items must be unopened or defective."
- For general troubleshooting (printer not working, monitor issues), provide helpful steps without calling tools.
- For greetings or general questions, respond naturally.

RULES:
- Be concise, helpful, and professional.
- If you need an Order ID or Customer ID, ask for it before calling tools.
- If you don't know something, say so honestly.
"""


# ============================================
# 3. HELPER FUNCTIONS
# ============================================
def mcp_tool_to_groq(tool):
    """Convert MCP tool format to Groq/OpenAI function format"""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema or {"type": "object", "properties": {}},
        },
    }


# ============================================
# 4. CORE LOGIC - MCP + LLM Integration
# ============================================
async def process_message(user_input, chat_history):
    """Process user message with tool-calling via MCP (SSE)."""

    if client is None:
        return "LLM chat is disabled because GROQ_API_KEY is missing. Enable demo mode with ENABLE_DUMMY_DATA=1 to test mock orders, or set GROQ_API_KEY to use full chat."

    async with sse_client(
        MCP_SERVER_URL,
        headers={"Accept": "text/event-stream", "Content-Type": "application/json"},
        timeout=30,
        sse_read_timeout=300,
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()
            groq_tools = [mcp_tool_to_groq(t) for t in mcp_tools.tools]

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(chat_history)
            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=messages,
                tools=groq_tools,
                tool_choice="auto",
                max_tokens=512,
                temperature=0.2,
            )

            assistant_msg = response.choices[0].message
            tool_calls = assistant_msg.tool_calls or []

            if not tool_calls:
                return assistant_msg.content or ""

            # Append dict (NOT the SDK object), so Groq can serialize tool calls.
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in tool_calls
                    ],
                }
            )

            tool_names = [tc.function.name for tc in tool_calls]
            st.toast(f"🛠️ Using tools: {', '.join(tool_names)}")

            for tc in tool_calls:
                function_name = tc.function.name
                function_args = json.loads(tc.function.arguments or "{}")

                result = await session.call_tool(function_name, function_args)

                # Serialize tool results safely as JSON.
                if hasattr(result, "content"):
                    try:
                        content_str = json.dumps(
                            result.content, ensure_ascii=False, default=str
                        )
                    except Exception:
                        content_str = str(result.content)
                else:
                    content_str = json.dumps(result, ensure_ascii=False, default=str)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": function_name,
                        "content": content_str,
                    }
                )

            final_response = client.chat.completions.create(
                model=MODEL_ID,
                messages=messages,
                tools=groq_tools,
                max_tokens=512,
                temperature=0.2,
            )
            return final_response.choices[0].message.content or ""


# ============================================
# 5. INPUT HANDLER
# ============================================
def handle_user_input(user_input):
    """Handle user input from chat or quick action buttons."""

    model_input = user_input
    display_input = user_input
    if isinstance(user_input, dict):
        model_input = user_input.get("model", "")
        display_input = user_input.get("display", model_input)

    st.session_state.messages.append({"role": "user", "content": display_input})

    with st.chat_message("user"):
        st.write(display_input)

    with st.chat_message("assistant"):
        with st.spinner("🔄 Processing your request..."):
            try:
                groq_history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                ]

                response_text = asyncio.run(process_message(model_input, groq_history))
                st.write(response_text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )


def _append_assistant_message(text: str) -> None:
    with st.chat_message("assistant"):
        st.write(text)
    st.session_state.messages.append({"role": "assistant", "content": text})


def _append_user_message(text: str) -> None:
    with st.chat_message("user"):
        st.write(text)
    st.session_state.messages.append({"role": "user", "content": text})


# ============================================
# 6. USER INTERFACE
# ============================================
st.title("🛍️ SuperTech Store Support")
st.caption(f"AI-powered support • Powered by Groq ({MODEL_ID}) & MCP")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

st.markdown("### ⚡ Quick Actions")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📦 Order Status", use_container_width=True):
        st.session_state.pending_action = "order_status"

with col2:
    if st.button("🛒 View Products", use_container_width=True):
        st.session_state.pending_action = "list_products"

with col3:
    if st.button("🔍 Search", use_container_width=True):
        st.session_state.pending_action = "search_product"

with col4:
    if st.button("↩️ Returns", use_container_width=True):
        st.session_state.pending_action = "return_policy"

with col5:
    if st.button("👤 My Orders", use_container_width=True):
        st.session_state.pending_action = "my_orders"


if st.session_state.pending_action:
    action = st.session_state.pending_action

    if action == "order_status":
        with st.form("order_form", clear_on_submit=True):
            st.markdown("**📦 Check Order Status**")
            order_id = st.text_input("Enter your Order ID:", placeholder="e.g., ORD-12345")
            submitted = st.form_submit_button("Check Status", use_container_width=True)
            if submitted and order_id:
                st.session_state.pending_action = None
                handle_user_input(f"What is the status of order {order_id}?")
                st.rerun()

    elif action == "list_products":
        st.session_state.pending_action = None
        handle_user_input("Show me all available products.")
        st.rerun()

    elif action == "search_product":
        with st.form("search_form", clear_on_submit=True):
            st.markdown("**🔍 Search Products**")
            search_term = st.text_input(
                "What are you looking for?", placeholder="e.g., monitor, printer"
            )
            submitted = st.form_submit_button("Search", use_container_width=True)
            if submitted and search_term:
                st.session_state.pending_action = None
                handle_user_input(f"Search for products related to: {search_term}")
                st.rerun()

    elif action == "return_policy":
        st.session_state.pending_action = None
        handle_user_input("What is your return policy?")
        st.rerun()

    elif action == "my_orders":
        with st.form("customer_form", clear_on_submit=True):
            st.markdown("**👤 View My Orders**")
            email = st.text_input("Email:", placeholder="e.g., donaldgarcia@example.net")
            pin = st.text_input("PIN:", type="password", placeholder="4-digit PIN")
            submitted = st.form_submit_button("View Orders", use_container_width=True)
            if submitted and email and pin:
                st.session_state.pending_action = None
                normalized_email = email.strip().lower()
                normalized_pin = pin.strip()

                # Demo mode: verify + show demo orders without sending the PIN to the LLM.
                if ENABLE_DUMMY_DATA and normalized_email in DUMMY_CUSTOMER_PINS:
                    user_text = f"My email is {normalized_email}. Show me my orders."
                    _append_user_message(user_text)
                    if normalized_pin != DUMMY_CUSTOMER_PINS[normalized_email]:
                        _append_assistant_message(
                            "❌ Verification failed (demo data): the PIN does not match this email."
                        )
                        st.rerun()

                    orders = DUMMY_ORDERS.get(normalized_email, [])
                    if not orders:
                        _append_assistant_message(
                            "✅ Verified (demo data). I couldn’t find any demo orders for this account."
                        )
                        st.rerun()

                    orders_text = "\n".join(
                        [
                            f"- Order {o['order_id']}: {o['status']} ({o['items']} item(s))"
                            for o in orders
                        ]
                    )
                    _append_assistant_message(
                        "✅ Verified (demo data). Here are your demo orders:\n" + orders_text
                    )
                    st.rerun()

                # Default behavior: keep PIN out of chat history, but allow the assistant/tooling flow.
                handle_user_input(
                    {
                        "display": f"My email is {email}. Show me my orders.",
                        "model": f"My email is {email} and my PIN is {pin}. Show me my orders.",
                    }
                )
                st.rerun()


st.divider()
st.markdown("### 💬 Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.write(
            "👋 Hello! Welcome to SuperTech Store Support. How can I help you today?"
        )
        st.write(
            "You can use the quick action buttons above or type your question below."
        )

if prompt := st.chat_input("Type your message here..."):
    handle_user_input(prompt)


with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown(
        """
This chatbot can help you with:
- 📦 Order tracking & status
- 🛒 Product information
- 🔍 Product search
- ↩️ Return policy questions
- 🛠️ General support
"""
    )

    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_action = None
        st.rerun()

    st.divider()

    st.markdown("### 🔧 Technical Info")
    st.markdown(
        f"""
- **Model:** {MODEL_ID}
- **MCP Server:** Connected
- **Tools:** 8 available
 - **Demo data:** {'Enabled' if ENABLE_DUMMY_DATA else 'Disabled'}
"""
    )
