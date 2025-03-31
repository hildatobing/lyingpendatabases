from authorship import show_authors
from datetime import datetime
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import sqlite3 as sql
import streamlit as st


def colors_RGB_to_01_scale(rgb):
    rgb = rgb[4:-1].split(',')
    return [int(x) / 255.0 for x in rgb]


# Generate a continuous color scale between blue and red of Safe discrete colors
def colors_continuousSafe(ncolors=256):
    blue, red = px.colors.qualitative.Safe[0:2]
    cmap = LinearSegmentedColormap.from_list(
        "Safe_bluered_scale", [colors_RGB_to_01_scale(blue), 
                               colors_RGB_to_01_scale(red)])
    continuous_blue_red = [cmap(i/ncolors) for i in range(ncolors)]
    safe_colorscale = [
        [i/(len(continuous_blue_red)-1), 
         f'rgba({int(c[0]*255)}, {int(c[1]*255)}, {int(c[2]*255)}, {c[3]})'] \
         for i, c in enumerate(continuous_blue_red)]
    return safe_colorscale


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


def format_list(col, items, delimiter='', showifnone=False, ordered=False):
    emptylist = False
    flagone = False
    output = ''
    if items is None:
        output = ' Unknown'
        emptylist = True
    else:
        items = items.split(delimiter)
        if len(items) > 1:
            output = '<ol>' if ordered else '<ul>'
            for item in items:
                if not item.isspace():
                    url = re.search("(?P<url>https?://[^\s]+)", item)
                    if url:
                        url = url.group("url")
                        item = item.replace(url, '[(URL)](%s)' %url)
                    output += '<li>' + item + '</li>'
            output += '</ol>' if ordered else '</ul>'
        else:
            flagone = True
            if len(items[0]) > 30:
                output += '<br>' + items[0]
            else:
                output = items[0]
    
    if col == 'Sources' and flagone:
        col = 'Source'
    if emptylist:
        if showifnone:
            st.markdown('**' + col + ':** ' + output, unsafe_allow_html=True)
    else:
        st.markdown('**' + col + ':** ' + output, unsafe_allow_html=True)


def format_date(df_date):
    yy, mm, dd = df_date.split('-')
    mm = datetime.strptime(df_date, '%Y-%m-%d').date().strftime('%B')
    return ' '.join([dd, mm, yy])


def format_markdown_longline(col, cell):
    st.markdown('**' + col + ':** <br>' + cell, unsafe_allow_html=True)


def format_markdown_shortline(col, cell):
    st.markdown('**' + col + ':** ' + cell, unsafe_allow_html=True)


def format_markdown(row, rotation=False):
    # Exhibition name
    st.markdown('<h5>' + row.title + '</h5>\n\n', unsafe_allow_html=True)

    # Venue and location
    output = ''
    if not pd.isna(row.venue):
        output += ':classical_building: ' + row.venue + '<br>'
    if not pd.isna(row.location):
        output += ':round_pushpin: ' + row.location
    st.markdown(output, unsafe_allow_html=True)
    
    # Visitors and guide
    if not pd.isna(row.visitors):
        if len(row.visitors) > 20:
            format_markdown_longline('Numbers of visitors', row.visitors)
        else:
            format_markdown_shortline('Numbers of visitors', row.visitors)
    if not pd.isna(row.guidebook):
        format_markdown_longline('Guidebook', row.guidebook)

    # Exhibited items
    format_list('Exhibited Dead Sea Scrolls', row.exhb_dss, delimiter=',', 
                showifnone=True)
    format_list('Exhibited post-2002 fragments', row.exhb_post2002, 
                delimiter=',')
    format_list('Other exhibited items', row.exhb_oitem, delimiter=',')
    
    # Sources
    if not pd.isna(row.sources):
        sources = row.sources.replace('\n\n', ';')
        format_list('Sources', sources, delimiter=';', ordered=True)


def decade():
    # Establish connection and query all information
    conn = sql.connect('lyingpen.sqlite3')
    dec = pd.read_sql_query(
        """SELECT * FROM exhibition_v_ALL""", conn)
    conn.commit()
    conn.close()

    options = sorted(dec['decade'].unique())
    content_selected = st.selectbox('Select a decade', options=options)
    st.markdown('</br>', unsafe_allow_html=True)
    hits = st.empty()
    
    results = dec.loc[dec['decade'] == content_selected]
    for row in results.itertuples():
        # if pd.isna(row.Rotation):
        startdate = format_date(row.start_date)
        enddate = '' if pd.isna(
            row.end_date) else ' - ' + format_date(row.end_date)
        permanent = True if pd.isna(row.end_date) else False
        title = 'Permanent exhibition since ' + startdate if \
            permanent else (startdate + enddate)
        with st.expander(title):
            format_markdown(row)
    #     else:
    #         rot_id, rot_n, rot_order = row.Rotation.split(';')
    #         if rot_order == '1':
    #             temp = results[results.Rotation == results.Rotation]
    #             idx = []
    #             for i in range(int(rot_n)):
    #                 q = ';'.join([rot_id, rot_n, str(i+1)])
    #                 idx.append(temp.index[temp.Rotation == q][0])
                
    #             inrotation = df.iloc[idx]
    #             title = format_date(inrotation.iloc[0]['Start Date']) + ' - ' +\
    #                 format_date(inrotation.iloc[-1]['End Date'])
    #             with st.expander(title):
    #                 st.markdown(':red[Exhibition with rotation still under construction]')
    #                 #format_markdown(inrotation, rotation=True)

    counter = len(results)
    if counter == 0:
        txt = ':red[No entries found]'
    else:
        txt = ':blue[' + str(counter) + ' entries found]'
    hits.markdown(txt, unsafe_allow_html=True)


def overview(exhbtable):
    exhb = exhbtable.copy()
    exhb.rename({
        'start_date':'Start Date', 'end_date':'End Date', 'title':'Exhibition',
        'venue':'Venue', 'location':'Location', 'exhb_dss':'Exhibited DSS',
        'exhb_post2002':'Exhibited Post-2002 Fragments', 'guidebook':'Guidebook',
        'exhb_oitem':'Other Items Exhibited', 'visitors':'Number of Visitors',
        'sources': 'Sources'
        }, axis='columns', inplace=True)
    st.dataframe(exhb, hide_index=True)


def map_exhibition_US():
    # Establish connection and query all information
    conn = sql.connect('lyingpen.sqlite3')
    df = pd.read_sql_query(
        """SELECT E.state_id, S.state_name, S.abbrv, COUNT(S.abbrv) as count
        FROM exhibition E
        LEFT JOIN country_US_state S ON E.state_id = S.state_id
        WHERE E.country_id = '236'
        GROUP BY E.state_id, S.state_name
        ORDER BY count""", conn)
    conn.commit()
    conn.close()

    # Frequency of exhibitions in the U.S.
    title = 'Number of Exhibitions in the United States since 1949'
    fig = go.Figure(data=go.Choropleth(
        locations=df['abbrv'], z=df['count'], locationmode='USA-states', 
        colorscale=colors_continuousSafe(), autocolorscale=False, 
        text=df['state_name'], marker_line_color='black', 
        marker_line_width=.5, colorbar_title='Number of exhibitions'))
    fig.update_layout(
        title_text=title, font_family='sans-serif',
        geo=dict(scope='usa'))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        'This choropleth map visualises the number of Dead Sea Scrolls exhibit'\
        'ions held across the United States since 1949. Hover over each state '\
        'to see the exact number of exhibitions held there.')


def map_exhibition_world():
    # Establish connection and query all information
    conn = sql.connect('lyingpen.sqlite3')
    df = pd.read_sql_query(
        """SELECT E.country_id, C.name, COUNT(E.country_id) as count
        FROM exhibition E
        LEFT JOIN country C ON E.country_id = C.country_id
        GROUP BY C.name
        ORDER BY count""", conn)
    conn.commit()
    conn.close()

    # Frequency of exhibitions in the U.S.
    title = 'Number of Exhibitions Worldwide since 1949'
    fig = go.Figure(data=go.Choropleth(
        locations=df['name'], locationmode="country names", 
        colorscale=colors_continuousSafe(), text=df['name'], z=df['count'], 
        marker_line_color='black', 
        marker_line_width=.5, colorbar_title='Number of exhibitions'))
    fig.update_layout(title_text=title, font_family='sans-serif')
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        'This choropleth map visualises the number of Dead Sea Scrolls exhibit'\
        'ions held worldwide since 1949. Hover over each country to see the ex'\
        'act number of exhibitions held there. Nevertheless, it is clear that '\
        'the U.S. dominated the distribution, hosting 101 out of the total 155'\
        ' exhibitions worldwide since 1949, which accounts for 65.2%.')


def hist_exhibition():
    conn = sql.connect('lyingpen.sqlite3')
    df = pd.read_sql_query(
        """SELECT is_permanent, start_date, end_date,
            STRFTIME('%Y', start_date) AS year, COUNT(*) AS numperyear
        FROM exhibition
        GROUP BY STRFTIME('%Y', start_date)""", conn)
    conn.commit()
    conn.close()

    # Plot chart
    fig = px.bar(
        df, x='year', y='numperyear', title='Number of Exhibitions per Year',
        color_discrete_sequence=px.colors.qualitative.Safe)
    fig.add_vline(2002, line_width=2.5, line_color=px.colors.qualitative.Safe[1])
    fig.update_xaxes(tickangle=-45, title='Year', tick0=1950, dtick=5)
    fig.update_yaxes(
        range=[0, df['numperyear'].max()+4], title='Number of exhibitions')
    fig.add_annotation(
        x=2000.5, y=9, text='2002, New fragments started to emerge',
        showarrow=False, font=dict(size=12, color='black'), textangle=-90)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        'This diagram shows the number of Dead Sea Scrolls exhibitions every y'\
        'ear since its discovery. Hover over each bar to see the exact'\
        ' number of exhibitions held that year. The red line annotated "2002, '\
        'New fragments started to emerge" marked the year 2002 where the so-ca'\
        'lled Post-2002 Dead Sea Scrolls-like Fragments started to emerge. It '\
        'can be observed how the demand for the scrolls increased post-2002 co'\
        'mpared to the years and decades before that. The [Post-2002 Fragments'\
        '](%s) database is also available in this platform.' %(
        'https://lyingpendatabases.streamlit.app/Post2002'))
    st.markdown('</br>', unsafe_allow_html=True)


def visualisation():
    hist_exhibition()
    st.divider()
    map_exhibition_world()
    st.divider()
    map_exhibition_US()


def search(df):
    df1 = df.copy()

    post_query = str(st.text_input('Enter query', ''))
    st.markdown('</br>', unsafe_allow_html=True)
    hits = st.empty()

    txt = ''
    counter = 0
    if len(post_query) > 0:
        mask = np.column_stack(
            [df1[col].astype(str).str.contains(post_query, case=False, na=False) \
             for col in df1])
        results = df1.loc[mask.any(axis=1)]
        counter = len(results)

        for res in results.itertuples():
            title = 'Permanent exhibition since ' + format_date(res.start_date) if \
                pd.isna(res.end_date) else format_date(res.start_date) + ' - ' + \
                format_date(res.end_date)
            with st.expander(title):
                format_markdown(res)

        if counter == 0:
            txt = ':red[No entries found]'
        else:
            txt = ':blue[' + str(counter) + ' of ' + str(len(df1)) + ' hits]'

    hits.markdown(txt, unsafe_allow_html=True)


def getalldata():
    # Establish connection and query all information
    conn = sql.connect('lyingpen.sqlite3')
    exhb = pd.read_sql_query(
        """SELECT * FROM exhibition_v_ALL""", conn)
    conn.commit()
    conn.close()
    
    cols = ['start_date', 'end_date', 'title', 'venue', 'location', 'exhb_dss',
            'exhb_post2002', 'exhb_oitem', 'guidebook', 'visitors', 'sources']
    exhb = exhb[cols]

    exhb['exhb_dss'] = exhb['exhb_dss'].str.replace(',', '; ')
    exhb['exhb_oitem'] = exhb['exhb_oitem'].str.replace(',', '; ')
    exhb['exhb_post2002'] = exhb['exhb_post2002'].str.replace(',', '; ')
    
    return exhb



exhbtable = getalldata()

st.header('Dead Sea Scrolls Exhibitions in the 20th and 21st Centuries')
authors = show_authors(['ludvikak', 'hildad'])
st.markdown('By ' + authors, unsafe_allow_html=True)
st.write('##')

st.write(
    'Since first being exhibited at the Library of Congress in Washington (DC)'\
    ', the Dead Sea Scrolls have been featured in more than 150 different exhi'\
    'bitions worldwide. These exhibitions span over seven decades, from 1949 t'\
    'o the late 2010s, and over six continents. But most of them have taken pl'\
    'ace in the US. This article describes a database of these exhibitions. Th'\
    'e database contains information about exhibition venues, dates, curators,'\
    ' et cetera, manually collected and catalogued.')


with st.expander('Cite this database'):
    apa = 'Kjeldsberg, L. A. & Deborah, H. (2025). A Database of Dead Sea Scro'\
        'lls Exhibitions in the 20th and 21st Centuries. <i>In preparation</i>.'
    st.markdown(apa, unsafe_allow_html=True)

st.markdown('</br>', unsafe_allow_html=True)
tabs = st.tabs(
    ['Overview', 'Filter by Decade', 'Visualisation Gallery', 'Search'])

tab_overview = tabs[0]
with tab_overview:
    st.markdown('</br>', unsafe_allow_html=True)
    overview(exhbtable)

tab_decade = tabs[1]
with tab_decade:
    st.markdown('</br>', unsafe_allow_html=True)
    decade()

tab_vis = tabs[2]
with tab_vis:
    st.markdown('</br>', unsafe_allow_html=True)
    visualisation()

tab_search = tabs[3]
with tab_search:
    st.markdown('</br>', unsafe_allow_html=True)
    search(exhbtable)