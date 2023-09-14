import numpy as np
import os
import pandas as pd
# import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Post-2002 Dead Sea Scrolls-like Fragments",
    layout="wide", page_icon='assets/Icon.png'
)

def five_colors():
    return ['#262622', '#D98E32', '#8C503A', '#D98162', '#D9AB9A']

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

def format_markdown(col_names, row, skip=0, searchres=False):
    col_stop = -2 # To not include content and canonical grouping information
    for col, cell in zip(col_names[skip:col_stop], row[skip+1:col_stop]):
        if not pd.isna(cell):
            cell = cell.replace('$', '\$')
            # if searchres:
            #     cell = cell.replace(r'\bis\s+(Nr\s*\d+)', r'(\1)', regex=True)
            if col.lower().startswith('purchase'):
                format_markdown_purchase(col, cell)
            elif col.lower().startswith('asking'):
                format_markdown_longline(col, cell)
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


# def content_graph(sub_df, groups):
#     data = []
#     for val, cnt in df['Content group'].value_counts().items():
#         label, order = val.split(', ')
#         canon = sub_df[sub_df['Content group'] == val].iloc[0]['Canonical group']
#         data.append([int(order), label, cnt, canon])
#     data.sort(key=lambda x: int(x[0]))
#     data = np.array(data)[:, 1:]
    
#     # Plot chart
#     bar = pd.DataFrame(
#         {'Canonical distribution':data[:, 0], 'Number of fragments':data[:, 1],
#          'Canonical group':data[:, 2]})
#     fig = px.bar(
#         bar, x='Canonical distribution', y='Number of fragments', 
#         color='Canonical group', 
#         color_discrete_sequence=px.colors.qualitative.Safe)
#     fig.update_xaxes(tickangle=-45)
#     fig.update_yaxes(range=[0, 13])
#     st.plotly_chart(fig, use_container_width=True)
#     st.write('##')


def content(df):
    sub_df = df[['Content group', 'Canonical group']]
    groups = [g.split(', ') for g in df['Content group'].unique()]
    groups.sort(key=lambda x: int(x[1]))

    st.markdown(':red[Visualisation temporarily removed]')
    # content_graph(sub_df, groups)

    options = [x[0] for x in groups]
    content_selected = st.selectbox(
        'Select the content group', options=options)
    st.write('##')
    hits = st.empty()

    results = df.loc[df['Content group'].str.startswith(content_selected)]
    for row in results.itertuples():
        with st.expander(row.Content):
            format_markdown(list(df.columns.values), row, skip=2)
            
    counter = len(results)
    if counter == 0:
        txt = ':red[No entries found]'
    else:
        txt = ':blue[' + str(counter) + ' of ' + str(len(df)) + ' hits]'
    hits.markdown(txt, unsafe_allow_html=True)
                

def collectors(df):
    query = st.text_input('Enter collector name', '').lower()
    st.markdown(
        '<sup>Type in the name of a collector to show all Sales and Donations rec'\
        'orded with the collector. You can also use the keyword "NOT", e.g., "NOT'\
        ' Kando" to show all materials recorded without the name "Kando".</sup>', 
        unsafe_allow_html=True)
    st.write('##')
    hits = st.empty()

    # Check negation
    neg_flag = False
    if query.startswith('not'):
        neg_flag = True
        query = ''.join(query.split(' ')[1:])

    results = None
    if neg_flag:
        results = df[~df["Sales (➤) and Donations (➢)"].str.lower().str.contains(query)]
    else:
        results = df[df["Sales (➤) and Donations (➢)"].str.lower().str.contains(query)]

    for row in results.itertuples():
        with st.expander(row.Content):
            format_markdown(list(df.columns.values), row, skip=2)

    st.write('##')
    counter = len(results)
    if counter == 0:
        txt = ':red[No entries found]'
    else:
        txt = ':blue[' + str(counter) + ' of ' + str(len(df)) + ' hits]'
    hits.markdown(txt, unsafe_allow_html=True)


def search(df):
    df1 = df.copy()

    post_query = str(st.text_input('Enter query', ''))
    st.write('##')
    hits = st.empty()

    txt = ''
    counter = 0
    if len(post_query) > 0:
        mask = np.column_stack(
            [df1[col].str.contains(post_query, case=False, na=False) \
             for col in df1])
        results = df1.loc[mask.any(axis=1)]
        counter = len(results)

        for res in results.itertuples():

            with st.expander(res.Content):
                format_markdown(df1.columns.values, res)

        if counter == 0:
            txt = ':red[No entries found]'
        else:
            txt = ':blue[' + str(counter) + ' of ' + str(len(df1)) + ' hits]'

    hits.markdown(txt, unsafe_allow_html=True)


def overview(df):
    st.markdown(
        'In the table below, you can browse our database in its entirety. Note that an'\
        ' option to view the table as a full page will show up on the top right of the'\
        ' table when you hover the table.', unsafe_allow_html=True)
    df1 = df.copy()
    st.dataframe(df1.iloc[:, :-2], hide_index=True)


dbf = os.getcwd() + '/data/post2002DB-v2.xlsx'
df = pd.read_excel(dbf, dtype=str)

# Selection of columns to show and process in this page
cols = list(range(0, 22))
cols = [x for x in cols if x not in [4, 17, 18]]
df = df.iloc[:, cols]

st.header('The Post-2002 Dead Sea Scroll-like fragments')

authors = 'Ludvik A. Kjeldsberg ' + format_markdown_orcid('0000-0001-5268-4983') + ', '
authors += 'Årstein Justnes ' + format_markdown_orcid('0000-0001-6448-0507') + ', and '
authors += 'Hilda Deborah ' + format_markdown_orcid('0000-0003-3779-2569')
st.markdown('By ' + authors, unsafe_allow_html=True)
st.markdown('##')

ftitle = open('assets/texts/lp_post_intro.txt', 'r')
st.markdown(
    '<div style="text-align: justify;">'+ftitle.read()+'</div>', unsafe_allow_html=True)
st.markdown('##')

tabs = st.tabs(['Overview', 'Filter collector', 'Filter content', 
                'Search'])


tab_collector = tabs[0]
with tab_collector:
    st.write('##')
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

