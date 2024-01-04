import sqlite3 as sql


def show_authors(namekeys, show_affil=False):
    '''
    Todo: identical affiliations for different authors, perhaps the SQL View is not necessary
    '''
    authors = ''
    affiliations = ''
    na = len(namekeys)
    for i, nk in enumerate(namekeys):
        name, orcid, aff, add = get_author(nk)

        # Oxford commas, handled at the start of a name
        if i > 0 and na > 2:
            authors += ', '
            if i == na-1:
                authors += 'and '
        if na == 2 and i == na-1:
            authors += ' and '
        authors += name + ' '

        # If to show affiliations
        if show_affil:
            authors += '<sup>%s,</sup>' %str(i+1)
        authors += orcid

        # affiliations += '<sup><sup><sub>%s </sub></sup></sup><sup><sub>%s'\
        #     '; %s</sub></sup>' %(str(i+1), aff, add)
        # if i < len(namekeys)-1:
        #     affiliations += '<br>'
    if show_affil:
        return authors, affiliations
    else:
        return authors


def get_author(namekey):
    conn = sql.connect('lyingpen.sqlite3')
    c = conn.cursor()
    auth = conn.execute(
        "SELECT author_name, author_orcid, author_dept, author_inst, "\
        "author_city, author_country FROM author_affiliation WHERE "\
        "namekey = '%s'" %(namekey,))
    name, orcid, dept, inst, city, country = auth.fetchone()
    affil = format_markdown_affiliation(dept, inst)
    address = format_markdown_address(city, country)
    return name, format_markdown_orcid(orcid), affil, address


def format_markdown_orcid(orcid):
    if orcid is not None:
        return '<sup>[![](https://info.orcid.org/wp-content/uploads/2019'\
            '/11/orcid_16x16.png)](https://orcid.org/' + orcid + ')</sup>'
    else:
        return ''


def format_markdown_affiliation(dept, inst):
    if dept is None:
        return inst
    else:
        return dept + ', ' + inst
    
def format_markdown_address(city, country):
    return city + ', ' + country


# if __name__ == '__main__':
#     get_author('matthewpm')