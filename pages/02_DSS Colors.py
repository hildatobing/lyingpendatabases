from authorship import show_authors

import os
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="The Colors of the Dead Sea Scrolls Fragments",
    page_icon='assets/Icon.png',
)


def capfirst(s):
    return s[:1].upper() + s[1:]


def format_markdown(df_row, mode=0):
    col_desc = '\"' + capfirst(df_row._4).removeprefix(
        'Papyrus colour: ').removeprefix('Colour: ') + '\"'
    ms = ' (' + df_row.Manuscript
    if not pd.isnull(df_row._2):
        ms += ' &ndash; ' + df_row._2
    if not pd.isnull(df_row._6):
        ms += ' &ndash; Resp. editor(s): ' + df_row._6

    # Standard output for DJD entries
    output = col_desc + '<sub>' + ms
    # For when outputing non DJD entries
    if mode == 1: 
        output += ', Source: ' + df_row.Source
    output += ')</sub>'

    # Checking if there is other notes
    if not pd.isnull(df_row._7):
        output += '<br>**>>``Other notes``:** ``\"' + capfirst(df_row._7) + '\"``'
    st.markdown(output, unsafe_allow_html=True)


def format_markdown_orcid(orcid):
    return '<sup>[![](https://info.orcid.org/wp-content/uploads/2019/11/'\
        'orcid_16x16.png)](https://orcid.org/' + orcid + ')</sup>'


def overview(df):
    st.markdown(
        'Below are all color description entries found in the database. The heade'\
        'r or column name is clickable, and is useful to sort the database based '\
        'on the selected column, either in ascending or descending order.',
        unsafe_allow_html=True)
    
    new_columns = df.columns.values
    new_columns[2] = 'Number of fragments'
    df.columns = new_columns
    st.dataframe(df, hide_index=True)


def djdvolumes(df):
    query = st.text_input('Enter DJD volume', '')
    st.caption(
        'Type in the DJD volume of interest to show all entries with color desc'\
        'ription found in that publication. Multiple entries is supported and m'\
        'ust be written separated by commas, e.g., "12, 4". The keyword "NOT DJ'\
        'D" can also be used to retrieve colour descriptions found in other pub'\
        'lications.</sup>', unsafe_allow_html=True)
    hits = st.empty()
    txt = ''
    st.write('##')

    counter = 0
    valid_entry = True if len(query) > 0 else False

    if len(query) > 0:
        query = query.split(',')
        subhead = False if len(query) == 1 else True
        for q in query:
            # Checking negation
            if q.lower().strip().startswith('not'):
                if subhead:
                    st.subheader('Other publications (Non-DJD)')
                for row in df.itertuples():
                    if not row.Source.lower().startswith('djd'):
                        format_markdown(row, mode=1)
                        counter += 1
            # Checking if DJD volume
            elif q.strip().isdigit():
                if subhead:
                    st.subheader('DJD ' + str(q).strip())
                results = df.loc[
                    df['Source'].str.startswith('DJD ' + q.strip() + ':')]
                
                if len(results) > 0:
                    for row in results.itertuples():
                        format_markdown(row)
                else:
                    # Only show for multiple queries
                    if len(query) > 1:
                        st.markdown(':red[No entries found in DJD ' + \
                                    str(q).strip() + ']')
                counter += len(results)
            else:
                valid_entry = False

        if counter == 0 and valid_entry:
            txt = ':red[No entries found]'
        elif counter > 0:
            txt = ':blue[' + str(counter) + ' entries found]'
            if not valid_entry:
                txt += '<br>:red[One or more entered keywords are not supported.]'
        elif not valid_entry:
            txt = '<br>:red[One or more entered keywords are not supported.]'

    hits.markdown(txt, unsafe_allow_html=True)


def editor(df):
    query = st.text_input('Enter an editor\'s name', '')
    st.caption(
        'Type in the name of an editor to find entries made under the responsib'\
        'le editor. Note that despite a DJD volume having multiple editors, som'\
        'e color descriptions may have been recorded not under all editors of i'\
        'ts corresponding DJD volume.', unsafe_allow_html=True)
    hits = st.empty()
    st.write('##')

    counter = 0
    if len(query) > 0:
        # Remove no values entries first
        results = df.loc[df['Responsible editor'].notnull()]
        # Find the query in non-null elements, and sort based on DJD volume
        results = results[results['Responsible editor'].str.lower().str.contains(
            query.strip().lower())].sort_values('Source')
        
        vols = []
        djd = True
        for row in results.itertuples():
            mode = 0
            # Checking the publication and writing the publication subheader
            publ = 'Other publications (Non-DJD)' if 'DJD' not in row.Source \
                else row.Source.rsplit(':')[0]
            if 'Other' in publ:
                st.subheader(publ)
                mode = 1
            else:
                vol = publ.split(' ')[1]
                if vol not in vols:
                    vols.append(vol)
                    st.subheader(publ)
            
            format_markdown(row, mode=mode)

        counter += len(results)

    if len(query) == 0:
        txt = ''
    else:
        if counter == 0:
            txt = ':red[No entries found]'
        else:
            txt = ':blue[' + str(counter) + ' entries found]'
    hits.markdown(txt, unsafe_allow_html=True)


def search(df):
    query = str(st.text_input('Enter query', ''))
    st.caption(
        'Type in a keyword to find all entries that contains it in the color desc'\
        'ription.', unsafe_allow_html=True)
    hits = st.empty()
    st.write('##')

    counter = 0
    if len(query) > 0:
        highlighted = ':blue[***' + query + '***]'
        results = df[df['Color description'].str.contains(query, case=False)]
        results['Color description'] = results['Color description'].apply(
            lambda x: x.casefold().replace(query.casefold(), highlighted))
        
        for row in results.itertuples():
            format_markdown(row, mode=1)

        counter += len(results)
    
        if counter == 0:
            txt = ':red[No entries found]'
        else:
            txt = ':blue[' + str(counter) + ' entries found]'
    else:
        txt = ''
    hits.markdown(txt, unsafe_allow_html=True)


dbf = os.getcwd() + '/data/dsscolors-v2.xlsx'
df = pd.read_excel(dbf, dtype=str)


st.header('The Colors of the Dead Sea Scrolls Fragments')
authors = show_authors(['hildad', 'signemh'])
st.markdown('By ' + authors, unsafe_allow_html=True)
st.markdown('##')

st.markdown(
    'Color is often used as the physical description of Dead Sea scrolls and frag'\
    'ments. This is especially true throughout the volumes of the Discoveries in '\
    ' the Judaean Desert (DJD). In this database, we have listed color descriptio'\
    'ns of DSS fragments found in DJD and a few other publications. However, it i'\
    's important to note that these descriptions of color is a subjective and qua'\
    'litative way to describe color and it is far from being an objective and acc'\
    'urate description of surface color. ')
st.markdown(
    'To read all entries listed in this database, see the **Overview** tab. The t'\
    'ab **Filter DJD volumes** will allow you read database entries on specific D'\
    'JD volumes or those found in other publications. The tab **Filter editor** w'\
    'ill give all entries specifically entered by the entered responsible editor.'\
    ' Finally, the tab **Search** allows finding a specific keyword, e.g., "blue"'\
    ', in the Color description entries.'
)

tabs = st.tabs(['Overview', 'Filter DJD volumes', 'Filter editor', 'Search'])

tab_collector = tabs[0]
with tab_collector:
    st.write('##')
    overview(df)

tab_collector = tabs[1]
with tab_collector:
    st.write('##')
    djdvolumes(df)

tab_collector = tabs[2]
with tab_collector:
    st.write('##')
    editor(df)

tab_collector = tabs[3]
with tab_collector:
    st.write('##')
    search(df)
