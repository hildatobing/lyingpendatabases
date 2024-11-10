import streamlit as st


st.set_page_config(
    page_title="The Lying Pen of Scribes Databases and Resources",
    page_icon='assets/Icon.png',
    # initial_sidebar_state='collapsed'
)

pages = {
    'The Lying Pen of Scribes': [
        st.Page('pages/DSShome.py', title='About', icon=':material/home:'),
        st.Page('pages/Aboutus.py', title='People', icon=':material/groups:')],
    'Databases': [
        # st.Page('pages/DSSscribal.py', title='DSS Physical and Scribal Features'),
        st.Page('pages/Post2002.py', title='Post 2002 Fragments')
    ],
    'Resources': [
        st.Page('pages/PosterArt.py', title='Art & Illustrations', 
                icon=':material/palette:')
    ]
}

pg = st.navigation(pages)
pg.run()