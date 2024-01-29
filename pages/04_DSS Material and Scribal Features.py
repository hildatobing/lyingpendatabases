from authorship import show_authors
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder

import os
import pandas as pd
import streamlit as st
import sqlite3 as sql

st.set_page_config(
    page_title="DSS Material and Scribal Features",
    page_icon='assets/Icon.png'
)


def remove_row_gap():
    st.markdown("""
        <style>
        [data-testid=stVerticalBlock] >
        div:last-of-type[data-testid=stVerticalBlockBorderWrapper] > 
        div:first-of-type > 
        div:first-of-type[data-testid=stVerticalBlock]{
            gap: 0rem;
        }
        </style>
        """,unsafe_allow_html=True)
    

def format_markdown_orcid(orcid):
    return '<sup>[![](https://info.orcid.org/wp-content/uploads/2019/11/'\
        'orcid_16x16.png)](https://orcid.org/' + orcid + ')</sup>'


def format_markdown_title(title):
    fmt_title = ''
    for word in title.split(' '):
        if len(word) == 1:
            if word.isalpha():
                word = "<sup style='font-size:.8em;'>%s</sup>" %word
        else:
            word = ' ' + word
        fmt_title += word
    return fmt_title + '</br>  </br>'


def format_markdown_checkmark(entry):
    if entry == '```None```':
        return ':heavy_multiplication_x:'
    else:
        return ':heavy_check_mark:'
    

def format_markdown_notimplemented():
    return '```Not yet implemented```'
    

def layout_single_manuscript(dssid):
    # Establish connection and query all information
    conn = sql.connect('lyingpen.sqlite3')
    dss = pd.read_sql_query(
        """SELECT * FROM dss_v_materialscribal WHERE dssid='%s'""" %dssid, conn)
    content = pd.read_sql_query(
        """SELECT * FROM dss_textualcontent content
        LEFT JOIN gr_composition composition
            ON content.composition_id = composition.composition_gid
        LEFT JOIN gr_canonical canon
            ON composition.canon_gid = canon.canon_gid
        WHERE dss_id='%s'""" %dssid, conn)
    conn.commit()
    conn.close()

    empty = '```None```'
    dss = dss.fillna(empty)
    category, text, textrange = empty, empty, empty
    spacephyl = '</br>'
    if len(content) > 0:
        content = content.fillna('```None```')
        category = content.canon_gname2.iloc[0].title()
        text = ', '.join([x for x in content.composition_gname])
        textrange = content.content_range.iloc[0] if len(content)==1 else\
            '</br>'.join([x + ' ' + str(y) for x, y in zip(
            content.composition_gname, content.content_range)])#.replace('None', '-')
        spacephyl = ''.join(['</br>']*len(content))
    
    # Font definition
    st.markdown('''
        <style>
        .big-font {
            font-size:20px;
        }
        </style>
        ''', unsafe_allow_html=True)
    
    title = format_markdown_title(dss.title.iloc[0])
    with st.container(border=True):
        remove_row_gap()

        header = '<center><h2>%s - %s</h2></center>' %(dss.siglum.iloc[0], title)
        st.markdown(header, unsafe_allow_html=True)

        # Reference information
        main_content = dss.site.iloc[0]
        if main_content.lower() == 'qumran':
            main_content += ', Cave ' + str(dss.cave.iloc[0])
        if dss.djdtitle.iloc[0] == empty:
            main_content += '</br>' + empty
        else:
            main_content += '</br>' + dss.djdtitle.iloc[0] + ' ' + dss.djdvol.iloc[0]
            if dss.djdpp.iloc[0] != empty:
                main_content += ', pp. ' + dss.djdpp.iloc[0]

        colh1, colh2 = st.columns([0.7, 2], gap='small')
        colh1.markdown('**Site </br>Reference**', unsafe_allow_html=True)
        colh2.markdown(main_content, unsafe_allow_html=True)

        colh3, colh4 = st.columns([0.7, 2], gap='small')
        colh3.markdown('**URL**', unsafe_allow_html=True)
        colh4.markdown(dss.leonlevy_url.iloc[0], unsafe_allow_html=True)

        # Textual information
        st.write('##')
        st.write('##')
        st.subheader(':page_with_curl: Textual information', anchor=None)
        st.write('##')
        text_header = '**Language </br>Script </br>Date**'
        text_content = dss.language.iloc[0].title() + '</br>' +\
            dss.script.iloc[0].title() + '</br>' + dss.date.iloc[0]
        colt1, colt2 = st.columns([0.7, 2], gap='small')
        colt1.markdown(text_header, unsafe_allow_html=True)
        colt2.markdown(text_content, unsafe_allow_html=True)
        st.write('##')
        
        colt3, colt4 = st.columns([0.7, 2], gap='small')
        colt3.markdown('**Category </br>Text**', unsafe_allow_html=True)
        colt4.markdown(category + '</br>' + text, unsafe_allow_html=True)

        colt5, colt6 = st.columns([0.7, 2], gap='small')
        colt5.markdown('**Range**', unsafe_allow_html=True)
        colt6.markdown(textrange, unsafe_allow_html=True)

        if dss.phylactery.iloc[0] != empty:
            colt7, colt8 = st.columns([0.7, 2], gap='small')
            colt7.markdown('**Is Phylactery?**', unsafe_allow_html=True)
            colt8.markdown(format_markdown_checkmark(
                dss.phylactery.iloc[0]), unsafe_allow_html=True)

        # Material information
        st.write('##')
        st.write('##')
        st.subheader(':scroll: Material information', anchor=None)
        st.write('##')
        mat_header = '**Material</br>Length <sub>(reconstructed)</sub></br>'\
            'Page height**'#'Margins</br></br></br></br></br>Page and column sizes**'
        mat_content = dss.material.iloc[0].title() + '</br>' + \
            str(dss.reconstr_len.iloc[0]) + '</br>' + str(dss.pageh_cm.iloc[0])
        if empty not in str(dss.pageh_cm.iloc[0]):
            mat_content += ' cm'
        mat_content += '</br>'
        colm1, colm2= st.columns([.7, 2], gap='small')
        colm1.markdown(mat_header, unsafe_allow_html=True)
        colm2.markdown(mat_content, unsafe_allow_html=True)
        
        # Scribal features
        st.write('##')
        st.write('##')
        st.subheader(':black_nib: Scribal features', anchor=None)
        st.write('##')
        scrib_header = '**Dry lines? </br>Guide marks? </br>Margins'\
            '</br></br></br></br></br>Column sizes</br></br>Distance'\
            ' between lines</br>Letter height**'
        scrib_check = format_markdown_checkmark(dss.drylines.iloc[0]) + \
            '</br>' + format_markdown_checkmark(dss.guidemarks.iloc[0])
        margincol_hdr = '</br>*Top</br>Bottom</br>Left</br>Right</br>Between'\
            ' columns</br>Column width</br>Column height*</br>'
        margins = '</br></br>%s mm</br>%s mm</br>%s mm</br>%s mm</br>%s mm' %(
            dss.top_margin.iloc[0], dss.bottom_margin.iloc[0], 
            dss.left_margin.iloc[0], dss.right_margin.iloc[0],
            dss.between_cols.iloc[0])
        colsize = '</br>%s cm | %s letters</br>%s cm | %s lines' %(
            dss.colw_cm.iloc[0], dss.colw_letters.iloc[0], dss.colh_cm.iloc[0], 
            dss.colh_lines.iloc[0])
        lineslet = '%s mm' %dss.distance_betweenlines.iloc[0] + \
            '</br>%s mm' %dss.letterh_mm.iloc[0]
        cols1, cols2 = st.columns([0.8, 2])
        cols1.markdown(scrib_header, unsafe_allow_html=True)
        with cols2:
            cols21, cols22 = st.columns([1, 2], gap='medium')
            cols21.markdown(
                scrib_check + margincol_hdr + lineslet, unsafe_allow_html=True)
            cols22.markdown(margins + colsize, unsafe_allow_html=True)
    

def single_manuscript():

    # Establish connection and read for dropdown option
    conn = sql.connect('lyingpen.sqlite3')
    dss = pd.read_sql_query(
        """SELECT dssid, siglum, title FROM dss_v_materialscribal""", conn)
    conn.commit()
    conn.close()

    help = 'Type in a manuscript name and a list of available manuscripts '\
        'containing the entered text will show up.'
    placeholder = 'Select or type a manuscript name'
    dss_options = dss.siglum.astype(str) + ' - ' + dss.title.astype(str)
    selected = st.selectbox(
        ' ', dss_options, index=None, help=help, placeholder=placeholder)
    st.write('##')

    # If a row is selected
    if selected is not None:
        idx = list(dss_options).index(selected)
        layout_single_manuscript(dss.dssid[idx])
        

def overview():
    # Establish connection and query all information
    conn = sql.connect('lyingpen.sqlite3')
    matscrib = pd.read_sql_query("""SELECT * FROM dss_v_materialscribal""", conn)
    content = pd.read_sql_query("""SELECT * FROM dss_v_contentcat""", conn)
    conn.commit()
    conn.close()

    # Aggregating content dataframe, because a single fragment can contain texts
    # from different books
    content['textcontent'] = content.iloc[:, 2:].apply(
        lambda x: ' - '.join(x.dropna().astype(str)), axis=1)
    content = content.fillna('').groupby(['dssid','category'])['textcontent'].apply(
        ' | '.join).reset_index()
    
    # Merge to a complete table
    dss = pd.merge(content, matscrib, on='dssid')

    # Formatting
    dss[['material', 'script', 'language']] = dss[[
        'material', 'script', 'language']].astype(str).apply(lambda x: x.str.title())
    dss.loc[dss['phylactery'] == 1, 'phylactery'] = 'Yes'
    dss.loc[dss['guidemarks'] == 1, 'guidemarks'] = 'Yes'
    dss.loc[dss['guidemarks'] == 0, 'guidemarks'] = ''
    dss.loc[dss['drylines'] == 1, 'drylines'] = 'Yes'
    dss.loc[dss['drylines'] == 0, 'drylines'] = ''
    ov_table = dss[['siglum', 'title', 'site', 'cave', 'category', 'textcontent', 
                    'phylactery', 'material', 'script', 'language', 'date', 
                    'reconstr_len', 'leonlevy_url', 'top_margin', 'bottom_margin', 
                    'right_margin', 'left_margin', 'between_cols', 'pageh_cm', 
                    'colw_cm', 'colw_letters', 'colh_cm', 'colh_lines', 'drylines', 
                    'distance_betweenlines', 'guidemarks', 'letterh_mm']].copy()
    ov_table.rename(columns={
        'textcontent': 'textual content', 'leonlevy_url': 'link', 
        'reconstr_len': 'reconstructed length', 'phylactery': 'is phylactery?',
        'top_margin': 'top margin (mm)', 'bottom_margin': 'bottom margin (mm)', 
        'right_margin': 'right margin (mm)', 'left_margin': 'left margin (mm)', 
        'between_cols': 'margin between cols (mm)', 'pageh_cm': 'page height (cm)', 
        'colw_cm': 'Column width (cm)', 'colw_letters': 'Column width (letters)', 
        'colh_cm': 'Column height (cm)', 'colh_lines': 'Column height (lines)', 
        'letterh_mm': 'letter height (mm)', 'drylines': 'has drylines?',
        'distance_betweenlines':'Distance between lines', 
        'guidemarks': 'has guidemarks?'}, inplace=True)
    ov_table.columns = map(str.capitalize, ov_table.columns)

    # Configure grid options
    builder = GridOptionsBuilder.from_dataframe(ov_table)
    builder.configure_columns('Textual content', wrapText=True, autoHeight=True)
    builder.configure_pagination(
        enabled=True, paginationAutoPageSize=False, paginationPageSize=25)
    builder.configure_selection(selection_mode='single', use_checkbox=False)
    grid_options = builder.build()

    overview_table = AgGrid(
        ov_table.fillna(''), gridOptions=grid_options, enable_enterprise_modules=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)




st.header('Dead Sea Scrolls Material and Scribal Features')

authors = show_authors(['matthewpm'], show_affil=False)
st.markdown('By ' + authors, unsafe_allow_html=True)
st.markdown('##')

# st.markdown(':red[Intro text here, and some instructions. To mention sources mainly DJD and Tov]')
st.markdown(':warning: :red[Page is under construction]')
st.markdown('##')

tabs = st.tabs(['Overview', 'Filter single ms', 'Visualisation gallery'])

tab_overview = tabs[0]
with tab_overview:
    st.write('##')
    # st.markdown(
    #     ':green[Implementation notes: \n Use aggrid table, with possibility '\
    #     'of aggrid sorting showing a dropdown of available entries]', 
    #     unsafe_allow_html=True)
    st.markdown(
        'The table below shows Dead Sea scrolls and materials containing material '\
        'and scribal information. This means that the list of scrolls and fragment'\
        's itself are not complete. The table allows you to sort entries based on '\
        'a chosen column, as well as advanced filter the entries. These advanced o'\
        'ptions will show up upon hovering a column header.'
    )
    overview()

tab_details = tabs[1]
with tab_details:
    st.write('##')
    single_manuscript()

tab_visualisation = tabs[2]
with tab_visualisation:
    st.write('##')

    # graph_textualcontent()

    # Connection testing
    conn = sql.connect('lyingpen.sqlite3')
    c = conn.cursor()
    c.execute("""SELECT siglum FROM dss_main""")
    st.write(len(c.fetchall()))