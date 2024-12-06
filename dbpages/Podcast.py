import format_markdowns as fmd
import streamlit as st

from authorship import show_authors


st.header('Dødehavsrullene')
authors = show_authors(['signemh'])
st.markdown('By ' + authors, unsafe_allow_html=True)
st.write('##')


im, txt = st.columns([.9, 2], vertical_alignment='center')
im.image('assets/art/podcast.png')
txt.caption(':green-background[This podcast is only available in Norwegian.]')
txt.markdown(fmd.general_justifypar(
    'Dette er en kort mini-serie bestående av tre episoder som handler om Døde'\
    'havsrullene. Serien tar utgangspunkt i lite til ingen forkunnskaper om Dø'\
    'dehavsrullene. Podcastserien er laget av Lying Pen of Scribes ved UiA, et'\
    ' tverrfaglig forksningsprosjekt som forsker på Dødehavsrullene. Det er Si'\
    'gne Marie Hægeland som har laget episodene og står for intervjuene i epis'\
    'odene.'), unsafe_allow_html=True)

st.markdown(
    '<br>**Episoder**<br>1. Dødehavsrullene - en innføring<br>'\
    '2. Hvordan Lansere et Falskt Dødehavsrullfragment?<br>'\
    '3. Tapte fragmenter<br>', unsafe_allow_html=True)

url = 'https://podcasts.apple.com/no/podcast/d%C3%B8dehavsrullene/id1666259129'
st.markdown('**Lenken til Apple Podcast:** [Dødehavsrullene](%s)' %url)
