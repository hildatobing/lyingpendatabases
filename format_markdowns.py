import re
import streamlit as st


def __replaceNone(listoftuple, isdataframe=False):
    nlist_ = []
    if isdataframe:
        return listoftuple.fillna('```None```')
    else:
        for tuple_ in listoftuple:
            nlist_.append(
                tuple([x if x is not None else '```None```' for x in tuple_]))
        return nlist_


def __replaceEmpty(text):
    if len(text.strip()) == 0:
        text = '?'
    return text


def __qSuperscript(text, sigl=False):
    # Case for siglum text, e.g., 1Qx, not superscripted but concat with the
    # Qnumber. But if the Qnumber is, e.g., 1QH a, it is superscripted.
    if sigl:
        subs = text.split(' ')
        if len(subs) > 1:
            if subs[-1].islower():
                if subs[-2][-1].isnumeric():
                    subs[-1] = subs[-1]
                else:
                    subs[-1] = "<sup style='font-size:.7em;'>" + subs[-1] +\
                         "</sup>"
        text = ''.join(subs)
    else:
        subs = text.split(' ')
        for i, sub in enumerate(subs):
            if len(sub) < 2 and i > 0 and sub.islower():
                subs[i] = "<sup style='font-size:.7em;'>" + subs[i] + "</sup>"
        text = ' '.join(subs)
        text = text.replace(' <sup', '<sup')
    return text


def __addDotPAMNumber(pamnum):
    return '{:,}'.format(pamnum).replace(',', '.')


def general_justifypar(text, color='black'):
    return '<div style="text-align:justify;color:' + color + '">' + text +\
        '</div><br>'


def pam_getRangeOptions():
    bins = [x for x in range(40000, 44501, 500)]
    return [__addDotPAMNumber(x) + '–' + __addDotPAMNumber(y-1) for x, y in \
            zip(bins[:-1], bins[1:])] + ['Others']


def cat_tabPhotograph(res):
    '''
    Markdown formatting for Reed's catalog page.
    '''
    url = res[6]
    pamtext = '<a href="' + url + '">' + res[0] + '</a>' if url != '-' \
        else res[0]
    st.markdown('<b>' + pamtext + '</b><br>', unsafe_allow_html=True)
    
    sigla = res[1].split(',')
    titles = res[2].split(';')
    djdids = res[3].split(',') if res[3] is not None else '?'
    plates = res[4].split(',') if res[3] is not None else '?'
    fragments = res[5].split(';') if res[3] is not None else '?'
    caves = [int(x) for x in res[7].split(',')]
    sortnr = [float(x) for x in res[8].split(',')]

    zipped = zip(sigla, titles, djdids, plates, fragments, caves, sortnr)
    sortedres = sorted(zipped, key=lambda t: (t[-2], t[-1]), reverse=False)
    
    dsstext = '<pre>'
    for sig, title, djd, djdpl, djdfrg, cv, srt in sortedres:
        dsstitle = __qSuperscript(title)
        dsstext += '&emsp;' + __qSuperscript(sig, sigl=True) + '&ensp;' +\
            dsstitle
        dsstext += '&emsp;DJD ' + __replaceEmpty(djd) + '&ensp;'
        dsstext += 'pl. ' + __replaceEmpty(djdpl) + '&ensp;'
        if 'frg' in djdfrg:
            dsstext += djdfrg
        else:
            nfrg = len(djdfrg.strip().split(','))
            if nfrg > 1 or '–' in djdfrg: # Multiple fragments
                dsstext += 'frgs. ' + djdfrg
            else: # Zero fragment not printed at all
                if len(djdfrg) > 0: # Single fragment
                    dsstext += 'frg. ' + djdfrg
        dsstext += '<br>'

    dsstext += '</pre>'
    st.markdown(dsstext, unsafe_allow_html=True)


def cat_tabDocument(res, docpl):
    doctext = '<pre><b>' + __qSuperscript(res[1], sigl=True) +\
        ' ' + __qSuperscript(res[2], sigl=False) + '</b>'
    if docpl is not None:
        doctext += '</b><br>' + docpl[0] + ', pl. '
        for i, pl in enumerate(docpl[1].split(',')):
            plnr = pl.split('<')[0]
            url = re.search('<(.+?)>', pl).group(1)
            if i > 0:
                doctext += ', '
            if url == '-':
                doctext += plnr
            else:
                doctext += '<a href="' + url + '">' + plnr + '</a>'
    doctext += '</pre>'
    st.markdown(doctext, unsafe_allow_html=True)

    pamnrs = res[4].split(',')
    pamurls = res[5].split(',')
    djdids = res[6].split(',')
    djdpls = res[7].split(',')
    djdfrgs = res[8].split(';')
    pamtext = '<pre>'
    for pamnr, pamurl, djdid, djdpl, djdfrg in zip(
        pamnrs, pamurls, djdids, djdpls, djdfrgs):
        
        if len(pamurl) > 1:
            ahref = '<a href="' + pamurl + '">'
            pamtext += ahref + pamnr + '</a>'
        else:
            pamtext += pamnr

        pamtext += '&emsp;&emsp;DJD ' + __replaceEmpty(djdid)
        pamtext += '&emsp;pl. ' + __replaceEmpty(djdpl) + '&emsp;'
        if 'frg' in djdfrg:
            pamtext += djdfrg
        else:
            nfrg = len(djdfrg.strip().split(','))
            if nfrg > 1 or '–' in djdfrg: # Multiple fragments
                pamtext += 'frgs. ' + djdfrg
            else: # Zero fragment not printed at all
                if len(djdfrg) > 0: # Single fragment
                    pamtext += 'frg. ' + djdfrg
                
        pamtext += '<br>'
    pamtext += '</pre>'
    st.markdown(pamtext, unsafe_allow_html=True)


def cat_tabPhotograph_2(contentdf):
    '''
    Markdown formatting for Reed's catalog photo list option 2.
    '''
    contentdf = __replaceNone(contentdf, isdataframe=True)
    for res in contentdf.itertuples():
        label = res.siglum.replace(' ', '') + ' ' + res.title
        with st.expander(label):
            _, catData_2_ch1, _ = st.columns(
                [0.1, 1, 3], vertical_alignment='center')
            catData_2_ch1.caption(
                ':green-background[<b>PAM information</b>]', 
                unsafe_allow_html=True)
            _, catData_2_c11, catData_2_c12 = st.columns(
                [0.2, 1, 3], vertical_alignment='center')
            catData_2_c11.markdown(
                '<b>Position on plate</b><br><b>Label</b>', 
                unsafe_allow_html=True)
            catData_2_c12.markdown(
                '%s<br>%s' %(res.pam_position, res.pamlabel), 
                unsafe_allow_html=True)
            
            _, catData_2_ch2, _ = st.columns(
                [0.1, 1, 3], vertical_alignment='center')
            catData_2_ch2.caption(
                ':green-background[<b>DJD information</b>]', 
                unsafe_allow_html=True)
            _, catData_2_c21, catData_2_c22 = st.columns(
                [0.2, 1, 3], vertical_alignment='center')
            catData_2_c21.markdown(
                '<b>Volume</b><br><b>Plate</b><br><b>Column</b><br>'\
                '<b>Fragments</b><br><b>Notes on plate</b><br><b>Edi'\
                'tor\'s notes</b>', unsafe_allow_html=True)
            catData_2_c22.markdown(
                '%s<br>%s<br>%s<br>%s<br>%s<br>%s' %(
                res.djd_vol, res.djd_plate, res.djd_col, res.djd_frg, 
                res.pam_notesonplate, res.djd_ednotes), 
                unsafe_allow_html=True)
            
            _, catData_2_ch3, _ = st.columns(
                [0.1, 1, 3], vertical_alignment='center')
            catData_2_ch3.caption(
                ':green-background[<b>Additional remarks</b>]', unsafe_allow_html=True)
            _, catData_2_c3 = st.columns([0.2, 4], vertical_alignment='center')
            catData_2_c3.markdown(
                '%s' %res.remarks, unsafe_allow_html=True)
            
            # st.write(content)


def catData_tabContent_deleteEntry(entry):
    entry = __replaceNone(entry, isdataframe=True)
    pamlabel = entry.pam_labelonplate
    if entry.pam_flag_illegiblelabel == 1:
        pamlabel = 'Illegible label'
    elif entry.pam_flag_nolabel == 1:
        pamlabel = 'No label'
    
    _, catData_2_ch1, _ = st.columns([0.1, 1, 3], vertical_alignment='center')
    catData_2_ch1.caption(
        ':grey-background[<b>PAM information</b>]', unsafe_allow_html=True)
    _, catData_2_c11, catData_2_c12 = st.columns(
        [0.2, 1, 3], vertical_alignment='center')
    catData_2_c11.markdown(
        '<b>Position on plate</b><br><b>Notes on plate</b><br><b>Label</b>', 
        unsafe_allow_html=True)
    catData_2_c12.markdown(
        '%s<br>%s<br>%s' %(entry.pam_position, entry.pam_notesonplate, 
        pamlabel), unsafe_allow_html=True)
    
    _, catData_2_ch2, _ = st.columns([0.1, 1, 3], vertical_alignment='center')
    catData_2_ch2.caption(
        ':grey-background[<b>DJD information</b>]', unsafe_allow_html=True)
    _, catData_2_c21, catData_2_c22 = st.columns(
        [0.2, 1, 3], vertical_alignment='center')
    catData_2_c21.markdown(
        '<b>Volume</b><br><b>Plate</b><br><b>Column</b><br><b>Fragments</b>'\
        '<br><b>Editor\'s notes</b>', unsafe_allow_html=True)
    catData_2_c22.markdown(
        '%s<br>%s<br>%s<br>%s<br>%s' %(
        entry.djd_vol, entry.djd_plate, entry.djd_col, entry.djd_frg, 
        entry.djd_ednotes), 
        unsafe_allow_html=True)
    
    _, catData_2_ch3, _ = st.columns([0.1, 1, 3], vertical_alignment='center')
    catData_2_ch3.caption(
        ':grey-background[<b>Additional remarks</b>]', unsafe_allow_html=True)
    _, catData_2_c3 = st.columns([0.2, 4], vertical_alignment='center')
    catData_2_c3.markdown('%s' %entry.remarks, unsafe_allow_html=True)


def scribal_fmt_title(siglum, title):
    return '<center><h3>%s %s</h3></center><br>' %(
        __qSuperscript(siglum, sigl=True), __qSuperscript(title))


def scribal_fmt_subtitle(subtitle):
    return '<br><center><h4>' + subtitle + '</h4></center>'


def scribal_fmt_checkmark(entry):
    if entry == '```None```':
        return ':heavy_multiplication_x:'
    else:
        return ':heavy_check_mark:'
    

def scribal_twocolstext(text1, text2, colsize, captionsize=False):
    c1, c2 = st.columns(colsize)
    if captionsize:
        c1.caption(text1, unsafe_allow_html=True)
        c2.caption(general_justifypar(text2), unsafe_allow_html=True)
    else:
        c1.markdown(text1, unsafe_allow_html=True)
        c2.markdown(general_justifypar(text2), unsafe_allow_html=True)


def scribal_fmt_singlespace_row():
    st.markdown("""
        <style>
        [data-testid=stVerticalBlock] >
        div:last-of-type[data-testid=stVerticalBlockBorderWrapper] > 
        div:first-of-type > 
        div:first-of-type[data-testid=stVerticalBlock]{
            row-gap: 0rem;
        }
        </style>
        """,unsafe_allow_html=True)
    

def scribal_fmt_quote(entry):
    if entry == '```None```':
        return entry
    else:
        return '<em>"' + entry.strip() + '"</em>'
    

def scribal_get_twocols():
    return st.columns([0.6, 2], gap='small')


def scribal_writeout_col(col1, col2):
    c1, c2 = scribal_get_twocols()
    c1.markdown(col1, unsafe_allow_html=True)
    c2.markdown(col2, unsafe_allow_html=True)


def scribal_writeout_col_multirow(col1, col2, extra=None):
    if len(col2) == 1:
        scribal_writeout_col(col1, scribal_fmt_quote(col2.iloc[0]))
    else:
        none_countdown = len(col2)
        c1, c2 = scribal_get_twocols()
        c1.markdown(col1, unsafe_allow_html=True)
        content = ''
        for row, desc in zip(col2, extra):
            if row != '```None```':    
                if desc != '```None```':
                    content += ':blue-background[frg(s). %s: ]' %(desc)
                content += scribal_fmt_quote(row) + '<br>'
        if len(content) == 0:
            content = '```None```'
        c2.markdown(content, unsafe_allow_html=True)


def scribal_tabSingleManuscript(dss, content):
    empty = '```None```'
    dss = dss.fillna(empty)
    text, textrange = empty, empty
    if len(content) > 0:
        content = content.fillna('```None```')
        text = ', '.join([x for x in content.composition_gname])
        textrange = content.content_range.iloc[0] if len(content)==1 else\
            '<br>'.join([x + ' ' + str(y) for x, y in zip(
            content.composition_gname, content.content_range)])

    with st.container(border=True):
        scribal_fmt_singlespace_row()
        st.markdown(scribal_fmt_title(
            dss.siglum.iloc[0], dss.title.iloc[0]), unsafe_allow_html=True)

        # Referencing information: edition, url
        main_content = dss.site.iloc[0]
        if main_content.lower() == 'qumran':
            main_content += ', Cave ' + str(dss.cave.iloc[0])
        if dss.djdtitle.iloc[0] == empty:
            main_content += '<br>' + empty
        else:
            main_content += '<br>' + dss.djdtitle.iloc[0]\
                + ' ' + dss.djdvol.iloc[0]
            if dss.djdpp.iloc[0] != empty:
                main_content += ', pp. ' + dss.djdpp.iloc[0]
        main_content += '<br>' + dss.othered.iloc[0]
        scribal_writeout_col(
            '**Site <br>DJD edition <br>Other edition**', main_content)
        scribal_writeout_col('**Photo URL**', dss.url.iloc[0])

        # Textual information
        st.markdown(scribal_fmt_subtitle(
            '📃 Textual information'), unsafe_allow_html=True)
        text_header = '**Language <br>Script <br>Period <br>Editor dating**'
        text_content = dss.language.iloc[0].title() + '<br>' +\
            dss.script.iloc[0].title() + '<br>' + dss.period.iloc[0] + '<br>' +\
            dss.date.iloc[0]
        scribal_writeout_col(text_header, text_content)
        st.markdown('<br>', unsafe_allow_html=True)
        scribal_writeout_col('**Category <br>Text**', dss.cat.iloc[0] + '<br>' + text)
        scribal_writeout_col('**Range**', textrange)
        if dss.phylactery.iloc[0] != empty:
            scribal_writeout_col(
                '**Is Phylactery?**', 
                scribal_fmt_checkmark(dss.phylactery.iloc[0]))

        # Material information
        st.markdown(scribal_fmt_subtitle(
            '📜 Material and physical features'), unsafe_allow_html=True)
        mat_header = '**Material<br>Length <sub>(reconstructed)</sub><br>'\
            'Page height**'
        mat_content = dss.material.iloc[0].title() + '<br>' + \
            str(dss.reconstr_len.iloc[0]) + '<br>' + str(dss.pageh_cm.iloc[0])
        if empty not in str(dss.pageh_cm.iloc[0]):
            mat_content += ' cm'
        mat_content += '<br>'
        scribal_writeout_col(mat_header, mat_content)
        st.markdown('<br>', unsafe_allow_html=True)
        scribal_writeout_col_multirow('**Color**', dss.color, dss.frgs)
        scribal_writeout_col_multirow('**Ink**', dss.ink, dss.frgs)
        scribal_writeout_col_multirow('**Surface**', dss.surface, dss.frgs)
        scribal_writeout_col_multirow(
            '**Other description**', dss.otherdesc, dss.frgs)
        
        # Scribal features
        st.markdown(scribal_fmt_subtitle(
            '🖋️ Scribal features'), unsafe_allow_html=True)
        scrib_header = '**Dry lines? <br>Guide marks? <br>Margins'\
            '<br><br><br><br><br>Column sizes<br><br>Distance'\
            ' between lines<br>Letter height**'
        scrib_check = scribal_fmt_checkmark(dss.drylines.iloc[0]) + \
            '<br>' + scribal_fmt_checkmark(dss.guidemarks.iloc[0])
        margincol_hdr = '<br>*Top<br>Bottom<br>Left<br>Right<br>Between'\
            ' columns<br>Column width<br>Column height*<br>'
        margins = '<br><br>%s mm<br>%s mm<br>%s mm<br>%s mm<br>%s mm' %(
            dss.top_margin.iloc[0], dss.bottom_margin.iloc[0], 
            dss.left_margin.iloc[0], dss.right_margin.iloc[0],
            dss.between_cols.iloc[0])
        colsize = '<br>%s cm | %s letters<br>%s cm | %s lines' %(
            dss.colw_cm.iloc[0], dss.colw_letters.iloc[0], dss.colh_cm.iloc[0], 
            dss.colh_lines.iloc[0])
        lineslet = '%s mm' %dss.distance_betweenlines.iloc[0] + \
            '<br>%s mm' %dss.letterh_mm.iloc[0]
        cols1, cols2 = st.columns([0.7, 2])
        cols1.markdown(scrib_header, unsafe_allow_html=True)
        with cols2:
            cols21, cols22 = st.columns([0.8, 2], gap='medium')
            cols21.markdown(
                scrib_check + margincol_hdr + lineslet, unsafe_allow_html=True)
            cols22.markdown(margins + colsize, unsafe_allow_html=True)