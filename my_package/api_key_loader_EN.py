import streamlit as st

def configure_api_key(env):
    with st.sidebar:
        col1, col2 = st.columns([9, 4])
        with col1:
            with st.expander("Load API Key"):
                tab1, tab2, tab3 = st.tabs(["Local", "Upload_API_KEY", "WEB"])

                # Option 1: Key from .env file
                with tab1:
                    if st.button("Load env in application folder VSCODE"):
                        st.info(
                            "Env loaded from the application directory running on VSCODE"
                        )
                        if "openai_api_key" in env:
                            st.session_state["openai_api_key"] = env[
                                "openai_api_key"
                            ]
                        elif st.session_state.get("openai_api_key"):
                            st.success(
                                "API key has been saved to session on your computer."
                            )
                        else:
                            st.info(
                                "OpenAI API key not found. Set it in the .env file or enter manually."
                            )

                # Option 2: Key from a file
                with tab2:
                    uploaded_file = st.file_uploader(
                        "Upload file with API keys for LLM modules", type=None
                    )
                    st.info(
                        "Finds the key from a file stored in .env format, e.g., OPENAI_API_KEY=******"
                    )
                    if uploaded_file is not None:
                        content = uploaded_file.read().decode("utf-8")
                        lines = content.splitlines()

                        # Function to find the key
                        def find_key(lines, prefix):
                            for line in lines:
                                if line.strip().startswith(prefix):
                                    return (
                                        line.strip()
                                        .replace(prefix, "")
                                        .strip()
                                    )
                            return None

                        openai_key = find_key(lines, "OPENAI_API_KEY=")

                        if openai_key:
                            st.write("OpenAI API key found")
                            st.session_state["openai_api_key"] = openai_key
                            st.success(
                                "API key has been saved to session on your computer."
                            )
                        else:
                            st.write("OpenAI API key not found in the file.")

                # Option 3: Key from Streamlit Secrets
                with tab3:
                    if st.button("Load from Streamlit Secrets"):
                        if "OPENAI_API_KEY" in st.secrets:
                            st.session_state["openai_api_key"] = st.secrets[
                                "OPENAI_API_KEY"
                            ]
                            env["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
                        elif st.session_state.get("openai_api_key"):
                            st.success("API key is already in session")
                        else:
                            st.error(
                                "OpenAI API key not found. Set it in Streamlit > App Settings > Secrets."
                            )

        with col2:
            if st.button("Load from Web API"):
                if "OPENAI_API_KEY" in st.secrets:
                    st.session_state["openai_api_key"] = st.secrets[
                        "OPENAI_API_KEY"
                    ]
                    env["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

    # Protect the API key
    if not st.session_state.get("openai_api_key"):
        if "OPENAI_API_KEY" in env:
            st.session_state["openai_api_key"] = env["OPENAI_API_KEY"]
        else:
            st.info(
                "Add your OpenAI API key to use this application"
            )
            st.session_state["openai_api_key"] = st.text_input(
                "API Key", type="password"
            )
            if st.session_state["openai_api_key"]:
                st.rerun()

    if not st.session_state.get("openai_api_key"):
        st.stop()
