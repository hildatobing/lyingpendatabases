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


def layout_single_manu(row):
    # Font definition
    st.markdown('''
        <style>
        .big-font {
            font-size:20px;
        }
        </style>
        ''', unsafe_allow_html=True)
    
    row = row.copy().fillna('```None```')
    title = format_markdown_title(row.Title)
    with st.container(border=True):
        header = '<center><h2>%s - %s</h2></center>' %(row.Siglum,title)
        # header += '(Siglum %s)</br></center>' %row.Siglum
        st.markdown(header, unsafe_allow_html=True)
        st.write('##')

        # Reference information
        main_header = '**Site </br>Reference </br>URL**'
        main_content = row.Site
        if not pd.isna(row.Cave):
            main_content += ', Cave ' + row.Cave
        main_content += '</br>' + row.Reference + '</br>' + row.Link
        colh1, colh2 = st.columns([0.7, 2], gap='small')
        colh1.markdown(main_header, unsafe_allow_html=True)
        colh2.markdown(main_content, unsafe_allow_html=True)

        # Textual information
        st.subheader(':page_with_curl: Textual information', anchor=None)
        text_header = '**Language </br>Script </br>Date**'
        text_content = row.Language + '</br>' + row.Script + '</br>' + row.Date
        colt1, colt2 = st.columns([0.7, 2], gap='small')
        colt1.markdown(text_header, unsafe_allow_html=True)
        colt2.markdown(text_content, unsafe_allow_html=True)

        text_header = '**Category </br>Text </br>Range**'
        text_content = row.Category + '</br>' + row.Text + '</br>' + row.Range
        colt3, colt4 = st.columns([0.7, 2], gap='small')
        colt3.markdown(text_header, unsafe_allow_html=True)
        colt4.markdown(text_content, unsafe_allow_html=True)

        # Material information
        st.subheader(':scroll: Material information', anchor=None)
        mat_header = '**Material</br>Length <sub>(reconstructed)</sub></br>'\
            'Page height**'#'Margins</br></br></br></br></br>Page and column sizes**'
        mat_content = '%s</br>%s</br>%s cm</br>' %(
            row.Material, row['Reconstructed Length'], row['Page Height'])
        colm1, colm2= st.columns([.7, 2], gap='small')
        colm1.markdown(mat_header, unsafe_allow_html=True)
        colm2.markdown(mat_content, unsafe_allow_html=True)            
        
        # Scribal features
        st.subheader(':black_nib: Scribal features', anchor=None)
        scrib_header = '**Dry lines? </br>Guide marks? </br>Margins'\
            '</br></br></br></br></br>Column sizes</br></br>Distance'\
            ' between lines</br>Letter height**'
        scrib_check = format_markdown_checkmark(row['Dry Lines?']) + '</br>' +\
            format_markdown_checkmark(row['Guide Marks?'])
        margincol_hdr = '</br>*Top</br>Bottom</br>Left</br>Right</br>Between'\
            ' columns</br>Column width</br>Column height*</br>'
        margins = '</br></br>%s mm</br>%s mm</br>%s mm</br>%s mm</br>%s mm' %(
            row['Top Margin'], row['Bottom Margin'], row['Left Margin'], 
            row['Right Margin'], row['Between Columns'])
        colsize = '</br>%s cm | %s letters</br>%s cm | %s lines' %(
            row['Column Width cm'], row['Column Width Letters'], 
            row['Column Height cm'], row['Column Height Lines'])
        lineslet = '%s mm' %row['Distance Between Lines'] + '</br>%s mm' \
            %row['Letter Height']
        cols1, cols2 = st.columns([0.8, 2])
        cols1.markdown(scrib_header, unsafe_allow_html=True)
        with cols2:
            cols21, cols22 = st.columns([1, 2], gap='medium')
            cols21.markdown(
                scrib_check + margincol_hdr + lineslet, unsafe_allow_html=True)
            cols22.markdown(margins + colsize, unsafe_allow_html=True)
    

def single_manuscript(df):
    dfs = df.copy()

    help = 'Type in a manuscript name and a list of available manuscripts '\
        'containing the entered text will show up.'
    placeholder = 'Select or type a manuscript name'
    df_options = '(' + df['Siglum'].astype(str) + ') ' + df['Title'].astype(str)
    selected = st.selectbox(
        ' ', df_options, index=None, help=help, placeholder=placeholder)
    st.write('##')

    # If a row is selected
    if selected is not None:
        idx = list(df_options).index(selected)
        row = df.iloc[idx, :]
        layout_single_manu(row)


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
authors = 'Matthew P. Monger ' + format_markdown_orcid('0009-0008-4412-3682')
st.markdown('By ' + authors, unsafe_allow_html=True)
st.markdown('##')

st.markdown(':red[Intro text here, and some instructions. To mention sources mainly DJD and Tov]')
st.markdown('##')

tabs = st.tabs(['Overview', '[Single ms placeholder]', 'Visualisation gallery'])

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
    single_manuscript(df)

tab_visualisation = tabs[2]
with tab_visualisation:
    st.write('##')

    # graph_textualcontent()
    conn = sql.connect('lyingpen.sqlite3')
    c = conn.cursor()
    c.execute("""SELECT siglum FROM dss_main""")
    st.write(len(c.fetchall())) # magic