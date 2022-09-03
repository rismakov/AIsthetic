import streamlit as st


def about_info():
    st.header('About AIsthetic')

    st.write("""
        AIsthetic is a wardrobe optimizer that helps you decide what to wear, 
        helps pack for a trip, and helps find items in your closet that best 
        resemble an inspiration photo.\n\n

        All you have to do is upload images of closet, and the app does the rest
        for you.\n\n

        With this app, you can:\n
        1. View all items in your closet.
        2. Select a random outfit based on weather and occasion.
        3. Surface outfit pieces that most closely resemble those from an
            inspiration image (e.g. Pinterest post).
        4. Generate an itinerary of clothing for your next trip based on trip 
            start date, trip end date, location, and luggage allowances.

        helping with diminishing decision fatigue, with reducing need to 
        purchase more clothing, and with optimizing travel planning.

        The algorithm currently has logic in place that determines whether two
        items match together when generating an outfit and logic in place that
        ensures the same item isn't selected too close together when creating an
        outfit plan.
    """)

def tagging_session_info(placeholder, cat):
    placeholder.subheader(cat)
    placeholder.write("""
        Please tag the following item accordingly by style (basic vs
        statement), occasion (where you would wear it), and season (when you
        would wear it).\n\n A clothing article is considered a 'Basic' piece
        if it is simple, solid-colored and able to match to many other items.
        By contrast, a 'Statement' item is colorful, patterned, and not
        likely to match to many other items.\n\n
    """)


def finished_tagging_info():
    st.subheader('Closet Setup: Complete')
    st.write("""
        Yay! You finished tagging all items in your closet! Your closet setup
        is complete. \n\n Click the button below to download the information
        and easily access your closet when you next enter this app.
    """)


def categorize_wardrobe_info():
    """Used in "Show Wardrobe Info" option.
    """
    st.subheader('About')
    st.write("""
        Items here are separated into 'Basic' pieces (i.e. items that are
        simple, solid colored, and able to match to many other items) and
        'Statement' pieces (items that are colorful, patterned, and not likely
        to match to many other items).\n\n
        In order to limit manual user oversight and prevent user fatigue, a
        CNN Image Classification model was trained on 15000+ labeled images
        and was used to predict the appropriate category an item should fall
        into. The algorithm then uses this information to determine how to
        style clothing articles together.\n\n
        Keep in mind however, that the model may fail at times to categorize
        properly; in such a case, the user has the option to update the tags
        manually.
    """)


def select_filters_info():
    """Used in "View all clothing articles in closet" option sidebar.
    """
    st.sidebar.header("Filters")
    st.sidebar.write(
        "Please select either seasons and occasions filters"
    )
