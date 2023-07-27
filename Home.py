#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 15:04:28 2023

@author: hildad
"""
from glob import glob
from math import isnan
from matplotlib import pyplot as plt
from streamlit_tags import st_tags, st_tags_sidebar
from streamlit_option_menu import option_menu

import numpy as np
import pandas as pd
import re
import streamlit as st


st.set_page_config(
    page_title="Lying Pen Databases and Resources",
)


st.markdown('<h1>The Lying Pen of Scribes</h1>\n<h2>Databases and Resources</h2>', unsafe_allow_html=True)

ftitle = open('texts/lp_frontpage_intro.txt', 'r')
st.write(ftitle.read())
st.markdown(':red[To add introductory text to the project and the website.  ]')