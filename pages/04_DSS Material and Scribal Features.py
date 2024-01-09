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


def format_markdown_orcid(orcid):
    return '<sup>[![](https://info.orcid.org/wp-content/uploads/2019/11/'\
        'orcid_16x16.png)](https://orcid.org/' + orcid + ')</sup>'


def format_markdown_title(title):
    final_word = title.split(' ')[-1]
    if len(final_word) == 1:
        fmt = "<sup style='font-size:.8em;'>%s</sup>" %final_word
        return title[:-2] + fmt
    return title


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
        """SELECT * FROM dss_main main
        LEFT JOIN dss_site site ON main.site_id = site.site_id
        LEFT JOIN dss_writing_lang lang
            ON main.writinglang_id = lang.lang_id
        LEFT JOIN dss_writing_script writing
            ON main.writingscript_id = writing.script_id
        LEFT JOIN dss_writing_medium medium
            ON main.writingmedium_id = medium.material_id
        WHERE dss_id='%s'""" %dssid, conn)
    content = pd.read_sql_query(
        """SELECT * FROM dss_textualcontent content
        LEFT JOIN gr_composition composition
            ON content.composition_id = composition.composition_gid
        LEFT JOIN gr_canonical canon
            ON composition.canon_gid = canon.canon_gid
        WHERE dss_id='%s'""" %dssid, conn)
    scribal = pd.read_sql_query(
        """SELECT * FROM dss_scribal WHERE dss_id='%s'""" %dssid, conn)
    conn.commit()
    conn.close()

    empty = '```None```'
    dss = dss.fillna(empty)
    scribal = scribal.fillna(empty)
    category, text, textrange = empty, empty, empty
    spacephyl = '</br>'
    if len(content) > 0:
        content = content.fillna('```None```')
        category = content.canon_gname.iloc[0].title() if pd.isna(
            content.canon_gname2.iloc[0]) else content.canon_gname2.iloc[0].title()
        text = ', '.join([x for x in content.composition_gname])
        textrange = content.content_range.iloc[0] if len(content==1) else\
            '</br>'.join([x + ' ' + str(y) for x, y in zip(
            content.composition_gname, content.content_range)]).replace('None', '-')
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
        header = '<center><h2>%s - %s</h2></center>' %(
            dss.siglum.iloc[0], title)
        st.markdown(header, unsafe_allow_html=True)
        st.write('##')

        # Reference information
        main_header = '**Site </br>Reference </br>URL**'
        main_content = dss.site_name.iloc[0]
        if main_content.lower() == 'qumran':
            main_content += ', Cave ' + str(dss.cave_num.iloc[0])
        main_content += '</br>' + format_markdown_notimplemented() +\
            '</br>' + dss.leonlevy_url.iloc[0]
        colh1, colh2 = st.columns([0.7, 2], gap='small')
        colh1.markdown(main_header, unsafe_allow_html=True)
        colh2.markdown(main_content, unsafe_allow_html=True)

        # Textual information
        st.subheader(':page_with_curl: Textual information', anchor=None)
        text_header = '**Language </br>Script </br>Date**'
        text_content = dss.lang_name.iloc[0].title() + '</br>' +\
            dss.script_name.iloc[0].title() + '</br>' + dss.date_text.iloc[0]
        colt1, colt2 = st.columns([0.7, 2], gap='small')
        colt1.markdown(text_header, unsafe_allow_html=True)
        colt2.markdown(text_content, unsafe_allow_html=True)

        text_header = '**Category </br>Is phylactery?</br>Text </br>Range**'
        text_content = category + '</br>' + format_markdown_checkmark(
            dss.is_phylactery.iloc[0]) + '</br>' + text + '</br>' + textrange
        colt3, colt4 = st.columns([0.7, 2], gap='small')
        colt3.markdown(text_header, unsafe_allow_html=True)
        colt4.markdown(text_content, unsafe_allow_html=True)

        # Material information
        st.subheader(':scroll: Material information', anchor=None)
        mat_header = '**Material</br>Length <sub>(reconstructed)</sub></br>'\
            'Page height**'#'Margins</br></br></br></br></br>Page and column sizes**'
        mat_content = dss.material_name.iloc[0].title() + '</br>' + \
            str(dss.reconstr_len_text.iloc[0]) + '</br>' + \
            str(dss.page_height_cm.iloc[0])
        if empty not in str(dss.page_height_cm.iloc[0]):
            mat_content += ' cm'
        mat_content += '</br>'
        colm1, colm2= st.columns([.7, 2], gap='small')
        colm1.markdown(mat_header, unsafe_allow_html=True)
        colm2.markdown(mat_content, unsafe_allow_html=True)
        print(scribal)
        # Scribal features
        st.subheader(':black_nib: Scribal features', anchor=None)
        scrib_header = '**Dry lines? </br>Guide marks? </br>Margins'\
            '</br></br></br></br></br>Column sizes</br></br>Distance'\
            ' between lines</br>Letter height**'
        scrib_check = format_markdown_checkmark(scribal.has_drylines.iloc[0]) + \
            '</br>' + format_markdown_checkmark(scribal.has_guidemarks.iloc[0])
        margincol_hdr = '</br>*Top</br>Bottom</br>Left</br>Right</br>Between'\
            ' columns</br>Column width</br>Column height*</br>'
        margins = '</br></br>%s mm</br>%s mm</br>%s mm</br>%s mm</br>%s mm' %(
            scribal.margin_mm_top.iloc[0], scribal.margin_mm_bottom.iloc[0], 
            scribal.margin_mm_left.iloc[0], scribal.margin_mm_right.iloc[0],
            scribal.margin_betweencols.iloc[0])
        colsize = '</br>%s cm | %s letters</br>%s cm | %s lines' %(
            scribal.col_width_cm.iloc[0], scribal.col_width_letters.iloc[0], 
            scribal.col_height_cm.iloc[0], scribal.col_height_lines.iloc[0])
        lineslet = '%s mm' %scribal.distance_betweenlines_mm.iloc[0] + \
            '</br>%s mm' %scribal.letter_height_mm.iloc[0]
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
        """SELECT dss_id, siglum, title FROM dss_main""", conn)
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
        layout_single_manuscript(dss.dss_id[idx])
        


def overview(df):
    dfo = df.copy()
    dfo.replace(['0', ], '', inplace=True) # CONFIRM WITH MATTHEW

    # Configure grid options
    builder = GridOptionsBuilder.from_dataframe(dfo)
    builder.configure_pagination(
        enabled=True, paginationAutoPageSize=False, paginationPageSize=25)
    builder.configure_selection(selection_mode='single', use_checkbox=False)
    grid_options = builder.build()

    overview_table = AgGrid(
        dfo.fillna(''), gridOptions=grid_options, enable_enterprise_modules=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)



dbf = os.getcwd() + '/data/dssmaterialscribal.xlsx'
df = pd.read_excel(dbf, dtype=str, index_col=None)

st.header('[Test page] Dead Sea Scrolls Material and Scribal Features')

authors = show_authors(['matthewpm'], show_affil=False)
st.markdown('By ' + authors, unsafe_allow_html=True)
st.markdown('##')

st.markdown(':red[Intro text here, and some instructions. To mention sources mainly DJD and Tov]')
st.markdown('##')

tabs = st.tabs(['Overview', 'Filter single ms', 'Visualisation gallery'])

tab_overview = tabs[0]
with tab_overview:
    st.write('##')
    st.markdown(
        ':green[Implementation notes: \n Use aggrid table, with possibility '\
        'of aggrid sorting showing a dropdown of available entries]', 
        unsafe_allow_html=True)
    overview(df)

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