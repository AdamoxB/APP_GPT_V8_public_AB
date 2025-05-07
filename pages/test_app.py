# import streamlit as st
# import requests
# from bs4 import BeautifulSoup

# st.title("Pobieranie i wyświetlanie tekstu ze strony WWW")

# # Pole do wpisania URL
# url = st.text_input("Wpisz adres URL strony:", "")

# if url:
#     try:
#         # Pobranie strony
#         headers = {"User-Agent": "Mozilla/5.0"}
#         resp = requests.get(url, headers=headers, timeout=10)
#         resp.raise_for_status()

#         # Parsowanie HTML i wyciągnięcie samego tekstu
#         soup = BeautifulSoup(resp.text, "html.parser")
#         # Możesz ograniczyć do konkretnego tagu, np. soup.find("div", {"class":"content"})
#         plain_text = soup.get_text(separator="\n", strip=True)

#         main_content = soup.get_text()

#         # Wyświetlenie tekstu w okienku przewijalnym
#         st.text_area("Zawartość strony:", plain_text, height=500)

#         # Opcja do pobrania treści w pliku
#         st.download_button(
#             label="Pobierz treść jako plik tekstowy",
#             data=main_content,
#             file_name='zawartosc_strony.txt'
#         )

#     except requests.exceptions.RequestException as e:
#         st.error(f"Błąd pobierania strony: {e}")











# import streamlit as st
# import requests
# from bs4 import BeautifulSoup

# def get_text(url):
#     r = requests.get(url)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     for tag in soup(["script", "style"]):
#         tag.decompose()
#     return soup.get_text(separator="\n").strip()

# st.title("Wyświetl_treść strony")
# url = st.text_input("Podaj URL", "")
# if url:
#     try:
#         text = get_text(url)
#         st.text_area("Treść strony", text, height=400)
#     except Exception as e:
#         st.error(e)

import streamlit as st
import requests
from bs4 import BeautifulSoup

@st.cache_data
def fetch_text(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    texts = soup.find_all(text=True)
    blacklist = ['script', 'style', 'head', 'title', 'meta', '[document]']
    visible = [t.strip() for t in texts if t.parent.name not in blacklist and t.strip()]
    return '\n'.join(visible)

st.title("Webpage Text Importer")
url = st.text_input("Podaj URL", "")

if st.button("Pobierz"):
    if url:
        try:
            with st.spinner("Ładowanie..."):
                content = fetch_text(url)
                st.text_area("Zawartość tekstowa", content, height=400)
        except Exception as e:
            st.error(f"Błąd: {e}")