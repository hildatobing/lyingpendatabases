import matplotlib.colors as mplc
import numpy as np
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Post-2002 Dead Sea Scrolls-like Fragments",
    page_icon='assets/Icon.png'
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


def content_histogram(sub_df, groups):
    data = []
    for val, cnt in df['Content Group'].value_counts().items():
        label, order = val.split(', ')
        canon = sub_df[sub_df['Content Group'] == val].iloc[0]['Canonical Group']
        data.append([int(order), label, cnt, canon])
    data.sort(key=lambda x: int(x[0]))
    data = np.array(data)[:, 1:]
    
    # Plot chart
    bar = pd.DataFrame(
        {'Texts':data[:, 0], 'Number of fragments':data[:, 1],
         'Text groups':data[:, 2]})
    fig = px.bar(
        bar, x='Texts', y='Number of fragments', 
        color='Text groups', title='Post-2002 fragments\' textual distribution',
        color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_xaxes(tickangle=-45)
    fig.update_yaxes(range=[0, 13])
    st.plotly_chart(fig, use_container_width=True)
    st.write('##')


def content(df):
    sub_df = df[['Content Group', 'Canonical Group']]
    groups = [g.split(', ') for g in df['Content Group'].unique()]
    groups.sort(key=lambda x: int(x[1]))

    content_histogram(sub_df, groups)

    options = [x[0] for x in groups]
    content_selected = st.selectbox(
        'Select a grouping option', options=options)
    st.write('##')
    hits = st.empty()

    results = df.loc[df['Content Group'].str.startswith(content_selected)]
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
        '<sup>Type in the name of a collector to show all Sale, Donation, and Col'\
        'laboration recorded with the collector. You can also use the keyword "NO'\
        'T", e.g., "NOT Kando" to show all materials recorded without the name "K'\
        'ando".</sup>', unsafe_allow_html=True)
    st.write('##')
    hits = st.empty()

    # Check negation
    neg_flag = False
    if query.startswith('not'):
        neg_flag = True
        query = ''.join(query.split(' ')[1:])

    results = None
    col_names = df.columns.values.tolist()
    sale_col = [col for col in col_names if col.startswith('Sale')][0]
    if neg_flag:
        results = df[~df[sale_col].str.lower().str.contains(query)]
    else:
        results = df[df[sale_col].str.lower().str.contains(query)]

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
                format_markdown(df1.columns.values, res, skip=2)

        if counter == 0:
            txt = ':red[No entries found]'
        else:
            txt = ':blue[' + str(counter) + ' of ' + str(len(df1)) + ' hits]'

    hits.markdown(txt, unsafe_allow_html=True)


def get_rgba_hex(color_array, alpha=.8):
    '''
    To convert add transparencies to given color array
    '''
    ishex = True if color_array[0].startswith('#') else False
    rgba_tuples, hex = [], []
    rgb = None
    if ishex:
        rgb = np.array([mplc.to_rgb(x) for x in color_array]) * 255
        hex = color_array.copy()
    else:
        rgblist = []
        for rgbstr in color_array:
            rgblist.append([int(x)/255. for x in rgbstr[4:-1].split(', ')])
        rgb = np.array(rgblist) * 255.
        hex = [mplc.to_hex(x).upper() for x in rgblist]

    for x in rgb:
        rgba_tuples.append(
            'rgba(' + ','.join([str(int(i)) for i in x[:3]]) + \
            ',' + str(alpha) + ')')
        
    return rgba_tuples, hex

def gallery():
    sankeyf = os.getcwd() + '/data/post2002-sankeyvis-changeofhands.csv'
    sankeydf = pd.read_csv(sankeyf, sep=';', encoding='utf-8')
    
    # The operation '|' is a set union
    set_nodes = set(sankeydf['Seller']) | set(sankeydf['Buyer'])
    dict_nodes = dict(zip(set_nodes, np.arange(len(set_nodes))))

    cmap_colors = [x for x in px.colors.qualitative.T10_r]
    rgba, hex = get_rgba_hex(cmap_colors, alpha=0.8)

    source, target, count = [], [], []
    sankeynp = sankeydf.to_numpy()
    for i in range(len(sankeynp)):
        row = sankeynp[i, :]
        source.append(dict_nodes[row[0]])
        target.append(dict_nodes[row[1]])
        count.append(int(row[2]))
    fig = go.Figure(data=[go.Sankey(
        arrangement = 'snap',
        node = {"label": list(set_nodes), "thickness":35, "pad":10,
                "color": [hex[i % len(hex)] for i in np.arange(len(set_nodes))],},
        link = {"source": source, "target": target, "value": count,#}
                "color": [rgba[i % len(hex)] for i in source]}
    )])
    fig.update_layout(
        title_text='Flow diagram of the sale and donation of Post-2002 Fragments', height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        '**Abbreviations:** \n - LMI: Legacy Ministries International \n - ATS: Ashland '\
        'Theological Seminary \n - APU: Azusa Pacific University \n - SBTS: Southwestern'\
        ' Baptist Theological Seminary \n - NCF: National Christian Foundation',
        unsafe_allow_html=True)
    st.caption(
        '**Note:** The actor "RE: William Kando" is the same as "William Kando". They '\
        'are shown as different actors to avoid having a looped connection for the same'\
        'actor, which will significantly reduce the readability of this visualisation.'
    )
    st.write('##')
    

def overview(df):
    st.markdown(
        'In the table below, you can browse our database in its entirety. Note that an'\
        ' option to view the table as a full page will show up on the top right of the'\
        ' table when you hover the table.', unsafe_allow_html=True)
    df1 = df.copy()
    st.dataframe(df1.iloc[:, :-2], hide_index=True)


dbf = os.getcwd() + '/data/post2002DB-v2-1.xlsx'
df = pd.read_excel(dbf, dtype=str)

# Selection of columns to show and process in this page
cols = list(range(0, 23))
cols = [x for x in cols if x not in [1, 18, 19]]
# print(cols)
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

tabs = st.tabs(['Overview', 'Filter content', 'Search', 'Gallery'])


tab_overview = tabs[0]
with tab_overview:
    st.write('##')
    overview(df)

tab_content = tabs[1]
with tab_content:
    st.write('##')
    content(df)

tab_search = tabs[2]
with tab_search:
    st.write('##')
    search(df)

tab_gallery = tabs[3]
with tab_gallery:
    st.write('##')
    gallery()