import streamlit as st

from authorship import show_authors



st.header('Dead Sea Scrolls Physical and Scribal Features')
authors = show_authors(['matthewpm','hildad'], show_affil=False)
st.markdown(
    'By ' + authors + '</br>:blue[ver. 2024-beta1]', unsafe_allow_html=True)
st.write('##')

st.markdown(
    ':red[Intro text here, and some instructions. To mention sources mainly '\
    'DJD and Tov]')