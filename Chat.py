from streamlit_feedback import streamlit_feedback
import streamlit as st
from helpers import init_config, write_history, DataRobotPredictionError, ask_generative_model, ask_guard_model, get_custom_metric_id, submit_metric, topic_guard
import datetime as dt
#from trubrics.integrations.streamlit import FeedbackCollector
import datarobotx as drx

from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb
import numpy as np



def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 105px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        "Hello ",
#        image('https://avatars3.githubusercontent.com/u/45109972?s=400&v=4',
#              width=px(25), height=px(25)),
#        " with ❤️ by ",
#        link("https://twitter.com/ChristianKlose3", "@ChristianKlose3"),
#        br(),
#        link("https://buymeacoffee.com/chrischross", image('https://i.imgur.com/thJhzOO.png')),
    ]
    layout(*myargs)

if __name__ == "__main__":




    init_config()

    print('test')
    st.set_page_config(
        page_title="SAS",
        page_icon="💬",
    )

    col1, col2, col3 = st.columns([1, 4, 1])

    #footer()



    with col1:
        st.image("sas.png", width=50)


    with col2:
        st.subheader("Meet your Compliance Oracle!")

    with col3:
        if st.button('Clear chat'):
            st.session_state.messages = []

    st.markdown('Please note that this app serves as a tool for research and development purposes only. Users are advised to exercise their professional judgment, as there is no guarantee of the accuracy or reliability of the information provided.')


    if "feedback" not in st.session_state:
        st.session_state.feedback = False

    print(st.session_state.feedback)

    if "current_message" not in st.session_state:
        st.session_state.current_message = []

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []


    #if st.session_state.feedback:
    #    write_history(dt.datetime.now(), "test", "test", True)


    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.messages:
        print('test')

    if len(st.session_state.messages) >0:
        print("message in the stack")



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
                response = topic_guard(prompt)
                if response['flagged']:
                    assistant_response = "Blocked because the question is unrelated to insurance content"
                    message_placeholder.markdown(assistant_response)
                else:
                    assistant_response, confidence_score = ask_generative_model(st.session_state.genai_model_deployment_id, prompt)

                    confidence_score_text = str(np.round(confidence_score,2)*100)+'%'
                    message_placeholder.markdown(assistant_response)
                    #message_placeholder.markdown(citations)
                    my_bar = st.progress(confidence_score, text=f"confidence score: {confidence_score_text}")
                st.session_state.current_message = [prompt, assistant_response]
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                #with open('data/rag/MAS 125_Apr 2013.pdf', 'rb') as f:
                #    st.download_button('Download Pdf', f, file_name='data/rag/MAS 125_Apr 2013.pdf')
                #st.session_state.feedback = streamlit_feedback(feedback_type="thumbs", align="flex-start")
                #with feedback:
                #    print(feedback)
                #collector = FeedbackCollector()
                #collector.st_feedback(feedback_type="issue")
                #feedback = streamlit_feedback(feedback_type="thumbs")



                #feedback_option = "faces" if st.toggle(label="Thumbs", value=False) else "thumbs"


                #write_history(dt.datetime.now(), prompt, assistant_response, True)
                #c = st.container()
                #_, thumbsup, thumbsdown = c.columns([15, 1, 1])
                #do_upvote = thumbsup.button(label=":thumbsup:")
                #do_downvote = thumbsdown.button(label=":thumbsdown:")

                #if do_upvote:
                #    write_history(dt.datetime.now(), st.session_state.current_message["prompt"], st.session_state.current_message["response"], True)
                #    with c.empty():
                #        st.markdown(":thinking_face:")
                #        #save_chat_response(history, "upvote")
                #        print('writing')

                #        st.markdown(":smile: Your response has been recorded!")

                #if do_downvote:
                #    write_history(dt.datetime.now(), prompt, assistant_response, False)
                #    with c.empty():
                #        st.markdown(":thinking_face:")
                #        #save_chat_response(history, "downvote")

                #        st.markdown(":disappointed_relieved: We'll try harder next time.")



    #if feedback:
    #    write_history(dt.datetime.now(), st.session_state.current_message["prompt"], st.session_state.current_message["response"], True)


        except Exception as e:
            st.write(f"{e.__class__.__name__}: {str(e)}")

    if len(st.session_state.current_message)>0:
        print("perfrfffeffff")
        feedback = streamlit_feedback(feedback_type="thumbs", align="flex-start")
        if feedback:
            print('feedback')
            print(feedback)
            print(st.session_state.current_message)
            write_history(dt.datetime.now(), st.session_state.current_message[0], st.session_state.current_message[1], feedback['score'])
