import streamlit as st
from helpers import init_config, write_history, DataRobotPredictionError, ask_generative_model, ask_guard_model, get_custom_metric_id, submit_metric
import datetime as dt

if __name__ == "__main__":

    init_config()

    st.set_page_config(
        page_title="SAS",
        page_icon="💬",
    )

    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        st.image("sas.png", width=50)

    with col2:
        st.subheader("Meet your Compliance Oracle! Hello")

    with col3:
        if st.button('Clear chat'):
            st.session_state.messages = []

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Please type in you question here?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        #try:
        #    with st.chat_message("assistant", avatar="datarobot_logo_icon.png"):
        #        message_placeholder = st.empty()
        #        print('running guard')
        #        toxic_label, toxic_value = ask_guard_model(st.session_state.guard_model_deployment_id , prompt)
        #        print('received guard')
        #        st.text(f"Prompt Toxicity: {toxic_label}, Value: {toxic_value}")
        #        if toxic_value < 0.5:
        #            assistant_response = ask_generative_model(st.session_state.genai_model_deployment_id, prompt)
        #        else:
        #            cm_id = get_custom_metric_id(st.session_state.genai_model_deployment_id )
        #            #submit_metric(st.session_state.genai_model_deployment_id , dt.datetime.now(), cm_id)
        #            assistant_response = "Blocked due to toxicity threshold"
        #        write_history(dt.datetime.now(), prompt, assistant_response, toxic_value > 0.5)
        #        message_placeholder.markdown(assistant_response)
        #    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        #except Exception as e:
        #    st.write(f"{e.__class__.__name__}: {str(e)}")

        try:
            with st.chat_message("assistant", avatar="sas.png"):
                message_placeholder = st.empty()
                assistant_response = ask_generative_model(st.session_state.genai_model_deployment_id, prompt)
                write_history(dt.datetime.now(), prompt, assistant_response, True)
                message_placeholder.markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        except Exception as e:
            st.write(f"{e.__class__.__name__}: {str(e)}")
