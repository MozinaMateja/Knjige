import requests
import re
import orodja

vzorec_bloka = re.compile(
    r'<tr itemscope itemtype="http://schema.org/Book">.*?'
    r'</div>\s*\n</div>\s*</td>\s*</tr>',
    flags=re.DOTALL
)
vzorec = re.compile(
    r'itemprop="url" href="/book/show/(?P<id>\d+).*'
    r"\n\s*<span itemprop='name'.*'4'>(?P<naslov>.*?)(\s\((?P<zbirka>.*?) #.*\))?</span>"
    r'\n</a>\s*<br/>'
    r"\n\s*<span class='by'>by</span>"
    r"\n<span itemprop='author' itemscope='' itemtype='http://schema.org/Person'>"
    r"\n<div class='authorName__container'>"
    r'\n<a class="authorName".*href="https:.*?show/(?P<id_avtorja>\d+)..*?"><span itemprop="name">(?P<avtor>.*)</span></a>.*?'
    r'\n</div>'
    r'\n</span>'
    r'\n\n\s*<br/>'
    r'\n\s*<div>'
    r'\n\s*<span class="greyText smallText uitext">'
    r'\n\s*<span class="minirating">.*?</span></span> (?P<ocena>.*) avg rating &mdash; (?P<stevilo_ocen>.*) ratings</span>'
    r'\n\s*&mdash;'
    r'\n\s*.*?publi.*'
    r'\n\s*(?P<leto>.*)'
    r'\n\s*&mdash; added by'
    r'\n\s*(?P<glasovi>.*) people'
)

vzorec_zbirke = re.compile(r"\n\s*<span itemprop='name'.*'4'>.*?\s\((?P<zbirka>.*?) #.*\)</span>")

def spremeni(blok):
    knjiga = vzorec.search(blok).groupdict()
    knjiga['id'] = int(knjiga['id'])
    knjiga['id_avtorja'] = int(knjiga['id_avtorja'])
    knjiga['avtor'] = knjiga['avtor'].replace("&#39", "'").replace("&amp;", "&").replace("&quot;", "'")
    knjiga['naslov'] = knjiga['naslov'].replace("&#39", "'").replace("&amp;", "&").replace("&quot;", "'")
    knjiga['ocena'] = float(knjiga['ocena'])
    knjiga['stevilo_ocen'] = int(knjiga['stevilo_ocen'].replace(',', ''))
    knjiga['leto'] = int(knjiga['leto'])
    knjiga['glasovi'] = int(knjiga['glasovi'].replace(',', ''))
    zbirka = vzorec_zbirke.search(blok)
    if zbirka:
        knjiga['zbirka'] = knjiga['zbirka'].replace("&amp;", "&")
        if knjiga['zbirka'][-1] == ',':
            knjiga['zbirka'] = knjiga['zbirka'][:-1]
    else:
        knjiga['zbirka'] = None
    return knjiga
    
def ena_stran(stevilka):
    url=f'https://www.goodreads.com/book/popular_by_date/{stevilka}/'
    datoteka = f'najbolj-popularne-knjige/{stevilka}.html'
    orodja.shrani_spletno_stran(url, datoteka)
    vsebina = orodja.vsebina_datoteke(datoteka)
    for blok in vzorec_bloka.finditer(vsebina):
        yield spremeni(blok.group(0))
        
seznam = []
for stevilka_leta in range(1920, 2021):
    for i in ena_stran(stevilka_leta):
        seznam.append(i)
orodja.zapisi_json(seznam, 'obdelani-podatki/knjige.json')
orodja.zapisi_csv(seznam, ['id', 'naslov', 'zbirka', 'id_avtorja', 'avtor', 'ocena', 'stevilo_ocen', 'leto', 'glasovi'], 'obdelani-podatki/knjige.csv')

