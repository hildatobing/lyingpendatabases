import os
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Post-2002 Dead Sea Scrolls-like Fragments",
    layout="wide", page_icon='assets/Icon.png'
)

def align(text, alignment='left'):
    return '<div style="text-align:' + alignment + '>' + text + '</div>'

def format_markdown_list(col, cell, delimiter='', ordered=False):
    items = cell.split(delimiter)
    output = ''
    if len(items) > 1:
        output = '<ol>' if ordered else '<ul>'
        for item in items:
            if not item.isspace():
                output += '<li>' + item + '</li>'
        output += '</ol>' if ordered else '</ul>'
    else:
        output = items[0]
    format_markdown_longline(col, output)

def format_markdown_longline(col, cell):
    st.markdown('**' + col + ':** <br>' + str(cell), unsafe_allow_html=True)

def format_markdown_shortline(col, cell):
    st.markdown('**' + col + ':** ' + str(cell), unsafe_allow_html=True)

def format_markdown_purchase(col, cell):
    bold, reg = col.split('\n')
    st.markdown(
        '**' + bold + '** (' + reg + ')**:** <br>' + str(cell), 
        unsafe_allow_html=True)
    
def format_markdown_orcid(orcid):
    return '<sup>[![](https://info.orcid.org/wp-content/uploads/2019/11/'\
        'orcid_16x16.png)](https://orcid.org/' + orcid + ')</sup>'

def format_markdown(col_names, row, mode=0):
    skip = 4 if mode == 0 else 1
    for col, cell in zip(col_names[skip:-1], row[skip+1:-1]):
        if not pd.isna(cell):
            cell = cell.replace('$', '\$')
            if col.lower().startswith('purchase'):
                format_markdown_purchase(col, cell)
            elif col.lower() == 'sources':
                format_markdown_list(
                    col, cell, delimiter='\n\n', ordered=False)
            else:
                if len(cell) < 50:
                    format_markdown_shortline(col, cell)
                else:
                    format_markdown_longline(col, cell)
        else:
            if col.lower().startswith('purchase'):
                format_markdown_purchase(col, 'Unknown')
            elif col.lower().startswith('asking'):
                format_markdown_longline(col, 'Unknown')
    

def content(df):
    groups = [g.split(', ') for g in df['Content group'].unique()]
    groups.sort(key=lambda x: int(x[1]))

    options = [x[0] for x in groups]
    content_selected = st.selectbox(
        'Select the content group', options=options)
    st.write('##')
    hits = st.empty()

    results = df.loc[df['Content group'].str.startswith(content_selected)]
    for row in results.itertuples():
        with st.expander(row.Name.lstrip('0123456789. ')):
            format_markdown(list(df.columns.values), row)
            
    counter = len(results)
    if counter == 0:
        txt = ':red[No entries found]'
    else:
        txt = ':blue[' + str(counter) + ' of ' + str(len(df)) + ' hits]'
    hits.markdown(txt, unsafe_allow_html=True)
                

def collectors(df):
    query = st.text_input('Enter collector name', '').lower()
    st.markdown(
        '<sup>Type in the name of a collector to show all materials rec'\
        'orded with the name. You can also use the keyword "NOT", e.g.,'\
        ' "NOT Kando" to show all materials recorded without the name.'\
        'Note that not all information available on the fragment is sho'\
        'wn here. Refer to the Overview tab to read all information.'\
        '</sup>', unsafe_allow_html=True)
    st.write('##')
    hits = st.empty()

    # Check negation
    neg_flag = False
    if query.startswith('not'):
        neg_flag = True
        query = ''.join(query.split(' ')[1:])

    results = None
    if neg_flag:
        results = df[~df["Collector(s)/Collection(s)"].str.lower().str.contains(query)]
    else:
        results = df[df["Collector(s)/Collection(s)"].str.lower().str.contains(query)]

    for row in results.itertuples():
        with st.expander(row.Name.lstrip('0123456789. ')):
            format_markdown(list(df.columns.values), row)

    st.write('##')
    counter = len(results)
    if counter == 0:
        txt = ':red[No entries found]'
    else:
        txt = ':blue[' + str(counter) + ' of ' + str(len(df)) + ' hits]'
    hits.markdown(txt, unsafe_allow_html=True)


def search(df):
    query = str(st.text_input('Enter a keyword', ''))
    st.markdown(
        ':red[<sup>UNDER CONSTRUCTION.</sup>]', unsafe_allow_html=True)
    hits = st.empty()
    st.write('##')


def overview(df):
    # Selecting columns to show
    cols = list(range(1, 17))
    cols.append(19)
    st.dataframe(df.iloc[:, cols], hide_index=True)


dbf = os.getcwd() + '/data/post2002DB-v2.xlsx'
df = pd.read_excel(dbf, dtype=str)


st.header('A Database of Post-2002 Dead Sea Scrolls-like Fragments')

authors = 'Ludvik A. Kjeldsberg ' + format_markdown_orcid('0000-0001-5268-4983') + ', '
authors += 'Årstein Justnes ' + format_markdown_orcid('0000-0001-6448-0507') + ', and '
authors += 'Hilda Deborah ' + format_markdown_orcid('0000-0003-3779-2569')
st.markdown('By ' + authors, unsafe_allow_html=True)
st.markdown('##')

st.markdown(
    'Since 2002, more than 100 "new" Dead Sea Scrolls-like fragments have '\
    'appeared on the antiquities market. The researchers in the Lying Pen of'\
    ' Scribes have made great efforts in catalouging these fragments. :red['\
    '(To be updated)]')
st.markdown('##')

tabs = st.tabs(['Overview', 'Filter collector', 'Filter content', 
                'Search keyword'])


tab_collector = tabs[0]
with tab_collector:
    # st.write('##')
    overview(df)

tab_collector = tabs[1]
with tab_collector:
    st.write('##')
    collectors(df)

tab_content = tabs[2]
with tab_content:
    st.write('##')
    content(df)

tab_search = tabs[3]
with tab_search:
    st.write('##')
    search(df)

