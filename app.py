import json  # 0.25.0 will be needed to save the file as a database
from pathlib import Path
import streamlit as st

from dotenv import dotenv_values, load_dotenv  # for reading .env files
import os
import requests  # for fetching USD rates
from my_package.usd_kurs import get_usd_to_pln
from my_package.api_key_loader_EN import configure_api_key
from my_package.model_pricings import model_pricings

# ------------------------------------------------------------------
# Page configuration
st.set_page_config(layout="wide")

# Load environment variables from .env
env = dotenv_values(".env")
load_dotenv()  # required for langfuse

def get_openai_client():
    return OpenAI(api_key=st.session_state["openai_api_key"])

# Configure API key
configure_api_key(env)

current_rate = get_usd_to_pln()
USD_TO_PLN = 3.98  # current rate (will be overwritten by the fetched value)
PRICING = []

# ------------------------------------------------------------------
# Sidebar configuration
with st.sidebar:
    st.subheader("Current conversation")
    col1, col2, col3 = st.columns([7, 7, 5])

    with col1:
        options = [
            (1, "No memory of previous chat queries"),
            (4, "Remember the previous conversation"),
            (6, "Remember two conversations"),
            (10, "Remember four conversations"),
            (20, "Remember nine conversations")
        ]
        display_options = [f"{desc}" for value, desc in options]
        selected_display = st.selectbox(
            "Select memory size of previous chat queries", display_options
        )
        selected_index = display_options.index(selected_display)
        MEMGPT = options[selected_index][0]

    with col2:
        MODEL = st.selectbox(
            "Model chosen by price",
            [
                'gpt-4.1-nano', 'gpt-4o-mini',
                'gpt-4.1-mini', 'o4-mini', 'o3-mini',
                'gpt-4.1', 'gpt-4o'
            ]
        )

    with col3:
        GPTROLE = st.selectbox(
            "Chat role",
            ['assistant', 'developer', 'system']
        )

    PRICING = model_pricings[MODEL]  # load pricing for the selected model

# ------------------------------------------------------------------
DEFAULT_PERSONALITY = """
As a perfectly prepared explanatory person, I am calm, patient, detailed, and empathetic,
and I strive to provide clear, concise, and broadly contextual answers.
My personality is professionalism combined with a passion for learning and teaching,
allowing me to explain even the most complex topics in an accessible and visual way—
often using examples, analogies, diagrams, tables, and illustrations.
I am open to questions and gladly explain every step,
using clear terminology and showing different methods to ensure full understanding.

Audience proficiency level: intermediate
Context: data analysis, programming learning?
Language: simple, visual, example-based
Formula: step-by-step, code in Python + Streamlit, diagram, graphics
""".strip()

# ------------------------------------------------------------------
DB_PATH = Path("C:/GPT/GPT__db")  # local storage path
DB_CONVERSATIONS_PATH = DB_PATH / "conversations"

def load_conversation_to_state(conversation):
    st.session_state["id"] = conversation["id"]
    st.session_state["name"] = conversation["name"]
    st.session_state["messages"] = conversation["messages"]
    st.session_state["chatbot_personality"] = conversation["chatbot_personality"]

def load_current_conversation():
    if not DB_PATH.exists():
        DB_PATH.mkdir(parents=True)
        DB_CONVERSATIONS_PATH.mkdir(parents=True)
        conversation_id = 1
        conversation = {
            "id": conversation_id,
            "name": f"Conversation {conversation_id}",
            "chatbot_personality": DEFAULT_PERSONALITY,
            "messages": [],
        }
        with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
            f.write(json.dumps(conversation))
        with open(DB_PATH / "current.json", "w") as f:
            f.write(
                json.dumps({"current_conversation_id": conversation_id})
            )
    else:
        with open(DB_PATH / "current.json", "r") as f:
            data = json.loads(f.read())
            conversation_id = data["current_conversation_id"]
        with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
            conversation = json.loads(f.read())

    load_conversation_to_state(conversation)

def save_current_conversation_messages():
    conversation_id = st.session_state["id"]
    new_messages = st.session_state["messages"]
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(
            json.dumps({**conversation, "messages": new_messages})
        )

def save_current_conversation_name():
    conversation_id = st.session_state["id"]
    new_conversation_name = st.session_state["new_conversation_name"]
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(
            json.dumps({**conversation, "name": new_conversation_name})
        )

def save_current_conversation_personality():
    conversation_id = st.session_state["id"]
    new_chatbot_personality = st.session_state["new_chatbot_personality"]
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(
            json.dumps({**conversation, "chatbot_personality": new_chatbot_personality})
        )

def create_new_conversation():
    conversation_ids = [int(p.stem) for p in DB_CONVERSATIONS_PATH.glob("*.json")]
    conversation_id = max(conversation_ids, default=0) + 1
    personality = DEFAULT_PERSONALITY
    if "chatbot_personality" in st.session_state and st.session_state["chatbot_personality"]:
        personality = st.session_state["chatbot_personality"]

    conversation = {
        "id": conversation_id,
        "name": f"Conversation {conversation_id}",
        "chatbot_personality": personality,
        "messages": [],
    }
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps(conversation))
    with open(DB_PATH / "current.json", "w") as f:
        f.write(
            json.dumps({"current_conversation_id": conversation_id})
        )
    load_conversation_to_state(conversation)
    st.rerun()

def switch_conversation(conversation_id):
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())
    with open(DB_PATH / "current.json", "w") as f:
        f.write(
            json.dumps({"current_conversation_id": conversation_id})
        )
    load_conversation_to_state(conversation)
    st.rerun()

def list_conversations():
    conversations = []
    for p in DB_CONVERSATIONS_PATH.glob("*.json"):
        with open(p, "r") as f:
            conversation = json.loads(f.read())
            conversations.append(
                {"id": conversation["id"], "name": conversation["name"]}
            )
    return conversations

# ------------------------------------------------------------------
load_current_conversation()  # load messages and personality into session_state
st.title(":classical_building: My Chat GPT")

# Display previous user messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message.get("contmodel", ""))
        st.markdown(message["content"])

prompt = st.chat_input("What would you like to ask?")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["messages"].append(
        {"role": "user", "contmodel": MODEL, "content": prompt}
    )

    with st.chat_message(GPTROLE):
        response = chatbot_reply(prompt, memory=st.session_state["messages"][-MEMGPT:])
        st.markdown(f"{MODEL}:\n{response['content']}")

    st.session_state["messages"].append(
        {"role": GPTROLE, "contmodel": MODEL, "content": response["content"], "usage": response["usage"]}
    )
    save_current_conversation_messages()

# ------------------------------------------------------------------
with st.sidebar:
    st.write("Current USD to PLN rate:", current_rate)

    total_cost = 0
    for message in st.session_state.get("messages") or []:
        if "usage" in message:
            total_cost += (
                message["usage"]["prompt_tokens"] * PRICING["input_tokens"]
            )
            total_cost += (
                message["usage"]["completion_tokens"] * PRICING["output_tokens"]
            )

    c0, c1 = st.columns(2)
    with c0:
        st.metric("Conversation cost (USD)", f"{total_cost:.4f}$")
    with c1:
        st.metric("Conversation cost (PLN)", f"{total_cost * current_rate:.4f}zł")

    st.session_state["name"] = st.text_input(
        "Conversation name",
        value=st.session_state["name"],
        key="new_conversation_name",
        on_change=save_current_conversation_name,
    )
    st.session_state["chatbot_personality"] = st.text_area(
        "Chatbot personality",
        max_chars=2000,
        height=100,
        value=st.session_state["chatbot_personality"],
        key="new_chatbot_personality",
        on_change=save_current_conversation_personality,
    )

    st.subheader("Conversations")
    if st.button("New conversation"):
        create_new_conversation()

    conversations = list_conversations()
    sorted_conversations = sorted(conversations, key=lambda x: x["id"], reverse=True)
    for conversation in sorted_conversations[:20]:
        c0, c1 = st.columns([10, 3])
        with c0:
            st.write(conversation["name"])
        with c1:
            if st.button(
                "Load", key=conversation["id"], disabled=conversation["id"] == st.session_state["id"]
            ):
                switch_conversation(conversation["id"])

# ------------------------------------------------------------------
with st.expander("How to effectively use ChatGPT for creating Python programs?"):
    st.markdown(
        """
### <span style='color: #00FF00;'>Step-by-step tips:</span>

1. **Choose the appropriate model**: For more complex projects it's better to use stronger models such as `gpt-4.1` or `gpt-4o`, which can handle intricate tasks.

2. **Define the project goal and scope**: Start by specifying the main purpose of the program, e.g., "a Streamlit app for data analysis", so ChatGPT better understands your expectations.

3. **Provide an overview first, then details step-by-step**: Begin with a question about the overall structure of the program, e.g., "Give me a diagram of a Python program using Streamlit and AI", then ask to gradually add functions.

4. **Build versions in stages**: Divide the project into smaller parts, e.g., data loading, connecting AI models, interface integration.
   Ask for code step-by-step, e.g., "Provide code for a simple Streamlit file upload interface".

5. **Verify and test individual fragments**: After receiving the code, run it in your environment; if something doesn't work, ask for fixes to the specific fragment.

6. **Model evaluates everything and suggests improvements**: Ask for an evaluation of the code, e.g., "Review this code and suggest improvements" — that will help increase its stability.

7. **Use context memory features**: Set the memory option so the model “remembers” previous steps, which is useful for larger projects,
   but remember to split long conversations into parts.

8. **Ask specific questions**: Focus on clear, precise tasks, e.g., "Provide a function to load CSV data",
   to get useful and working code snippets.

9. **Test code locally**: Run the generated solutions in your environment, fix any errors,
   and ask for modifications.

10. **Develop the project incrementally**: First create a basic version, then gradually add features and integrations,
    testing each time.

### <span style='color: #00FF00;'>Summary:</span>
- Providing a general idea followed by specific function versions helps the model understand the goal and yields more effective results.
- GPT models handle code evaluation well, but full verification requires practical testing.
"""
        ,
        unsafe_allow_html=True,
    )
