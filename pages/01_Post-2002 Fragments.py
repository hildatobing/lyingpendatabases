import os
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Lying Pen | Post-2002 DSS-like Fragments",
)

def format_markdown(df_columns, df_row, mode=0):
    for col in df_columns:
        # Handling for collector's browse, mention unknown if purchase price info unavailable
        if mode == 1:
            if 'purchase' in col.lower() or 'price' in col.lower():
                if pd.isnull(df_row[col]):
                    df_row[col] = '<br>Unknown'

        if not pd.isnull(df_row[col]):
            ws = ' ' if len(str(df_row[col])) < 80 else '<br>'
            cell = str(df_row[col]).replace('$', '\$')
            if '\nDealer' in col:
                col = col.replace('\n', '<br>')
            st.markdown('**' + col + '**:' + ws + str(cell), unsafe_allow_html=True)

def content(df):
    
    options = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 
               'Minor Prophets', 'Major Prophets', 'Unidentified']
    minor = ['hos', 'joel', 'amos', 'obad', 'jonah', 'mic', 'hab', 'nah',
             'zeph', 'hag', 'zac', 'mal']
    major = ['isa', 'jer', 'ezek', 'dan']
    cluster = ['gen', 'exod', 'lev', 'num', 'deut', minor, major, 'unident']
    content_selected = st.selectbox(
        'Select the content group', options=options)
    st.markdown(
        '<sup>Select a grouping from the dropdown list. In the future, '\
        'free text entry will also be allowed. The following groups inc'\
        'lude:\n <b>Minor Prophets</b> - Hosea, Joel, Amos, Obadiah, Jo'\
        'nah, Micah, Nahum, Habbakuk, Zephaniah, Haggai, Zechariah, and'\
        'and Malachi. <b>Major Prophets</b> - Isaiah, Jeremiah, Lamenta'\
        'tions, Ezekiel, and Daniel. Note that not all information avai'\
        'lable on the fragment is shown here. Refer to the Overview tab'\
        ' to read all information.</sup>', unsafe_allow_html=True)
    st.write('##')
    hits = st.empty()

    query = cluster[options.index(content_selected)]
    df = df.reset_index()

    counter = 0
    column_names = list(df.columns.values)
    for i, row in df.iterrows():
        if 'joel' in query or 'isa' in query:
            for q in query:
                if q in row['Content'].lower():
                    skip = 3
                    with st.expander(row['Name'].lstrip('0123456789. ')):
                        format_markdown(column_names[skip:], row[skip:])
                    counter += 1
        else:
            if query in row['Content'].lower():
                skip = 3
                with st.expander(row['Name'].lstrip('0123456789. ')):
                    format_markdown(column_names[skip:], row[skip:])
                counter += 1


    if counter == 0:
        txt = ':red[No entries found]'
    else:
        txt = ':blue[' + str(counter) + ' of ' + str(len(df)) + ' hits]'
    hits.markdown(txt, unsafe_allow_html=True)
                

def align(text, alignment='left'):
    return '<div style="text-align:' + alignment + '>' + text + '</div>'


def collectors(df):
    query = st.text_input('Enter collector name', '')
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
    if query.lower().startswith('not'):
        neg_flag = True
        query = ''.join(query.split(' ')[1:])

    skip = 3
    column_names = [
        'DSS F. Name', 'Content', 'Alleged Provenance', 'Collector(s)/Collection(s)', 
        'Asking price', 'Purchase Price\nDealer/Seller ➤ Collector/Buyer']

    counter = 0
    for i, row in df.iterrows():
        if neg_flag:
            if not(query.lower() in row['Collector(s)/Collection(s)'].lower()):
                with st.expander(row['Name'].lstrip('0123456789. ')):
                    format_markdown(column_names, row[skip:], mode=1)
                counter += 1
        else:
            if query.lower() in row['Collector(s)/Collection(s)'].lower():
                with st.expander(row['Name'].lstrip('0123456789. ')):
                    format_markdown(column_names, row[skip:], mode=1)
                counter += 1

    st.write('##')
    if counter == 0:
        txt = ':red[No entries found]'
    else:
        txt = ':blue[' + str(counter) + ' of ' + str(len(df)) + ' hits]'
    hits.markdown(txt, unsafe_allow_html=True)


def overview(df):
    st.dataframe(df.iloc[:, 1:], hide_index=True)



# st.sidebar.title('Navigation')
# options = st.sidebar.radio(
#     'Pages', options=['Overview', 'Browse content', 'Browse collectors'])

dbf = os.getcwd() + '/databases/post2002DB.xlsx'
df = pd.read_excel(dbf, dtype=str)


st.header('A Database of Post-2002 Dead Sea Scrolls-like Fragments')
st.markdown(
    '<sup>By Ludvik A. Kjeldsberg, Årstein Justnes, and Martin Stomnås</sup>', 
    unsafe_allow_html=True)

st.write(
    'Since 2002, more than 100 "new" Dead Sea Scrolls-like fragments have '\
    'appeared on the antiquities market. The researchers in the Lying Pen of'\
    ' Scribes have made great efforts in catalouging these fragments. \n\n'\
    'This page contains the overview of the whole database, and several opti'\
    'ons to filter the database based on, e.g., content or collector. Use the'\
    'tabs below to toggle between the overview and different filter options.')

tabs = st.tabs(['Overview', 'Filter collector', 'Filter content'])


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
