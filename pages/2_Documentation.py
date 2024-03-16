import streamlit as st
import pandas as pd
from helpers import is_history, CONVERSATION_HISTORY, clean_history

st.set_page_config(
    page_title="Documentation",
    page_icon="📜",
)


st.write("Explanation about the application")

    #if st.button('Clean history'):
    #    clean_history()
    #    history_placeholder.empty()
