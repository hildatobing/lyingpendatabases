#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 15:04:28 2023

@author: hildad
"""
from glob import glob
from math import isnan

import numpy as np
import pandas as pd
import re
import streamlit as st


st.set_page_config(
    page_title="Lying Pen Databases and Resources",
    page_icon='assets/Icon.png'
)


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

# st.markdown(':red[Intro for the webpage, that it is for datasets and resources]')
