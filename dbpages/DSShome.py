#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 15:04:28 2023

@author: hildad
"""
import streamlit as st


# st.markdown('<h1>The Lying Pen of Scribes</h1>\n<h2>Databases and Resources</h2>', unsafe_allow_html=True)
st.header('The Lying Pen of Scribes Dead Sea Scrolls Databases and Resources')
ftitle = open('assets/texts/lp_frontpage_intro.txt', 'r')
st.markdown(
    '<div style="text-align: justify;">'+ftitle.read()+'</div>', unsafe_allow_html=True)
st.markdown('Note that, currently, this website is still :warning: **under development** :warning: and more databases will be added.', unsafe_allow_html=True)
st.markdown('##')

st.subheader('The Lying Pen of Scribes Research Project')
ftitle = open('assets/texts/lp_frontpage_project.txt', 'r')
st.markdown(
    '<div style="text-align: justify;">'+ftitle.read()+'</div>', unsafe_allow_html=True)
st.markdown('##')

c1, c2, c3, c4 = st.columns(
    [1, 1, 1, 0.7], gap='small', vertical_alignment='center')
c1.image('assets/logo-uia.jpg')
c2.image('assets/logo-ntnu.png')
c3.image('assets/logo-mf.png')