import streamlit as st

from authorship import show_authors


st.header('Art & Illustrations')
authors = show_authors(['thomasa'])
st.markdown('By ' + authors, unsafe_allow_html=True)
st.write('##')


url = 'https://cas-nor.no/project/books-known-only-title'
st.markdown(
    'This page holds the collection of art and illustrations created for the '\
    'Lying Pen of Scribes project and its events. Below, a conference jointly'\
    ' held with the project [**Books Known Only by Title**](%s) can also be f'\
    'ound.'%url, unsafe_allow_html=True)
st.markdown('##')

c1, c2 = st.columns([1, 1.3], gap='medium')
c1.image('assets/art/logo.png', caption='Logo-The Lying Pen of Scribes project')
c2.image(
    'assets/art/2021-10-MFconf.png', caption='Conference by The Lying Pen of '\
    'Scribes and Books Known Only by Title, 25-27 October 2021')

c3, c4 = st.columns([1, 1], gap='medium')
c3.image('assets/art/2020-03-UiAconf.png', caption='Conference, 13 March 2020')
c3.image(
    'assets/art/2021-12-UiAworkshop.png', caption='Workshop, 6-8 December 2021')
c4.image(
    'assets/art/2022-03-UiAretreat.png', caption='Retreat, 9-11 March 2022')
c4.image('assets/art/2022-05-MFconf.png', caption='Conference, 4-6 May 2022')

st.image('assets/art/2022-09-UiAconf.png', caption='Conference, September 2022')
st.image(
    'assets/art/2022-08-UiAconf-banner.png', 
    caption='Symposium, 29 August-1 September 2022')
st.image(
    'assets/art/2022-12-UiAconf.png', caption='Conference, 12-14 December 2022')

c5, c6 = st.columns([1, 1], gap='medium')
c5.image('assets/art/podcast.png', caption='Podcast (in Norwegian)')