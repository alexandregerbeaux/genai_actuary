import streamlit as st

st.set_page_config(
    page_title="Configuration",
    page_icon="📜",
)


with st.form("config_form"):

    guard_model_deployment_id_textbox = st.text_input('Guard Model Deployment ID', st.session_state.guard_model_deployment_id)
    generative_model_deployment_id_textbox = st.text_input('GenAI Model Deployment ID', st.session_state.genai_model_deployment_id)

    # Every form must have a submit button.
    submitted = st.form_submit_button("Update")
    if submitted:
        st.session_state.guard_model_deployment_id = guard_model_deployment_id_textbox
        st.session_state.genai_model_deployment_id = generative_model_deployment_id_textbox