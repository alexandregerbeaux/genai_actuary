import streamlit as st
import pandas as pd
from helpers import is_history, CONVERSATION_HISTORY, clean_history

st.set_page_config(
    page_title="Chat History",
    page_icon="📜",
)

history_placeholder = st.empty()

is_history()
df = pd.read_csv(CONVERSATION_HISTORY)
if df.empty:
    st.write("No chat history")
else:
    with history_placeholder.container():
        st.dataframe(df)
    
    if st.button('Clean history'):
        clean_history()
        history_placeholder.empty()