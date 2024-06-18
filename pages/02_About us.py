from authorship import team_card
from glob import glob

import os
import pandas as pd
import streamlit as st
import sqlite3 as sql

st.set_page_config(
    page_title="About",
    page_icon='assets/Icon.png'
)

def circle_image():
    st.markdown("""
        <style>
          [data-testid=stImage] {
              width: 200px;
              height: 200px;
              border-radius: 50%;
              overflow: hidden;
              box-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
              width: 100%;
              height: 100%;
              object-fit: cover;
          }
        </style>
        """, unsafe_allow_html=True)
    

def list_coreteam():
    namekeys = ['hildad', 'arsteinj', 'ludvikak'] #'matthewpm', 
    circle_image()
    for nk in namekeys:
        colphoto, coltext = st.columns([0.3, 2])
        card = team_card(nk)
        with colphoto:
            st.image(card[4])
        with coltext:
            text = '**' + card[0] + '**</br>:gray[' + card[1]
            # if card[2] is not None:
            #     text += '</br>' + card[2]
            text += '</br>' + card[3] + ']'
            st.markdown(text, unsafe_allow_html=True)


def list_pastmembers():
    conn = sql.connect('lyingpen.sqlite3')
    pastteam = pd.read_sql_query(
            """SELECT name_key, name, past_contribution FROM db_author 
            WHERE past_member=1""", conn)
    conn.close()

    for row in pastteam.itertuples():
        colphoto, coltext = st.columns([0.23, 2])
        if 'Signe' not in row.name: # To add Signe back when relevant DB is up
            # print(row.name)
            with colphoto:
                fim = glob('assets/team/' + row.name_key + '*')[0]
                st.image(fim)
            with coltext:
                text = ':gray[' + row.name + '</br><sup>Contributed to ' + \
                    row.past_contribution + '</sup>]'
                st.markdown(text, unsafe_allow_html=True)

st.subheader('The team')
list_coreteam()

st.markdown('##', unsafe_allow_html=True)
st.markdown('<h4>Past team members</h4>', unsafe_allow_html=True)
list_pastmembers()