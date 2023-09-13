import datetime
import os
import pandas as pd
import re
import streamlit as st


st.set_page_config(
    page_title="Dead Sea Scrolls Exhibitions in the 20th and 21st Centuries",
    layout="wide", page_icon='assets/Icon.png',
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
                output += '<li>' + item + '</li>'
        output += '</ol>' if ordered else '</ul>'
    else:
        output = items[0]
    return output


def format_date(df_date):
    dd = str(df_date.day)
    mm = df_date.strftime('%B')
    yy = str(df_date.year)
    return ' '.join([dd, mm, yy])

def format_markdown_longline(col, cell):
    st.markdown('**' + col + ':** <br>' + cell, unsafe_allow_html=True)

def format_markdown_shortline(col, cell):
    st.markdown('**' + col + ':** ' + cell, unsafe_allow_html=True)


def format_markdown(df_row, rotation=False):
    # Exhibition name
    st.markdown('<h5>' + df_row.Exhibition + '</h5>\n\n', 
                unsafe_allow_html=True)

    # Venue and location
    output = ''
    if not pd.isna(df_row.Venue):
        output += df_row.Venue + ', '
    if not pd.isna(df_row.Location):
        output += df_row.Location
    st.markdown(output, unsafe_allow_html=True)
    
    # Visitors and guide
    if not pd.isna(df_row._9):
        format_markdown_shortline('Numbers of visitors', df_row._9)
    if not pd.isna(df_row.Guide):
        format_markdown_shortline('Guide', df_row.Guide)

    # # Exhibited items
    # output += '<p>**Dead Sea Scrolls exhibited:** '
    # if pd.isna(df_row._7):
    #     output += 'Unknown'
    # else:
    #     output += '</br>' + format_list(df_row._7, delimiter=';', ordered=False)
    # output += '</p>'
    # if not pd.isna(df_row._10):
    #     output += '<p>**Other items exhibited:** </br>' + \
    #         format_list(df_row._10, delimiter=';', ordered=False) + '</p>'
    
    # # Sources
    # output += '<p>**Sources:** '
    # if pd.isna(df_row.Sources):
    #     output += '-'
    # else:
    #     output += '</br>' + format_list(df_row.Sources, delimiter='\n\n', ordered=False)
    # output += '</p>'

    # st.markdown(output, unsafe_allow_html=True)


def overview(df):
    
    df['Start Date'] = pd.to_datetime(df['Start Date']).dt.date
    df['End Date'] = pd.to_datetime(df['End Date']).dt.date

    st.dataframe(df.iloc[:, :-2], hide_index=True)


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
        
        if pd.isna(row.Rotation):
            startdate = format_date(row._2)
            enddate = '' if pd.isna(row._3) else ' - ' + format_date(row._3)
            permanent = True if pd.isna(row._3) else False
            title = 'Permanent exhibition since ' + startdate if \
                permanent else (startdate + enddate)
            with st.expander(title):
                format_markdown(row)
        else:
            rot_id, rot_n, rot_order = row.Rotation.split(';')
            if rot_order == '1':
                temp = results[results.Rotation == results.Rotation]
                idx = []
                for i in range(int(rot_n)):
                    q = ';'.join([rot_id, rot_n, str(i+1)])
                    idx.append(temp.index[temp.Rotation == q][0])
                
                inrotation = df.iloc[idx]
                title = format_date(inrotation.iloc[0]['Start Date']) + ' - ' +\
                    format_date(inrotation.iloc[-1]['End Date'])
                with st.expander(title):
                    st.markdown(':red[Exhibition with rotation still under construction]')
                    #format_markdown(inrotation, rotation=True)


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