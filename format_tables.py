import pandas as pd


def scribal_comparefeatures(dss):
    # Capitalizing first letter
    dss[['material', 'script', 'language']] = dss[[
        'material', 'script', 'language']].astype(str).apply(
        lambda x: x.str.title())
    
    # Boolean to True/False
    dss['phylactery'] = dss[
        'phylactery'].apply(lambda x: True if x == 1 else False)
    dss['guidemarks'] = dss[
        'guidemarks'].apply(lambda x: True if x == 1 else False)
    dss['drylines'] = dss['drylines'].apply(lambda x: True if x == 1 else False)
    
    # Subsetting the table
    # Note: Numbered period is taken here to enable correct sorting.
    comptable = dss[[
        'dssid', 'siglum', 'title', 'cat', 'text', 'findsite', 'material',
        'script', 'language', 'period_wnum', 'date', 'reconstr_len',
        'phylactery', 'top_margin', 'bottom_margin', 'right_margin',
        'left_margin', 'between_cols', 'pageh_cm', 'colw_cm', 'colw_letters',
        'colh_cm', 'colh_lines', 'distance_betweenlines', 'letterh_mm',
        'drylines', 'guidemarks', 'siteid', 'sortingnr']].copy()
    
    comptable.rename(columns={
        'cat': 'Category', 'findsite': 'Find site', 'date': 'Editor dating',
        'reconstr_len': 'reconstructed length', 'phylactery': 'is phylactery?',
        'top_margin': 'top margin (mm)', 'bottom_margin': 'bottom margin (mm)', 
        'right_margin': 'right margin (mm)', 'left_margin': 'left margin (mm)', 
        'between_cols': 'margin between cols (mm)', 'period_wnum': 'period',
        'pageh_cm': 'page height (cm)', 'colw_cm': 'Column width (cm)', 
        'colw_letters': 'Column width (letters)', 
        'colh_cm': 'Column height (cm)', 'colh_lines': 'Column height (lines)', 
        'letterh_mm': 'letter height (mm)', 'drylines': 'has drylines?',
        'distance_betweenlines':'Distance between lines', 
        'guidemarks': 'has guidemarks?'}, inplace=True)
    comptable.columns = map(str.capitalize, comptable.columns)
    comptable.index = pd.RangeIndex(start=1, stop=len(comptable.index)+1)
    
    return comptable


# def get_alldata():
#     # Establish connection and query all information
#     conn = sql.connect('lyingpen.sqlite3')
#     matscrib = pd.read_sql_query("""SELECT * FROM dss_v_physicalscribal""", conn)
#     content = pd.read_sql_query("""SELECT * FROM dss_textualcontent""", conn)
#     conn.commit()
#     conn.close()

#     # Aggregating content dataframe, because a single fragment can contain texts
#     # from different books
#     content['textcontent'] = content.iloc[:, 2:].apply(
#         lambda x: ' - '.join(x.dropna().astype(str)), axis=1)
#     content = content.fillna('').groupby(['dssid','category'])['textcontent'].apply(
#         ' | '.join).reset_index()
    
#     # Merge to a complete table
#     dss = pd.merge(content, matscrib, on='dssid', how='outer')

#     ov_table = dss[['dssid', 'siglum', 'title', 'site', 'cave', 'category', 
#                     'textcontent', 'phylactery', 'material', 'script', 'language', 
#                     'date', 'reconstr_len', 'url', 'top_margin', 'bottom_margin', 
#                     'right_margin', 'left_margin', 'between_cols', 'pageh_cm', 
#                     'colw_cm', 'colw_letters', 'colh_cm', 'colh_lines', 'drylines', 
#                     'distance_betweenlines', 'guidemarks', 'letterh_mm', 'color', 'ink',
#                     'surface', 'otherdesc']].copy()

#     return ov_table