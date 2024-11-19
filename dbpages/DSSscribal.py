from authorship import show_authors
from os import getcwd

import pandas as pd
import streamlit as st
import sqlite3 as sql

import db_selects as dbs
import format_markdowns as fmd
import format_tables as fmt


def single_manuscript():
    instr = 'To find a specific manuscript, first select the find site below, '\
        'then select or search for the specific manuscript. For example, to se'\
        'lect 1Q1, choose Qumran Cave 1 in the Find Site menu, then select 1Q1'\
        ' from the Manuscript menu.'
    st.caption(fmd.general_justifypar(
        instr, color='black'), unsafe_allow_html=True)
    
    scribal_tabSingleManu_c1, scribal_tabSingleManu_c2 = st.columns(
        [1, 1], gap='medium')
    st.markdown('</br></br>', unsafe_allow_html=True)
    scribal_tabSingleManu_cont = st.container()

    table_site = dbs.site_getfullnames()['sitefullname'].tolist()
    with scribal_tabSingleManu_c1:
        site_selected = st.selectbox(
            'Select find site', options=table_site, index=None)
        siteid = table_site.index(site_selected) + 1 \
            if site_selected is not None else -1
    dss = dbs.dss_getfullname_bysite(siteid=siteid)
    with scribal_tabSingleManu_c2:
        scrib_selectedmanu = st.selectbox(
            'Select manuscript', dss.fullname.astype(str), index=None)
        st.markdown('</br>', unsafe_allow_html=True)

    # If a manuscript is selected
    if scrib_selectedmanu is not None:
        with scribal_tabSingleManu_cont:
            dssid = dss.loc[dss['fullname'] == \
                            scrib_selectedmanu, 'dss_id'].iloc[0]
            dss, content = dbs.scribal_getmanuscript_byid(dssid)
            if len(dss) > 0:
                fmd.scribal_tabSingleManuscript(dss, content)
            else:
                st.error(
                    'No data is currently available for **' + 
                    scrib_selectedmanu + '**')


def compare_features():
    st.caption(fmd.general_justifypar(
        'To generate a list of manuscripts and features, first select one or m'\
        'ore categories of manuscripts from the menu (you can also specify whi'\
        'ch texts you want to view), then select the features you want to incl'\
        'ude in the table from the menu that appears. You can enter full-scree'\
        'n mode and download the generated table by holding the cursor over th'\
        'e table.'), unsafe_allow_html=True)
    datafilter_container = st.container(border=True)
    feature_container = st.container(border=True)
    table_container = st.container()

    if 'scribal_tabCompare_columns' not in st.session_state:
        st.session_state['scribal_tabCompare_columns'] = ['Siglum', 'Title']

    cats = dbs.canon_getall_name2()[:4]
    with datafilter_container:
        scribal_tabCompare_c1, scribal_tabCompare_c2 = st.columns(
            [1, 1], gap='medium')
        with scribal_tabCompare_c1:
            selected_cats = st.multiselect(
                'Select category(s)', options=cats['canon_gname2'])
        gids = cats[cats.canon_gname2.isin(selected_cats)].canon_gid.values
        
        texts = dbs.texts_getall_bycanonids(gids)
        with scribal_tabCompare_c2:
            selected_texts = st.multiselect(
                'Select text(s)', options=texts['composition_gname'])
        tids = texts[texts['composition_gname'].isin(
            selected_texts)].composition_gid.values
    
    # If text is selected, get all documents within text/composition, otherwise
    # get all within the category level
    if selected_cats or selected_texts:
        preselected = dbs.scribal_getdocs_bytexts(tids) if selected_texts else\
            dbs.scribal_getdocs_bycats(gids)
        dss_tocompare = fmt.scribal_comparefeatures(preselected)
        
        with feature_container:
            # limits = 5 if selected_texts else 4
            if selected_texts:
                st.session_state.scribal_tabCompare_columns = [
                    'Siglum', 'Title', 'Category', 'Text'] + st.multiselect(
                    'Select features to compare', dss_tocompare.columns[5:-2])
            else:
                st.session_state.scribal_tabCompare_columns = [
                    'Siglum', 'Title', 'Category'] + st.multiselect(
                    'Select features to compare', dss_tocompare.columns[4:-2])
        selecteddata = dss_tocompare[
            st.session_state.scribal_tabCompare_columns]

        if 'Is phylactery?' in st.session_state.scribal_tabCompare_columns:
            with feature_container:
                phyl = st.radio(
                    'Filter by phylactery',
                    ['Show all', 'Only phylactery', 'Remove phylactery'])
                if phyl == 'Show all':
                    selecteddata = selecteddata.copy()
                elif phyl == 'Only phylactery':
                    selecteddata = selecteddata[
                        selecteddata['Is phylactery?'] == True]
                elif phyl == 'Remove phylactery':
                    selecteddata = selecteddata[
                        selecteddata['Is phylactery?'] == False]
        if 'Period' in st.session_state.scribal_tabCompare_columns:
            with feature_container:
                periodopts = dbs.period_getall()
                periodopts_wnum = periodopts['dssperiod_order'].astype(str) +\
                    '. ' + periodopts['dssperiod_name']
                selectedperiod = st.multiselect(
                    'Filter by period', options=periodopts_wnum, 
                    default=periodopts_wnum.iloc[0:])
                selecteddata = selecteddata[pd.isna(selecteddata.Period) |
                    selecteddata.Period.isin(selectedperiod)]
    
        with table_container:
            st.markdown('<br><h3>Result</h3>', unsafe_allow_html=True)
            if len(selecteddata) == 0:
                st.warning('No entries found.')
            else:
                st.dataframe(
                    selecteddata, use_container_width=True,
                    height=(len(selecteddata)+1)*35+3)


def glossary():
    with st.expander('Glossary'):
        d1, d2 = st.columns([3.5, 1], gap='medium')
        d1.caption(fmd.general_justifypar(
            'The following glossary describes the terms used throughout the da'\
            'tabase. It can also be downloaded as a PDF.'),
            unsafe_allow_html=True)
        with open(getcwd() + '/assets/texts/scribal_glossary.pdf', 'rb') as f:
            PDFbyte = f.read()
        d2.download_button(
            label="Download", data=PDFbyte, file_name="glossary.pdf",
            mime='application/octet-stream')
        
        colsize = [1, 4.8]
        fmd.scribal_twocolstext(
            '**Site**', 'Currently, the database contains many, but not all, o'\
            'f the find sites in the Judean Desert.', colsize)
        fmd.scribal_twocolstext(
            '**DJD Edition**', 'References to the volume and pages of the publ'\
            'ication in DJD.', colsize)
        fmd.scribal_twocolstext(
            '**Other Edition**', 'References to primary publications outside o'\
            'f DJD or other sources used for data collection. Note that this i'\
            's not an exhaustive list, but sources consulted for this database'\
            '.', colsize)
        fmd.scribal_twocolstext(
            '**Photo URL**', 'Links to the Leon Levy Dead Sea Scrolls Digital '\
            'Library pages that correspond to each manuscript.', colsize)
        fmd.scribal_twocolstext(
            '**Language**', 'The primary language of the manuscript.', colsize)
        fmd.scribal_twocolstext(
            '**Script**', 'The primary script of the manuscript, the options a'\
            're Paleo-Hebrew, Square Script, Cryptic, Greek, and Arabic.', 
            colsize)
        fmd.scribal_twocolstext(
            '**Period**', 'The dating of the manuscript is structured accordin'\
            'g to periods: <br><b>Early Hellenistic</b>: Signifies the period '\
            'prior to the Hasmonean period, i.e. before c. 175 BCE. Previously'\
            ' called archaic.<br><b>Hellenistic-Roman</b>: Signifies manuscrip'\
            'ts that are not paleographically dated but fit within the broader'\
            ' period represented by the other manuscripts. Thus, sometime betw'\
            'een 200 BCE and 100 CE. This is a catch-all for undated manuscrip'\
            'ts.<br><b>Transitional</b>: Signifies a date between the Hasmonea'\
            'n and Herodian periods, often given by editors who see features o'\
            'f both periods. Ca. 30 BCE – 30 CE, but sometimes somewhat more b'\
            'roadly defined.<br><b>Hasmonean</b>: 175 – 30 BCE<br><b>Herodian'\
            '</b>: 30 BCE – 70 CE<br><b>Roman</b>: 70 CE and later', colsize)
        fmd.scribal_twocolstext(
            '**Editor Dating**', 'The specific dating of the manuscript accord'\
            'ing to the editor of the manuscript.', colsize)
        fmd.scribal_twocolstext(
            '**Category**', '<b>Hebrew Bible</b>: Includes the books found in '\
            'the traditional Hebrew canon.<br><b>Apocrypha</b>: Texts found am'\
            'ong the Apocryphal or Deuterocanonical books included in some Chr'\
            'istian traditions. The only texts included here are Tobit, Sirach'\
            ' (Ben Sira), and the Epistle of Jeremiah.<br><b>Pseudepigrapha</b'\
            '>: Includes ancient texts found outside the Hebrew canon that are'\
            ' known from Antiquity, but not included in the traditional Apocry'\
            'pha. These include Jubilees, 1 Enoch, and The Testaments of the 1'\
            '2 Patriarchs.<br><b>Qumran</b>: Includes texts known from Qumran.'\
            ' For now, this is limited to the most well-known and widely attes'\
            'ted texts: Community Rule, Hodayot, War Scroll, Temple Scroll, Da'\
            'mascus Document, Song of the Sabbath Sacrifice, and Reworked Pent'\
            'ateuch.<br><b>Uncategorized</b>: All other manuscripts are placed'\
            ' here by default, but other categories will be developed with tim'\
            'e, and some manuscripts can be moved to other categories as neede'\
            'd.', colsize)
        fmd.scribal_twocolstext(
            '**Text**', 'The name of the text(s) which can be identified in th'\
            'e manuscript.', colsize)
        fmd.scribal_twocolstext(
            '**Range**', 'The specific portions of the text that are found in '\
            'the manuscript.', colsize)
        fmd.scribal_twocolstext(
            '**Material**', 'The physical material the manuscript is made of. '\
            'These are very generally described: Papyrus and Skin are the two '\
            'main categories.', colsize)
        fmd.scribal_twocolstext(
            '**Length (reconstructed)**','The length of the scroll as measured'\
            ' (in very few cases) or reconstructed by the editors. Note that t'\
            'he vast majority of scrolls have not been reconstructed.', colsize)
        fmd.scribal_twocolstext(
            '**Page Height**', 'The total height of the page which is usually '\
            'highly reconstructed.', colsize)
        fmd.scribal_twocolstext(
            '**Color**', 'Descriptions of the color of the manuscript or certa'\
            'in fragments as found in DJD.', colsize)
        fmd.scribal_twocolstext(
            '**Ink**', 'Descriptions of the ink as found in DJD.', colsize)
        fmd.scribal_twocolstext(
            '**Surface**', 'Descriptions of the surface of the manuscript or f'\
            'ragments as found in DJD.', colsize)
        fmd.scribal_twocolstext(
            '**Other Descriptions**', 'Other descriptions of other physical fe'\
            'atures of the manuscripts are found in DJD.', colsize)
        fmd.scribal_twocolstext(
            '**Dry Lines**', 'Notes the presence of ruling with dry lines (tho'\
            'ugh a few cases are, in fact, wet lines with ink), indicating the'\
            ' topline of each line of writing.', colsize)
        fmd.scribal_twocolstext(
            '**Guide Marks**', 'Notes the presence of guide marks in the margi'\
            'ns used to indicate the writing block. These may have different f'\
            'orms and consistency.', colsize)
        fmd.scribal_twocolstext(
            '**Margins**', 'Measurements for extant margins including top marg'\
            'ins, bottom margins, right margins, left margins and intercolumna'\
            'r margins.', colsize)
        fmd.scribal_twocolstext(
            '**Column Size**', '<b>Column width</b> is given in both cm and le'\
            'tter spaces. The measurements are on the expected column size wit'\
            'h the published data from parenthesis. The value is sometimes an '\
            'average of the extant data and sometimes the result of choosing a'\
            ' representative column and then finding the average. Thus, the nu'\
            'mbers are a guideline.<br><b>Column Height</b> is given in both c'\
            'm and number of lines.', colsize)
        fmd.scribal_twocolstext(
            '**Distance Between Lines**', 'The measurement is an average or no'\
            'rmal value of the distance between successive toplines.', colsize)
        fmd.scribal_twocolstext(
            '**Letter Height**', 'The baseline measurement of letter sizes ref'\
            'lects standard letter sizes of letters that do not extend above o'\
            'r below the normal writing space.', colsize)


def credits():
    with st.expander('Credits'):
        m1, m2 = st.columns([2.5, 1], gap='medium', vertical_alignment='center')
        m1.caption(fmd.general_justifypar(
            'The data presented here was originally collected by Matthew P. Mo'\
            'nger (MF, Oslo) as a private resource for studying and comparing '\
            'different features of the scrolls. The majority of the measuremen'\
            'ts and data were pulled from DJD and Scribal Practices over sever'\
            'al years. Matthew is a part of MF Lab for Manuscript Studies and '\
            'Digital Research (MF L-MaSDR).'), unsafe_allow_html=True)
        m2.image('assets/logo-mf-lmasdr.png')
        h1, h2 = st.columns([3.4, 1], gap='medium')
        h1.caption(fmd.general_justifypar(
            'Hilda Deborah (NTNU, Gjøvik, Norway) designed the database and co'\
            'ntributed to data collation and entry. She is also responsible fo'\
            'r both backend and frontend developments. Hilda is a member of Co'\
            'lourlab at NTNU.'), unsafe_allow_html=True)
        h2.image('assets/logo-ntnu-colourlab.jpg')
        st.caption(fmd.general_justifypar(
            'Signe M. Hægeland collected the color, ink, and surface descripti'\
            'ons from DJD.'), unsafe_allow_html=True)
        st.caption(fmd.general_justifypar(
            'All data has been entered manually and is taken from published so'\
            'urces, so errors or inconsistencies may be due to the sources or '\
            'human error.', color='green'), unsafe_allow_html=True)

st.header('Dead Sea Scrolls Physical and Scribal Features')
authors = show_authors(['matthewpm','hildad'], show_affil=False)
st.markdown(
    'By ' + authors + '</br>:blue[ver. 2024-beta1]', unsafe_allow_html=True)
st.write('##')

st.markdown(fmd.general_justifypar(
    'The Dead Sea Scrolls Physical and Scribal Features Database provides acce'\
    'ss to a structured dataset containing information about the Dead Sea Scro'\
    'lls. The data includes publication information, textual information, mate'\
    'rial and physical features, and scribal features of the manuscripts. All '\
    'information in the current iteration of this database is gleaned from pub'\
    'lished editions, mainly found in the <i>Discoveries in the Judaean Desert'\
    '</i> series (Oxford, Clarendon Press, 1955–2010), supplemented by other p'\
    'ublished editions as well as Emanuel Tov’s <i>Scribal Practices and Appro'\
    'aches Reflected in the Texts Found in the Judean Desert</i> (Brill, 2004).'
    ), unsafe_allow_html=True)
st.markdown(fmd.general_justifypar(
    '<b>Note:</b> The database is currently in a beta-testing phase, updates t'\
    'o the design and contents may change without notice. Any corrections or c'\
    'omments can be sent to <b>DSS (at) mf.no</b>.'), unsafe_allow_html=True)
st.markdown(fmd.general_justifypar(
    'In addition to the wiki page (<i>Browse document</i>) for each manuscript'\
    ', there is a <i>Compare features</i> tab that generates lists of manuscri'\
    'pts based on the features you specify.'), unsafe_allow_html=True)

credits()
glossary()
st.markdown('##')

tabs = st.tabs(['Browse document', 'Compare features'])

tab_details = tabs[0]
with tab_details:
    single_manuscript()

tab_comparefeat = tabs[1]
with tab_comparefeat:
    compare_features()