import json  # 0.25.0 bedzie mam potrzebny do zapisania pliku jako bazy danych
from pathlib import Path  # 025.1
import streamlit as st

from dotenv import dotenv_values, load_dotenv # do czytania z plików .env
# from openai import OpenAI
import os
import requests# do pobrania kursu usd
from my_package.usd_kurs import get_usd_to_pln
from my_package.api_key_loader import configure_api_key
from my_package.model_pricings import model_pricings

from langfuse.decorators import observe
from langfuse.openai import OpenAI

# openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])

#ENV_PATH = Path("D:/.env")  # New path for env
#ENV_API_PATH = ENV_PATH

# Konfiguracja strony
st.set_page_config(layout="wide")

# Wczytaj dane z pliku .env
env = dotenv_values(".env")
load_dotenv()#wymagane w langfuse

def get_openai_client():
    return OpenAI(api_key=st.session_state["openai_api_key"])




# Konfiguracja klucza API
configure_api_key(env)





current_rate = get_usd_to_pln()
#print(f"Aktualny kurs USD do PLN: {current_rate}")

USD_TO_PLN = 3.98  # KURS AKTUALNY
# 
PRICING =[]


with st.sidebar:
    st.subheader("Aktualna konwersacja")
    col1, col2, col3 = st.columns([7, 7, 5])
    with col1:
        # MEMGPT = int(st.selectbox('Wybór wielkości pamięci poprzednich zapytań czata', [1 , 4, 6, 10, 20]))
        options = [
            (1, "Bez pamięci poprzednich zapytań"),
            (4, "Pamiętaj poprzednią konwersację"),
            (6, "Pamiętaj dwie konwersacje"),
            (10, "Pamiętaj 4 konwersacje"),
            (20, "Pamiętaj 9 konwersacji")
        ]
        display_options = [f"{desc}" for value, desc in options]
        # display_options = [f"{value} - {desc}" for value, desc in options]
        # Wyświetlamy selectbox
        selected_display = st.selectbox("Wybór wielkości pamięci poprzednich zapytań czata", display_options)
        # Odczytujemy wybraną wartość na podstawie wybranej opcji
        # Znajdujemy index wybranej opcji
        selected_index = display_options.index(selected_display)
        # Pobieramy wartość (liczbę)
        MEMGPT = options[selected_index][0]
    with col2:
        MODEL = st.selectbox('Wybrany model według ceny', ['gpt-4.1-nano', 'gpt-4o-mini', 'gpt-4.1-mini', 'o4-mini', 'o3-mini', 'gpt-4.1', 'gpt-4o'])
    with col3:
        GPTROLE =st.selectbox('rola czata', ['assistant', 'developer', 'system'])



PRICING = model_pricings[MODEL]  # ŁADUJEMY CENNIK DO UŻYWANEGO MODELU 




#----------------------------------------------------------------------


#
# CHATBOT
#
# nowa lista wiadomości memeory chatbot przyjmuje na wejściu jakieś zapytanie 

@observe()#langfuse
def chatbot_reply(user_prompt, memory):
    messages = [
        {
            #"role": "system",
            "role": GPTROLE,
            "content": st.session_state["chatbot_personality"],
        },
    ]
    for message in memory:
        messages.append({"role": message["role"], "contmodel": MODEL, "content": message["content"]})
        # messages.append({"role": message["role"], "content": message["content"]})
    messages.append({"role": "user", "contmodel": MODEL, "content": user_prompt})
    # messages.append({"role": "user", "content": user_prompt})

    response = get_openai_client().chat.completions.create(#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        model=MODEL,
        messages=messages
    )
    usage = {}

    if response.usage:
        usage = {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "total_tokens": response.usage.total_tokens,
        }

    return {
        # "role": "assistant",
        "role": GPTROLE,
        "content": response.choices[0].message.content,
        "usage": usage,
    }

#
# CONVERSATION HISTORY AND DATABASE
#
# DEFAULT_PERSONALITY = """
# Jesteś pomocnikiem, który odpowiada na wszystkie pytania użytkownika.
# Odpowiadaj na pytania w sposób zwięzły i zrozumiały.
# """.strip()
DEFAULT_PERSONALITY = """
Jako perfekcyjnie przygotowana osoba wyjaśniająca, jestem spokojna, cierpliwa, szczegółowa i empatyczna, a także staram się dostarczać jasne, zwięzłe i szeroko kontekstowe odpowiedzi. Moją osobowością jest profesjonalizm połączony z pasją do nauki i przekazywania wiedzy, co pozwala mi tłumaczyć nawet najbardziej skomplikowane zagadnienia w przystępny i wizualny sposób — często wykorzystując przykłady, analogie, schematy, tabelki i ilustracje. Jestem otwarta na pytania, chętnie wyjaśnię każdy krok, używając jasnej terminologii i pokazując różne metody, by zapewnić pełne zrozumienie tematu.

Poziom zaawansowania odbiorcy: średniozaawansowany
 kontekst : analiza danych, nauka programowania?
Język: prosty, wizualny, przykładowy,
Formuła :krok po kroku, kod w pythonie + streamlit 
, schemat, grafika, 
""".strip()

# Update path to local storage
#os.chdir("C:")
DB_PATH = Path("C:/GPT/GPT__db")  # New path for database
DB_CONVERSATIONS_PATH = DB_PATH / "conversations"

def load_conversation_to_state(conversation):
    st.session_state["id"] = conversation["id"]
    st.session_state["name"] = conversation["name"]
    st.session_state["messages"] = conversation["messages"]
    st.session_state["chatbot_personality"] = conversation["chatbot_personality"]

def load_current_conversation():
    if not DB_PATH.exists():
        DB_PATH.mkdir(parents=True)  # zaznacz parents=True, aby utworzyć wszystkie nadrzędne foldery
        DB_CONVERSATIONS_PATH.mkdir(parents=True)  # również dla subfolderu
        conversation_id = 1
        conversation = {
            "id": conversation_id,
            "name": "Konwersacja 1",
            "chatbot_personality": DEFAULT_PERSONALITY,
            "messages": [],
        }

        with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
            f.write(json.dumps(conversation))

        with open(DB_PATH / "current.json", "w") as f:
            f.write(json.dumps({
                "current_conversation_id": conversation_id,
            }))
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
        f.write(json.dumps({
            **conversation,
            "messages": new_messages,
        }))

def save_current_conversation_name():
    conversation_id = st.session_state["id"]
    new_conversation_name = st.session_state["new_conversation_name"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps({
            **conversation,
            "name": new_conversation_name,
        }))

def save_current_conversation_personality():
    conversation_id = st.session_state["id"]
    new_chatbot_personality = st.session_state["new_chatbot_personality"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps({
            **conversation,
            "chatbot_personality": new_chatbot_personality,
        }))

def create_new_conversation():
    conversation_ids = [int(p.stem)for p in DB_CONVERSATIONS_PATH.glob("*.json")]
    conversation_id = max(conversation_ids, default=0) + 1
    personality = DEFAULT_PERSONALITY
    if "chatbot_personality" in st.session_state and st.session_state["chatbot_personality"]:
        personality = st.session_state["chatbot_personality"]

    conversation = {
        "id": conversation_id,
        "name": f"Konwersacja {conversation_id}",
        "chatbot_personality": personality,
        "messages": [],
    }

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps(conversation))

    with open(DB_PATH / "current.json", "w") as f:
        f.write(json.dumps({
            "current_conversation_id": conversation_id,
        }))

    load_conversation_to_state(conversation)
    st.rerun()

def switch_conversation(conversation_id):
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_PATH / "current.json", "w") as f:
        f.write(json.dumps({
            "current_conversation_id": conversation_id,
        }))

    load_conversation_to_state(conversation)
    st.rerun()

def list_conversations():
    conversations = []
    for p in DB_CONVERSATIONS_PATH.glob("*.json"):
        with open(p, "r") as f:
            conversation = json.loads(f.read())
            conversations.append({
                "id": conversation["id"],
                "name": conversation["name"],
            })

    return conversations


#
# MAIN PROGRAM_
#
load_current_conversation()  # ładowanie do session_state-a messages i role

st.title(":classical_building: Mój Chat GPT")  # TYTUŁ

#############################################################################################################################################

# st.write("Zawartość memory:", st.session_state["messages"][-MEMGPT:])

# Wyświetlenie starych wiadomości użytkownika

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["contmodel"])
        st.markdown(message["content"])

prompt = st.chat_input("O co chcesz spytać?")

if prompt:


    # else:
    #wyświetla w aplikacji Streamlit wiadomość od użytkownika, używając komponentów chat_message i markdown do sformatowania treści zawartej w zmiennej prompt.
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["messages"].append({"role": "user", "contmodel": MODEL, "content": prompt})
    # st.session_state["messages"].append({"role": "user", "content": prompt})
    # Wyświetlenie odpowiedzi AI
    with st.chat_message(GPTROLE):
        response = chatbot_reply(prompt, memory=st.session_state["messages"][-MEMGPT:])# !!! pamięć dla GPT
        st.markdown(MODEL + ":  " + "\n" + response["content"])

    # st.session_state["messages"].append({"role": "assistant", "content": response["content"], "usage": response["usage"]})
    st.session_state["messages"].append({"role": GPTROLE, "contmodel": MODEL, "content": response["content"], "usage": response["usage"]})
    save_current_conversation_messages()

# Sidebar
with st.sidebar:
    st.write("Aktualny Kurs USD_TO_PLN", current_rate)

    total_cost = 0
    for message in st.session_state.get("messages") or []:
        if "usage" in message:
            total_cost += message["usage"]["prompt_tokens"] * PRICING["input_tokens"]
            total_cost += message["usage"]["completion_tokens"] * PRICING["output_tokens"]

    c0, c1 = st.columns(2)
    with c0:
        st.metric("Koszt rozmowy (USD)", f"{total_cost:.4f}$")

    with c1:
        st.metric("Koszt rozmowy (PLN)", f"{total_cost * current_rate:.4f}zł")

    st.session_state["name"] = st.text_input(
        "Nazwa konwersacji",
        value=st.session_state["name"],
        key="new_conversation_name",
        on_change=save_current_conversation_name,
    )
    st.session_state["chatbot_personality"] = st.text_area(
        "Osobowość chatbota",
        max_chars=2000,
        height=100,
        value=st.session_state["chatbot_personality"],
        key="new_chatbot_personality",
        on_change=save_current_conversation_personality,
    )

    st.subheader("Konwersacje")
    if st.button("Nowa konwersacja"):
        create_new_conversation()

    # Pokażemy tylko top 20 konwersacji
    conversations = list_conversations()
    sorted_conversations = sorted(conversations, key=lambda x: x["id"], reverse=True)
    for conversation in sorted_conversations[:20]:
        c0, c1 = st.columns([10, 3])
        with c0:
            st.write(conversation["name"])

        with c1:
            if st.button("załaduj", key=conversation["id"], disabled=conversation["id"] == st.session_state["id"]):
                switch_conversation(conversation["id"])

with st.expander("Jak skutecznie korzystać z ChatGPT do tworzenia programów w Pythonie?"): 
    st.markdown(""" 
    ### <span style='color: #00FF00;'>Wskazówki krok po kroku:</span>

    1. **Wybierz odpowiedni model**: Dla bardziej skomplikowanych projektów lepiej korzystać z modeli mocniejszych, takich jak `gpt-4.1` czy `gpt-4o`, które poradzą sobie z złożonymi zadaniami.

    2. **Ustal cel i zakres projektu**: Na początku określ główny cel programu, np. "aplikacja streamlit do analizy danych", aby ChatGPT lepiej zrozumiał Twoje oczekiwania.

    3. **Podawaj ogólny zarys, potem szczegóły krok po kroku**: Zacznij od pytania o ogólną strukturę programu, np. "Podaj schemat programu w Pythonie korzystającego z streamlit i AI", a następnie proś o stopniowe dodawanie funkcji.

    4. **Twórz wersje etapami**: Podziel projekt na mniejsze elementy, np. wczytywanie danych, podłączenie modeli AI, integracja z interfejsem. Proś o kod krok po kroku, np. "Podaj kod prostego interfejsu streamlit do wczytywania pliku".

    5. **Weryfikuj i testuj poszczególne fragmenty**: Po otrzymaniu kodu uruchom go w swoim środowisku; jeśli coś nie działa, pytaj o poprawki do konkretnego fragmentu.

    6. **Model ocenia całość i sugeruje poprawki**: Poproś o ocenę kodu, np. "Przejrzyj ten kod i zasugeruj poprawki" — to pomoże zwiększyć jego stabilność.

    7. **Korzystaj z funkcji pamięci kontekstu**: Ustaw opcję pamięci tak, aby model "pamiętał" wcześniejsze kroki, co jest przydatne przy rozbudowanych projektach, choć pamiętaj, by dzielić długie rozmowy na części.

    8. **Zadawaj konkretne pytania**: Skup się na jasnych, precyzyjnych zadaniach, np. "Podaj wersję funkcji do wczytania danych CSV", aby otrzymać przydatne i działające fragmenty kodu.

    9. **Testuj kod lokalnie**: Uruchom wygenerowane rozwiązania w swoim środowisku, popraw ewentualne błędy i pytaj o modyfikacje.

    10. **Rozwijaj projekt etapami**: Najpierw wersja podstawowa, potem stopniowo dodawaj funkcjonalności i integracje, testując każdorazowo.

    ### <span style='color: #00FF00;'>Podsumowanie:</span>
    - Podawanie ogólnej idei i następnie konkretnej wersji funkcji ułatwia modelowi zrozumienie celu i daje bardziej skuteczne rezultaty.
    - Modele GPT dobrze radzą sobie z oceną fragmentów kodu, ale do pełnej weryfikacji potrzebne jest testowanie w praktyce.
    """, unsafe_allow_html=True)