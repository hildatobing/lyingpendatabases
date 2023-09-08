import datetime
import os
import pandas as pd
import re
import streamlit as st


st.set_page_config(
    page_title="Dead Sea Scrolls Exhibitions in the 20th and 21st Centuries",
    layout="wide",
)


def format_with_url(text):
    url = re.search("(?P<url>https?://[^\s]+)", text)
    if url:
        url = url.group("url")
        if text.endswith(url):
            if url.endswith('.'):
                url = url[:-1]
                mdown_url = '[(Link)](' + url + ')'
                text = text.replace(url + '.', mdown_url)
            else:
                mdown_url = '[(Link)](' + url + ')'
                text = text.replace(url, mdown_url)
    return text


def format_list(items, delimiter='', ordered=False):
    items = items.split(delimiter)
    if len(items) > 1:
        output = '<ol>' if ordered else '<ul>'
        for item in items:
            if not item.isspace():
                # This is assuming that ordered list will only be used for Sources,
                # where we would need to clean up the shown url
                if ordered:
                    output += '<li>' + format_with_url(item) + '</li>'
                # Unordered/bullet point list is used for exhibited items
                else:
                    output += '<li>' + item + '</li>'
        output += '</ol>' if ordered else '</ul>'
    else:
        if ordered:
            output = format_with_url(items[0])
        else:
            output = items[0]
    return output


def format_date(df_date):
    dd = str(df_date.day)
    mm = df_date.strftime('%B')
    yy = str(df_date.year)
    return ' '.join([dd, mm, yy])


def format_markdown(df_row):
    # Exhibition name
    output = '<h5>' + df_row.Exhibition + '</h5>\n\n'

    # Venue and location
    if not pd.isna(df_row.Venue):
        output += df_row.Venue + ', '
    if not pd.isna(df_row.Location):
        output += df_row.Location
    
    # Visitors and guide
    output += '<p>'
    if not pd.isna(df_row._9):
        output += '**Numbers of visitors:** ' + str(df_row._9)
    if not pd.isna(df_row.Guide):
        output += '**Guide:** ' + df_row.Guide
    output += '</p>'

    # Exhibited items
    output += '<p>**Dead Sea Scrolls exhibited:** '
    if pd.isna(df_row._7):
        output += 'Unknown'
    else:
        output += '</br>' + format_list(df_row._7, delimiter=';', ordered=False)
    output += '</p>'
    if not pd.isna(df_row._10):
        output += '<p>**Other items exhibited:** </br>' + \
            format_list(df_row._10, delimiter=';', ordered=False) + '</p>'
    
    # Sources
    output += '<p>**Sources:** '
    if pd.isna(df_row.Sources):
        output += '-'
    else:
        output += '</br>' + format_list(df_row.Sources, delimiter='\n\n', ordered=True)
    output += '</p>'

    st.markdown(output, unsafe_allow_html=True)


def overview(df):
    st.markdown(
        '<sup>Below are all color description entries found in the database. The '\
        'header or column name is clickable, and is useful to sort the database b'\
        'ased on the selected column, either in ascending or descending order.'\
        '</sup>', unsafe_allow_html=True)
    
    df['Start Date'] = pd.to_datetime(df['Start Date']).dt.date
    df['End Date'] = pd.to_datetime(df['End Date']).dt.date

    st.dataframe(df.iloc[:, :-4], hide_index=True)


def decade(df):
    options = sorted(df['Decade'].unique())
    content_selected = st.selectbox(
        'Select a decade', options=options)
    # st.markdown(
    #     '<sup>Select a decade from the dropdown list.</sup>', unsafe_allow_html=True)
    st.write('##')
    hits = st.empty()
    
    results = df.loc[df['Decade'] == content_selected]
    for row in results.itertuples():
        enddate = '' if pd.isna(row._3) else ' - ' + format_date(row._3)
        with st.expander(format_date(row._2) + enddate):
            format_markdown(row)

    counter = len(results)
    if counter == 0:
        txt = ':red[No entries found]'
    else:
        txt = ':blue[' + str(counter) + ' entries found]'
    hits.markdown(txt, unsafe_allow_html=True)


def render_map(df):

    fig = go.Figure(go.Scattergeo(
        lat=df['Latitude'],
        lon=df['Longitude'],
        mode='markers',
        text=df['Venue']))
    st.plotly_chart(fig)


dbf = os.getcwd() + '/data/exhibition-v2.xlsx'
df = pd.read_excel(dbf, dtype=str)

st.header('Dead Sea Scrolls Exhibitions in the 20th and 21st Centuries')
st.markdown(
    '<sup>By Ludvik A. Kjeldsberg</sup>', 
    unsafe_allow_html=True)
st.write(
    'Since first being exhibited at the Library of Congress in Washington (DC), the Dead '\
    'Sea Scrolls have been featured in more than one hundred and sixty different exhibiti'\
    'ons worldwide. These exhibitions span over seven decades, from 1949 to the late 2010'\
    's, and over six continents. But most of them have taken place in the US. This articl'\
    'e describes a database of these exhibitions. The database contains information about'\
    ' exhibition venues, dates, curators, et cetera, manually collected and catalogued.')




tabs = st.tabs(['Overview', 'Filter decade'])


tab_collector = tabs[0]
with tab_collector:
    st.write('##')
    overview(df)

tab_collector = tabs[1]
with tab_collector:
    st.write('##')
    decade(df)