# -*- coding: utf-8 -*-
import os
import re
import sys
p = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, p)
from sources.local_settings import *
sys.path.insert(0, SEFARIA_PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = "local_settings"
from sources.functions import *
import codecs
from fuzzywuzzy import fuzz
term_exceptions=['Shavuot',"Esther","Song of Songs","Ruth","Lamentations","Ecclesiastes"]
heb_parshiot = [u"בראשית",u"נח", u"לך לך", u"וירא", u"חיי שרה", u"תולדות", u"ויצא", u"וישלח", u"וישב", u"מקץ",u'לחנוכה',
u"ויגש", u"ויחי", u"שמות", u"וארא", u"בא", u"בשלח", u"יתרו", u"משפטים", u"תרומה", u"תצוה", u"כי תשא",
u"ויקהל", u"פקודי", u"ויקרא", u"צו", u"שמיני", u"תזריע", u"מצרע", u"אחרי מות", u"קדשים", u"אמר", u"בהר",
u"בחקתי", u"במדבר", u'לשבועות',u"נשא", u"בהעלתך", u"שלח", u"קרח", u"חקת", u"בלק", u"פינחס", u"מטות",
u"מסעי", u"דברים", u"ואתחנן", u"עקב", u"ראה", u"שפטים", u"כי תצא", u"כי תבוא", u"נצבים",
u"וילך",u'לראש השנה ויום כפור', u"האזינו",u'לסוכות', u"וזאת הברכה",u'מגלת אסתר',
u'שיר השירים',u'מגלת רות',u'מגלת איכה',u'מגלת קהלת']

eng_parshiot = ["Bereshit", "Noach", "Lech Lecha", "Vayera", "Chayei Sara", "Toldot", "Vayetzei", "Vayishlach",
"Vayeshev", "Miketz","Channukah", "Vayigash", "Vayechi", "Shemot", "Vaera", "Bo", "Beshalach", "Yitro",
"Mishpatim", "Terumah", "Tetzaveh", "Ki Tisa", "Vayakhel", "Pekudei", "Vayikra", "Tzav", "Shmini",
"Tazria", "Metzora", "Achrei Mot", "Kedoshim", "Emor", "Behar", "Bechukotai", "Bamidbar", "Shavuot","Nasso",
"Beha'alotcha", "Sh'lach", "Korach", "Chukat", "Balak", "Pinchas", "Matot", "Masei",
"Devarim", "Vaetchanan", "Eikev", "Re'eh", "Shoftim", "Ki Teitzei", "Ki Tavo", "Nitzavim", "Vayeilech","Rosh Hashana and Yom Kippur","Ha'Azinu","Succot","V'Zot HaBerachah",
"Esther","Song of Songs","Ruth","Lamentations","Ecclesiastes"]
not_new_sections= [u'התעוררות לבעל תפלה',u'התעוררות לתקיעת שופר',u'התעוררות לתשובה']
empty_bmc=["Channukah"]

en_bmc_sections= eng_parshiot[:]
en_bmc_sections.insert(0,"Kuntres Meirat Einayim")
en_bmc_sections.remove("Channukah")

he_bmc_sections = heb_parshiot[:]
he_bmc_sections.insert(0,u'קונטרס מאירת עינים')
he_bmc_sections.remove(u'לחנוכה')
match_dict = heb_parshiot[:]

for section in not_new_sections:
    match_dict.append(section)

ref_dic={parsha:0 for parsha in eng_parshiot}
def post_index_bst():
    # create index record
    record = SchemaNode()
    record.add_title('Baal Shem Tov on Torah', 'en', primary =True, )
    record.add_title(u'בעל שם טוב על תורה', 'he',primary= True, )
    record.key = 'Baal Shem Tov on Torah'
    
    #add node for introduction
    intro_node = JaggedArrayNode()
    intro_node.add_title('Introduction', 'en', primary = True)
    intro_node.add_title(u'הקדמה', 'he',  primary =True)
    intro_node.key = 'Introduction'
    intro_node.depth = 1
    intro_node.addressTypes = ['Integer']
    intro_node.sectionNames = ['Paragraph']
    record.append(intro_node)

    #now for sefer nodes:
    for parsha in eng_parshiot:
        parsha_node = JaggedArrayNode()
        if Term().load({"name":parsha}) and parsha not in term_exceptions:
            parsha_node.add_shared_term(parsha)
        else:
            parsha_node.add_title(parsha, 'en', primary = True)
            parsha_node.add_title(heb_parshiot[eng_parshiot.index(parsha)], 'he',  primary =True)
        parsha_node.key = parsha
        parsha_node.depth = 2
        parsha_node.addressTypes = ['Integer', 'Integer']
        parsha_node.sectionNames = ['Comment','Paragraph']
        record.append(parsha_node)

    record.validate()

    index = {
        "title": "Baal Shem Tov on Torah",
        "categories": ["Chasidut"],
        "schema": record.serialize()
    }
    post_index(index)
def parse_bst():
    with open('בעל שם ראשי מוכן.txt') as myfile:
        lines = list(map(lambda(x): x.decode('utf','replace'), myfile.readlines()))
    """
    #first intros
    past_start=False
    bst_intro=[]
    for line in lines:
        if u'הקדמה לספר הקדוש בעל שם טוב זי"ע' in line:
            past_start=True
        if past_start:
            bst_intro.append(re.sub(ur"@\d{1,4}",u"",line))
        if u'@11הקדמה' in line:
            break
    version = {
        'versionTitle': 'VERSION TITLE',
        'versionSource': 'VERSION SOURCE',
        'language': 'he',
        'text': bst_intro
    }
    post_text_weak_connection('Baal Shem Tov on Torah, Introduction', version)
    """
    past_start = False
    parsha_dict = {}
    section_box = []
    for line in lines:
        if u'@65פרשת' in line:
            past_start=True
        if past_start and not_blank(line):
            if u'@65' in line and highest_fuzz(match_dict, line.replace(u'פרשת',u'')) not in not_new_sections:
                if len(section_box)>0:
                    parsha_dict[current_parsha].append(section_box)
                    section_box=[]
                current_parsha= highest_fuzz(heb_parshiot, line.replace(u'פרשת',u''))
                parsha_dict[current_parsha]=[]
                print current_parsha
                print line
            elif u'@00' in line:
                if len(section_box)>0:
                    parsha_dict[current_parsha].append(section_box)
                    section_box=[]
                section_box.append(clean_line(line))
            else:
                section_box.append(clean_line(line))

    #now fix inline refs
    for key in heb_parshiot:
        if key in parsha_dict.keys():
            parsha_dict[key]=insert_inline_tags(parsha_dict[key], key)
    
    offset=0
    for kindex, key in enumerate(heb_parshiot):
        if kindex+1-offset>=len(counts):
            print "!!",eng_parshiot[heb_parshiot.index(key)],"BST: ",ref_dic[key]," BMC: NONE"
        elif ref_dic[key]==0:
            offset+=1
            print key,ref_dic[key],0
        elif ref_dic[key]==counts[kindex+1-offset]:
            print eng_parshiot[heb_parshiot.index(key)],"BST: ",ref_dic[key]," BMC: ", counts[kindex+1-offset]
        else:
            print "!!",eng_parshiot[heb_parshiot.index(key)],"BST: ",ref_dic[key]," BMC: ", counts[kindex+1-offset]
            
    1/0
       
    for key in parsha_dict:
        for sindex, section in enumerate(parsha_dict[key]):
            for pindex, paragraph in enumerate(section):
                print key, sindex, pindex, paragraph
     

    for key in parsha_dict.keys():
        version = {
            'versionTitle': 'VERSION TITLE',
            'versionSource': 'VERSION SOURCE',
            'language': 'he',
            'text': parsha_dict[key]
        }
        post_text_weak_connection('Baal Shem Tov on Torah, '+eng_parshiot[heb_parshiot.index(key)], version)
        #post_text('Baal Shem Tov on Torah, '+eng_parshiot[heb_parshiot.index(key)], version, weak_network=True)
        
def clean_line(s):
    s= re.sub(ur'@00\S*\.? *',u'',s)
    s = s.replace(u'@11',u'<b>').replace(u'@22',u'</b>').replace(u'@88',u'<b>').replace(u"@99",u'</b>')
    s = re.sub(ur"@\d{1,4}",u"",s)
    for match in re.findall(ur'(?<=:)\s*\(.*?\)$',s):
        s = s.replace(match, u'<br><small>'+match+u'</small>')
    return s
def insert_inline_tags(parsha_array, parsha):
    footnote_count=1
    found=False
    new_array=[]
    section_box=[]
    for section in parsha_array:
        for paragraph in section:
            while u'&{*}' in paragraph:
                paragraph=paragraph[:paragraph.index(u'&{*}')]+u"<i data-commentator=\"Mekor Mayim Chayim\" data-order=\""+str(footnote_count)+"\"></i>"+paragraph[paragraph.index(u'&{*}')+4:]
                footnote_count+=1
                found=True
            section_box.append(paragraph)
            section_box=[]
        new_array.append(section_box)
    print parsha,footnote_count-1
    ref_dic[parsha]=footnote_count-1
    return new_array
counts=[]
def post_bmc_term():
    term_obj = {
        "name": "Mekor Mayim Chayim",
        "scheme": "commentary_works",
        "titles": [
            {
                "lang": "en",
                "text": "Mekor Mayim Chayim",
                "primary": True
            },
            {
                "lang": "he",
                "text": u'מקור מים חיים',
                "primary": True
            }
        ]
    }
    post_term(term_obj)
def bmc_index_post():
    # create index record
    record = SchemaNode()
    record.add_title('Mekor Mayim Chayim on Baal Shem Tov', 'en', primary =True, )
    record.add_title(u'מקור מים חיים על בעל שם טוב', 'he',primary= True, )
    record.key = 'Mekor Mayim Chayim on Baal Shem Tov'

    #now for sefer nodes:
    for parsha in en_bmc_sections:
        parsha_node = JaggedArrayNode()
        if Term().load({"name":parsha}) and parsha not in term_exceptions:
            parsha_node.add_shared_term(parsha)
        else:
            parsha_node.add_title(parsha, 'en', primary = True)
            parsha_node.add_title(he_bmc_sections[en_bmc_sections.index(parsha)], 'he',  primary =True)
        parsha_node.key = parsha
        parsha_node.depth = 2
        parsha_node.addressTypes = ['Integer', 'Integer']
        parsha_node.sectionNames = ['Comment','Paragraph']
        record.append(parsha_node)

    record.validate()

    index = {
        "title": "Mekor Mayim Chayim on Baal Shem Tov",
        "categories": ["Chasidut"],
        "dependence": "Commentary",
        "collective_title": "Mekor Mayim Chayim",
        "schema": record.serialize()
    }
    post_index(index)
def mmc_parse():
    with open('מקור חיים הכל מוכן.txt') as myfile:
        lines = list(map(lambda(x): x.decode('utf','replace'), myfile.readlines()))
    """
    #to test how texts match
    count=0
    for line in lines:
        if u"&{*}א)" in line and not_blank(line):
            if count>0:
                #print count
                counts.append(count)
            count=0
        if u'&{*}' in line:    
            count+=1
    print len(eng_parshiot)
    """
    final_parsha_dict={}
    parsha_box=[]
    comment_box =[]
    parsha_index=0
    for line in lines:
        if not_blank(line):
            if u"&{*}" in line and len(comment_box)>0:
                parsha_box.append(comment_box)
                comment_box=[]
            if u"&{*}א)" in line and len(parsha_box)>0:
                if parsha_index>=len(en_bmc_sections):
                    break

                final_parsha_dict[en_bmc_sections[parsha_index]]=parsha_box
                parsha_box=[]
                parsha_index+=1
                while en_bmc_sections[parsha_index] in empty_bmc:
                    parsha_index+=1
            comment_box.append(bmc_clean_line(line))
    """
    #finish last box
    parsha_box.append(comment_box)
    final_parsha_dict[en_bmc_sections[parsha_index]]=parsha_box
    """
    
    """
    #print test
    for parsha in final_parsha_dict.keys():
        for sindex, section in enumerate(final_parsha_dict[parsha]):
            for pindex, paragraph in enumerate(section):
                print parsha, sindex, pindex, paragraph
    """
    for parsha in final_parsha_dict.keys():
        version = {
            'versionTitle': 'Sefer Baal Shem Tov. Lodz, 1938',
            'versionSource': 'http://primo.nli.org.il/primo_library/libweb/action/dlDisplay.do?vid=NLI&docId=NNL_ALEPH001944944',
            'language': 'he',
            'text': final_parsha_dict[parsha]
        }
        post_text_weak_connection('Mekor Mayim Chayim on Baal Shem Tov", '+parsha, version)
        #post_text('Baal Shem Tov on Torah, '+eng_parshiot[heb_parshiot.index(key)], version, weak_network=True)
def bmc_clean_line(s):
    s = re.sub(ur'&\{\*\}\S*\)',u'',s)
    return re.sub(ur"@\d{1,4}",u"",s)

                
    
def not_blank(s):
    while " " in s:
        s = s.replace(u" ",u"")
    return (len(s.replace(u"\n",u"").replace(u"\r",u"").replace(u"\t",u""))!=0);
def highest_fuzz(input_list, input_item):
    highest_ratio = 0
    best_match = u''
    for item in input_list:
        if fuzz.ratio(input_item,item)>highest_ratio:
            best_match=item
            highest_ratio=fuzz.ratio(input_item,item)
    return best_match
#post_index_bst()
#post_bmc_term()
bmc_index_post()
mmc_parse()
#parse_bst()
"""
"Inspiration for the Prayer Leader","Inspiration for the Shofar Blower","Inspiration for Repentence"
"""