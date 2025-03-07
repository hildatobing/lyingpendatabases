import streamlit as st


st.set_page_config(
    page_title="The Lying Pen of Scribes Databases and Resources",
    page_icon='assets/Icon.png',
    # initial_sidebar_state='collapsed'
)

pages = {
    'The Lying Pen of Scribes': [
        st.Page('dbpages/DSShome.py', title='About', icon=':material/home:'),
        st.Page('dbpages/Aboutus.py', title='People', icon=':material/groups:')],
    'Databases': [
        st.Page('dbpages/DSSexhibitions.py', title='DSS Exhibitions'),
        st.Page('dbpages/DSSscribal.py', title='DSS Physical and Scribal Features'),
        st.Page('dbpages/Post2002.py', title='Post 2002 Fragments')
    ],
    'Resources': [
        st.Page('dbpages/PosterArt.py', title='Art & Illustrations', 
                icon=':material/palette:'),
        st.Page('dbpages/Podcast.py', title='Podcast', 
                icon=':material/podcasts:')
    ]
}

pg = st.navigation(pages)
pg.run()