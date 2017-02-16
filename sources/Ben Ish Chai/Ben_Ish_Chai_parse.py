# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import sys
import os
# for a script located two directories below this file
p = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, p)
from sources.local_settings import *

sys.path.insert(0, SEFARIA_PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = "local_settings"
#from sefaria.model import *
from sources.functions import *
import re
import data_utilities
import codecs
import pycurl
import cStringIO
from bs4 import BeautifulSoup
eng_parshiot = ["Bereshit", "Noach", "Lech Lecha", "Vayera", "Chayei Sara", "Toldot", "Vayetzei", "Vayishlach",
"Vayeshev", "Miketz", "Vayigash", "Vayechi", "Shemot", "Vaera", "Bo", "Beshalach", "Yitro",
"Mishpatim", "Terumah", "Tetzaveh", "Ki Tisa", "Vayakhel", "Pekudei", "Vayikra", "Tzav", "Shmini",
"Tazria", "Metzora", "Achrei Mot", "Kedoshim", "Emor", "Behar", "Bechukotai", "Bamidbar", "Nasso",
"Beha'alotcha", "Sh'lach", "Korach", "Chukat", "Balak", "Pinchas", "Matot", "Masei",
"Devarim", "Vaetchanan", "Eikev", "Re'eh", "Shoftim", "Ki Teitzei", "Ki Tavo", "Nitzavim", "Vayeilech", "Ha'Azinu",
"V'Zot HaBerachah"]

eng_bereishit = ["Bereshit", "Noach", "Lech Lecha", "Vayera", "Chayei Sara", "Toldot", "Vayetzei", "Vayishlach","Vayeshev","Hannakah", "Miketz", "Vayigash", "Vayechi"]
eng_shemot = ["Shemot", "Vaera", "Bo", "Beshalach", "Yitro","Mishpatim", "Terumah", "Tetzaveh", "Ki Tisa", "Vayakhel", "Pekudei"]
eng_vayikra = ["Vayikra", "Tzav", "Shmini","Tazria Metzora","Achrei Mot Kedoshim", "Emor", "Behar Bechukotai",]
eng_bamidbar = ["Bamidbar", "Nasso","Beha'alotcha", "Sh'lach", "Korach", "Chukat", "Balak", "Pinchas", "Matot", "Masei"]
eng_devarim = ["Devarim", "Vaetchanan", "Eikev", "Re'eh", "Shoftim", "Ki Teitzei", "Ki Tavo", "Nitzavim", "Vayeilech", "Ha'Azinu",
"V'Zot HaBerachah"]
all_parshas = [eng_bereishit,eng_shemot,eng_vayikra,eng_bamidbar,eng_devarim]
eng_bereishit2 = ["Bereshit", "Noach", "Lech Lecha", "Vayera", "Chayei Sara", "Toldot", "Vayetzei", "Vayishlach", "Miketz", "Vayigash", "Vayechi"]
eng_shemot2 = ["Shemot", "Vaera", "Bo", "Beshalach", "Yitro","Mishpatim", "Terumah", "Tetzaveh", "Ki Tisa", "Vayakhel", "Pekudei"]
eng_vayikra2 = ["Vayikra", "Tzav", "Shmini","Tazria", "Metzora", "Achrei Mot", "Kedoshim", "Emor", "Behar Bechukotai"]
eng_bamidbar2 = ["Nasso","Beha'alotcha", "Sh'lach", "Korach", "Chukat", "Balak", "Pinchas", "Matot", "Masei"]
eng_devarim2 = ["Vaetchanan", "Eikev", "Re'eh", "Shoftim", "Ki Teitzei", "Ki Tavo"]
all_parshas2 = [eng_bereishit2,eng_shemot2,eng_vayikra2,eng_bamidbar2,eng_devarim2]

eng_parshas=[ all_parshas, all_parshas2]
def get_parsed_drasha():
    parsha_titles = get_intro_parshas()
    return_list = []
    for index, parsha in enumerate(get_drasha_text()):
        return_list.append([[parsha_titles[index].replace("\n","").strip(),eng_parshiot[index]],parsha])
    return return_list
def get_drasha_text():
    with open('בן איש חי דרשות.txt') as myfile:
        ascii_lines = myfile.readlines()
    lines = list(map(lambda(x): x.decode('utf_8','replace'),ascii_lines))
    parsha_box = []
    all_parshas = []
    for line in lines:
        if "@02" in line:
            all_parshas.append(parsha_box)
            parsha_box = []
        parsha_box.append(re.sub(ur"@\d+",u"",line).replace(u"T",""))
    all_parshas.append(parsha_box)
    return all_parshas[2:]
def get_halachas_shana_1():
    return get_parsed_halachas(1)
def get_halachas_shana_2():
    return get_parsed_halachas(2)
def get_parsed_halachas(shana_num):
    soup = url_to_soup("https://he.wikisource.org/wiki/%D7%91%D7%9F_%D7%90%D7%99%D7%A9_%D7%97%D7%99")
    links = soup.find_all('ul')
    #links = filter(lambda(x):x('li'),links)
    #for index, li in enumerate(links[1:3]):
    sefer_links = []
    for a in links[shana_num].find_all('a'):
        sefer_links.append('https://he.wikisource.org'+a['href'])
    complete_year = []
    for sefer_index, sefer_link in enumerate(sefer_links):
        #sefer_parshas contains each parsha, and each parsha contains 1 title, 1 intro and 1 2D list of sections
        parsha_count = -1
        sefer_soup=url_to_soup(sefer_link)
        for index, li in enumerate(sefer_soup.find_all('li')):
            try:
                if u"פרשת" in ''.join(li.find_all(text=True)) or u"פרשיות" in ''.join(li.find_all(text=True)):
                    parsha_count+=1
                    parsha_box = []
                    parsha_soup = url_to_soup('https://he.wikisource.org'+li.find('a')['href'])
                    parsha_box.append([''.join(li.find_all(text=True)),eng_parshas[shana_num-1][sefer_index][parsha_count] ])
                    intro_box = []
                    first_headline_box =[]
                    for headline in parsha_soup.find_all(class_="mw-headline"):
                        if ''.join(headline.find_all(text=True)).strip()==u"פתיחה":
                            first_headline_box.append(headline)
                    first_headline = first_headline_box[0]
                    text_start_index = 0
                    start_index =  parsha_soup(True).index(first_headline)
                    for item in parsha_soup(True)[start_index:]:
                        if not item.has_attr('class') and not item.has_attr('href') and not item.has_attr('size') and item.name!="b":
                            if ''.join(item.find_all(text=True)).strip()==ur"הלכות[עריכה]":
                                text_start_index = parsha_soup(True).index(item)
                                break
                            intro_box.append(''.join(item.find_all(text=True)).strip())
                    parsha_box.append(intro_box)
                    #load in text of halachot
                    section_box = []
                    halacha_box = []
                    for item in parsha_soup(True)[text_start_index:]:
                        if item.name == "p":
                            section_box.append(''.join(item.find_all(text=True)).strip())
                        else:
                            if len(section_box)>0:
                                halacha_box.append(section_box)
                                section_box=[]
                    parsha_box.append(halacha_box)
                    complete_year.append(parsha_box)
            except:
                q=0
    return complete_year
    
    
def get_parsed_intro():
    with open('בן איש חי דרשות.txt') as myfile:
        ascii_lines = myfile.readlines()
    lines = list(map(lambda(x): x.decode('utf_8','replace'),ascii_lines))
    section_box = []
    for line in lines:
        section_box.append(re.sub(ur"@\d+",u"",line).replace(u"T",""))
        if "@00" in line:
            section_box = []
        if u"@01ספר בראשית" in line:
            break
    return section_box
def get_intro_parshas():
    with open('בן איש חי דרשות.txt') as myfile:
        ascii_lines = myfile.readlines()
    lines = list(map(lambda(x): x.decode('utf_8','replace'),ascii_lines))
    parshas = []
    for line in lines:
        if u"@02" in line:
            parshas.append(re.sub(ur"@\d+",u"",line).replace(u"T",""))
    return parshas[1:]
def url_to_soup(url):
    chapter_buf = cStringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    
    c.setopt(c.WRITEFUNCTION, chapter_buf.write)
    c.perform()
    soup = BeautifulSoup(chapter_buf.getvalue(), 'html.parser')
    return soup;
def not_blank(s):
    while " " in s:
        s = s.replace(" ","")
    return (len(s.replace("\n","").replace("\r","").replace("\t",""))!=0);
def print_text():
    with open('בן איש חי דרשות.txt') as myfile:
        ascii_lines = myfile.readlines()
    lines = list(map(lambda(x): x.decode('utf_8','replace'),ascii_lines))
    for line in lines:
        print line
def main():
    pass
if __name__ == "__main__":
    #parse intro:
    version = {
        'versionTitle': 'Ben Ish Chai; Jerusalem, 1898',
        'versionSource': 'http://primo.nli.org.il/primo_library/libweb/action/dlDisplay.do?vid=NLI&docId=NNL_ALEPH001933796',
        'language': 'he',
        'text': get_parsed_intro()
    }
    post_text('Ben Ish Hai, Introduction', version, weak_network=True)
    #post all text
    parsha_sections = ["Drashot","Halachot Shana 1","Halachot Shana 2"]
    parsha_content = [get_parsed_drasha(), get_halachas_shana_1(), get_halachas_shana_2()]
    for section_name, section_content in zip(parsha_sections,parsha_content):
        for parsha in section_content:
            #add intro if not drashot:
            if "Drashot" not in section_name:
                version = {
                    'versionTitle': 'Ben Ish Chai; Jerusalem, 1898',
                    'versionSource': 'http://primo.nli.org.il/primo_library/libweb/action/dlDisplay.do?vid=NLI&docId=NNL_ALEPH001933796',
                    'language': 'he',
                    'text': parsha[1] 
                }
                print "posting "+section_name+", "+parsha[0][1]+", Introduction"
                post_text('Ben Ish Hai, '+section_name+", "+parsha[0][1]+", Introduction", version, weak_network=True)
            
            version = {
                'versionTitle': 'Ben Ish Chai; Jerusalem, 1898',
                'versionSource': 'http://primo.nli.org.il/primo_library/libweb/action/dlDisplay.do?vid=NLI&docId=NNL_ALEPH001933796',
                'language': 'he',
                'text': parsha[1] if "Drashot" in section_name else parsha[2]
            }
            print "posting "+section_name+", "+parsha[0][1]
            post_text('Ben Ish Hai, '+section_name+", "+parsha[0][1], version, weak_network=True)
    
    """
    #print parsha titles 
    print "Drasha"
    for paindex, parsha in enumerate(get_parsed_drasha()):
        print parsha[0][0]
        print parsha[0][1]
    print "Shana 1"
    for paindex, parsha in enumerate(get_halachas_shana_1()):
        print parsha[0][0]
        print parsha[0][1]
    print "Shana 2"
    for paindex, parsha in enumerate(get_halachas_shana_2()):
        print parsha[0][0]
        print parsha[0][1]
        #for parsha in sefer:
           # print "TITLE: "+parsha[0][0]+" "+parsha[0][1]
        """
    """
        print "INTRO:"
        for p in parsha[1]:
            print p
        print "HALACHOT:"
        for sindex, sec in enumerate(parsha[2]):
            for pindex, pa in enumerate(sec):
                print str(sindex)+" "+str(pindex)+" "+pa
    """
    """
    for section in get_parsed_drashas():
        print "SECTION:"
        for line in section:
            print line
    """
    main()