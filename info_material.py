import streamlit as st


def tagging_session_info(cat):
    st.subheader(cat)
    st.write(
        "Please tag the following item accordingly by style (basic vs "
        "statement), occasion (where you would wear it), and season (when you "
        "would wear it).\n\n A clothing article is considered a 'Basic' piece "
        "if it is simple, solid-colored and able to match to many other items."
        " By contrast, a 'Statement' item is colorful, patterned, and not "
        "likely to match to many other items.\n\n"
    )


def finished_tagging_info():
    st.write(
        "Yay! You finished tagging all items in your closet! Your closet setup "
        "is complete. \n\n Click the button below to download the information "
        "and easily access your closet when you enter this app next."
    )


def categorize_wardrobe_info():
    st.subheader('About')
    st.write(
        "Items here are separated into 'Basic' pieces (i.e. items that are "
        "simple, solid colored, and able to match to many other items) and "
        "'Statement' pieces (items that are colorful, patterned, and not likely"
        " to match to many other items). \n \n"                
        "In order to limit manual user oversight and prevent user fatigue, a "
        "CNN Image Classification model was trained on 15000+ labeled images "
        "and was used to predict the appropriate category an item should fall "
        "into. The algorithm then uses this information to determine how to "
        "style clothing articles together. \n \n"
        "Keep in mind however, that the model may fail at times to categorize "
        "properly; in such a case, the user has the option to update the tags "
        "manually."
    )