import pandas as pd
import sqlite3 as sql


def connection():
    conn = sql.connect('lyingpen.sqlite3')
    c = conn.cursor()
    return conn, c


def actor_getmuseums():
    conn, _ = connection()
    museums = pd.read_sql_query(
        """SELECT actor_id, actor_name, actor_abbrv
        FROM actor WHERE flag_owndss == 1""", conn)
    conn.close()
    return museums


def actor_getphotographers():
    conn, _ = connection()
    photographers = pd.read_sql_query(
        """SELECT actor_id, actor_name FROM actor 
        WHERE flag_isphotographer == 1""", conn)
    conn.close()
    return photographers


def site_getfullnames():
    conn, _ = connection()
    sites = pd.read_sql_query(
        """SELECT (CASE 
            WHEN cave_num NOTNULL THEN site_name || ' Cave ' || cave_num
            WHEN cave_num ISNULL THEN site_name END) sitefullname
        FROM dss_site""", conn)
    conn.close()
    return sites


def djd_getvols():
    conn, _ = connection()
    vols = pd.read_sql_query("""SELECT djd_vol FROM djd""", conn)
    vols[vols['djd_vol'] == '?'] = 'Unknown'
    conn.close()
    return vols


def phototype_getall():
    conn, _ = connection()
    phototype = pd.read_sql_query("""SELECT * FROM photo_type""", conn)
    conn.close()
    return phototype


def photocoll_getall():
    conn, _ = connection()
    photocoll = pd.read_sql_query("""SELECT * FROM photo_collection""", conn)
    conn.close()
    return photocoll


def photo_checknr(photonr):
    _, c = connection()
    return c.execute(
        """SELECT photo_nr FROM photos WHERE photo_nr=?""", 
        (photonr,)).fetchone()


def photo_addnew(photonr, **kwargs):
    conn, c = connection()
    idtoassign = c.execute(
        """SELECT MAX(photo_id) FROM photos""").fetchone()[0] + 1
    c.execute(
        """INSERT INTO photos(
            photo_id, photo_nr, photographer_id, date_month, date_year, 
            phototype_id, photocoll_id, photo_url, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        idtoassign, photonr, kwargs.get('photographerid'), kwargs.get('month'), 
        kwargs.get('year'), kwargs.get('typeid'), kwargs.get('collectionid'), 
        kwargs.get('url'), kwargs.get('notes')))
    conn.commit()
    conn.close()


def photo_getoverview():
    conn, _ = connection()
    return pd.read_sql_query(
        """SELECT p.photo_id, p.photo_nr, 
                pc.photocoll_name AS collection,
                pt.phototype_name AS phototype,
                a.actor_name AS photographer,
                p.date_month AS month,
                p.date_year AS year,
                p.photo_url AS url,
                p.notes AS notes
        FROM photos p
        LEFT JOIN actor a ON a.actor_id = p.photographer_id
        LEFT JOIN photo_collection pc ON pc.photocoll_id = p.photocoll_id
        LEFT JOIN photo_type pt ON pt.phototype_id = p.phototype_id
        ORDER BY photo_nr""", conn)


def photo_getnrs():
    conn, _ = connection()
    return pd.read_sql_query(
        """SELECT photo_id, photo_nr FROM photos ORDER BY photo_nr""", conn)


def photo_getentry_bynr(photonr):
    conn, _ = connection()
    return pd.read_sql_query(
        """SELECT * FROM photos WHERE photo_nr='%s'""" %photonr, conn)


def photo_getid_bynr(photonr, return_url=False):
    conn, c = connection()
    queried = c.execute(
        """SELECT photo_id, photo_url FROM photos WHERE photo_nr=?""", (
        photonr,)).fetchone()
    conn.close()
    if queried:
        if return_url:
            return queried[0], queried[1]
        else:
            return queried[0]
        

def pam_getgroup_byrange(pamrange):
    conn, c = connection()
    table_photo = None
    if '–' in pamrange:
        i, j = pamrange.split('–')
        table_photo = c.execute(
            """SELECT pamnr, group_concat(siglum), group_concat(title, ';'),
            group_concat(djdvol), group_concat(djdpl), 
            group_concat(djdfrg, ';'), pamurl, group_concat(site), 
            group_concat(sortnr)
            FROM cat_v_photos 
            WHERE pamnr >= '%s' AND pamnr <= '%s'
            GROUP BY pamnr""" %(i, j)).fetchall()
    else:
        table_photo = c.execute(
            """SELECT pamnr, group_concat(siglum), group_concat(title, ';'),
            group_concat(djdvol), group_concat(djdpl), 
            group_concat(djdfrg, ';'), pamurl, group_concat(site), 
            group_concat(sortnr)
            FROM cat_v_photos 
            WHERE pamnr LIKE 'I%'
            GROUP BY pamnr""").fetchall()
    conn.close()
    return table_photo


def catpamdjd_getall_bypamnr(pamnr):
    conn, _ = connection()
    pamid, pamurl = photo_getid_bynr(pamnr, return_url=True)
    table_pamcontent = pd.read_sql_query(
        """SELECT cat.cat_id, dm.siglum, dm.title, cat.pam_position,
        cat.pam_tags, 
        CASE WHEN cat.pam_flag_nolabel == 1 THEN 'No label'
            WHEN cat.pam_flag_illegiblelabel == 1 THEN 'Illegible label'
            WHEN cat.pam_flag_nolabel == 0 AND cat.pam_flag_illegiblelabel
                == 0 THEN cat.pam_labelonplate END pamlabel,
        djd.djd_vol, cat.djd_plate, cat.djd_col, cat.djd_frg, 
        cat.djd_ednotes, cat.remarks
        FROM cat_pamdjd cat
        LEFT JOIN dss_main dm ON dm.dss_id = cat.dss_id
        LEFT JOIN djd ON djd.djd_id = cat.djd_id
        WHERE pam_id=%s""" %(pamid, ), conn)
    conn.close()
    return pamid, pamurl, table_pamcontent


def catpamdjd_getall_byid(catid):
    conn, _ = connection()
    cat_entry = pd.read_sql_query(
        """SELECT dm.siglum, dm.title, cat.pam_position, cat.pam_flag_nolabel,
        cat.pam_flag_illegiblelabel, cat.pam_labelonplate, djd.djd_id,
        djd.djd_vol, cat.djd_plate, cat.djd_col, cat.djd_frg, 
        cat.pam_notesonplate, cat.djd_ednotes, cat.remarks
        FROM cat_pamdjd cat
        LEFT JOIN dss_main dm ON dm.dss_id = cat.dss_id
        LEFT JOIN djd ON djd.djd_id = cat.djd_id
        WHERE cat_id=%s""" %(catid, ), conn)
    conn.close()
    return cat_entry


def catpamdjd_delete_byid(catid, tocommit=False):
    conn, c = connection()
    c.execute("""DELETE FROM cat_pamdjd WHERE cat_id=?""", (catid,))
    if tocommit:
        conn.commit()
    conn.close()


def dss_getfullname_bysite(siteid):
    conn, _ = connection()
    dssfullname = pd.read_sql_query(
        """SELECT dss_id, (siglum || ' ' || title) AS fullname, 
        sorting_attr_siglnr
        FROM dss_main WHERE site_id=%s ORDER BY sorting_attr_siglnr""" \
        %siteid, conn)
    conn.close()
    return dssfullname


def plates_getall_bymuseumid(museumid):
    conn, _ = connection()
    plates = pd.read_sql_query(
        """SELECT p.plate_id, p.plate_nr, p.museum_id, 
        a.actor_name AS museumname, a.actor_abbrv AS museumabbrv, p.plate_url, 
        p.plate_photographer AS photographer_id, 
        aa.actor_name AS photographername, p.plate_year, p.flag_lostplate,
        p.flag_nonewleonlevyphoto, p.reed_notes
        FROM plates p
        LEFT JOIN actor a ON a.actor_id = p.museum_id
        LEFT JOIN actor aa ON aa.actor_id = p.plate_photographer
        WHERE museum_id=%s""" %museumid, conn)
    conn.close()
    return plates


def canon_getall_name2():
    conn, _ = connection()
    cats = pd.read_sql_query(
        """SELECT canon_gid, canon_gname2 FROM gr_canonical""", conn)
    conn.close()
    return cats


def texts_getall_bycanonids(canon_gids):
    conn, _ = connection()
    query = 'SELECT composition_gid, composition_gname, order_hebrewbible ' +\
        'FROM gr_composition WHERE canon_gid IN (' + ','.join(
        ['?'] * len(canon_gids)) + ') ORDER BY order_hebrewbible'
    args = [int(x) for x in canon_gids]
    texts = pd.read_sql_query(query, conn, params=args)
    conn.close()
    return texts


def scribal_getmanuscript_byid(dssid):
    conn, _ = connection()
    manuscript = pd.read_sql_query(
        """SELECT * FROM dss_v_physicalscribal WHERE dssid=%s""" %dssid, conn)
    content = pd.read_sql_query(
        """SELECT * FROM dss_textualcontent content
        LEFT JOIN gr_composition composition
            ON content.composition_id = composition.composition_gid
        WHERE dss_id='%s'""" %dssid, conn)
    conn.close()
    return manuscript, content


def scribal_getdocs_bytexts(textids):
    conn, _ = connection()
    query = 'SELECT * FROM wiki_v_bycatcomp WHERE textid IN (' + ','.join(
        ['?'] * len(textids)) + ') GROUP BY dssid ORDER BY siteid, sortingnr'
    args = [int(x) for x in textids]
    docs = pd.read_sql_query(query, conn, params=args)
    conn.close()
    return docs


def scribal_getdocs_bycats(catids):
    conn, _ = connection()
    query = 'SELECT * FROM wiki_v_bycatcomp WHERE catid IN (' + ','.join(
        ['?'] * len(catids)) + ') GROUP BY dssid ORDER BY siteid, sortingnr'
    args = [int(x) for x in catids]
    docs = pd.read_sql_query(query, conn, params=args)
    conn.close()
    return docs


def period_getall():
    conn, _ = connection()
    periods = pd.read_sql_query(
        """SELECT * FROM dss_period ORDER BY dssperiod_order""", conn)
    conn.close()
    return periods