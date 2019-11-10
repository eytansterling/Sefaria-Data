# -*- coding: utf-8 -*-
import os
import re
import sys
p = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, p)
from sources.local_settings import *
sys.path.insert(0, SEFARIA_PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = "sefaria.settings"
import django
django.setup()
from sources.functions import *

en_sefer_names = ["Genesis","Exodus","Leviticus","Numbers","Deuteronomy"]

heb_parshiot = [u"בראשית",u"נח", u"לך לך", u"וירא", u"חיי שרה", u"תולדות", u"ויצא", u"וישלח", u"וישב", u"מקץ",
u"ויגש", u"ויחי", u"שמות", u"וארא", u"בא", u"בשלח", u"יתרו", u"משפטים", u"תרומה", u"תצוה", u"כי תשא",
u"ויקהל", u"פקודי", u"ויקרא", u"צו", u"שמיני", u"תזריע", u"מצורע", u"אחרי מות", u"קדושים", u"אמור", u"בהר",
u"בחוקתי", u"במדבר", u"נשא", u"בהעלותך", u"שלח לך", u"קרח", u"חקת", u"בלק", u"פינחס", u"מטות",
u"מסעי", u"דברים", u"ואתחנן", u"עקב", u"ראה", u"שופטים", u"כי תצא", u"כי תבוא", u"נצבים",
u"וילך", u"האזינו", u"וזאת הברכה"]

eng_parshiot = ["Bereshit", "Noach", "Lech Lecha", "Vayera", "Chayei Sara", "Toldot", "Vayetzei", "Vayishlach",
"Vayeshev", "Miketz", "Vayigash", "Vayechi", "Shemot", "Vaera", "Bo", "Beshalach", "Yitro",
"Mishpatim", "Terumah", "Tetzaveh", "Ki Tisa", "Vayakhel", "Pekudei", "Vayikra", "Tzav", "Shmini",
"Tazria", "Metzora", "Achrei Mot", "Kedoshim", "Emor", "Behar", "Bechukotai", "Bamidbar", "Nasso",
"Beha'alotcha", "Sh'lach", "Korach", "Chukat", "Balak", "Pinchas", "Matot", "Masei",
"Devarim", "Vaetchanan", "Eikev", "Re'eh", "Shoftim", "Ki Teitzei", "Ki Tavo", "Nitzavim", "Vayeilech", "Ha'Azinu",
"V'Zot HaBerachah"]



def get_parsha_ranges():
    return_dict={}
    for sefer in en_sefer_names:
        for node in library.get_index(sefer).alt_structs['Parasha']['nodes']:
            return_dict[node['sharedTitle']]=node['wholeRef']                
    return return_dict

def parse_text():
    with open("רזא.txt") as myFile:
        lines = list(map(lambda x: x.decode("utf-8",'replace'), myFile.readlines()))
    parsha_list=[]
    parsha_box=[]
    past_start=False
    for line in lines:
        if u'@בראשית' in line:
            past_start=True
        if past_start:
            if u'@' in line:
                if len(parsha_box)>0:
                    parsha_list.append(parsha_box)
                    parsha_box=[]
            if not_blank(line):
                parsha_box.append(line)
    parsha_list.append(parsha_box)
    """
    for pindex, parsha in enumerate(parsha_list):
        for lindex, line in enumerate(parsha):
            print eng_parshiot[pindex], lindex, line
    """
    #0/0
    for pindex, parsha in enumerate(parsha_list):
        version = {
            'versionTitle': "Paaneach Raza, Warsaw 1877",
            'versionSource': 'http://beta.nli.org.il/he/books/NNL_ALEPH002063331/NLI',
            'language': 'he',
            'text': parsha
        }
        print "posting {}...".format(eng_parshiot[pindex])
        #post_text("Ahavat Chesed, "+key, version, weak_network=True)
        post_text("Paaneach Raza, {}".format(eng_parshiot[pindex]),  version,weak_network=True, skip_links=True, index_count="on")
    
def not_blank(s):
    while " " in s:
        s = s.replace(u" ",u"")
    return (len(s.replace(u"\n",u"").replace(u"\r",u"").replace(u"\t",u""))!=0);

def post_index_pr():
    # create index record
    record = SchemaNode()
    record.add_title('Paaneach Raza', 'en', primary =True, )
    record.add_title(u'פענח רזא', 'he',primary= True, )
    record.key = 'Paaneach Raza'
    
    #now for sefer nodes:
    for parsha in eng_parshiot:
        parsha_node = JaggedArrayNode()
        if Term().load({"name":parsha}):
            parsha_node.add_shared_term(parsha)
        else:
             print parsha
             0/0
        parsha_node.key = parsha
        parsha_node.depth = 1
        parsha_node.addressTypes = ['Integer']
        parsha_node.sectionNames = ['Paragraph']
        record.append(parsha_node)

    record.validate()

    index = {
        "title": "Paaneach Raza",
        "categories": ["Chasidut"],
        "schema": record.serialize()
    }
    post_index(index)

def produce_link_sheets():
    parsha_ranges=get_parsha_ranges()
    for sefer_name in en_sefer_names:
        with open('Paaneach_Raza_{}_links.tsv'.format(sefer_name),'w') as record_file:
            for node in library.get_index(sefer_name).alt_structs['Parasha']['nodes']:
                parsha_name=node['sharedTitle']
                ty_text=TextChunk(Ref('Paaneach Raza, '+parsha_name),'he').text
                print '{}, {}'.format(sefer_name, parsha_name)
                base_chunk = TextChunk(Ref(parsha_ranges[parsha_name]),"he",'Tanach with Text Only')
                com_chunk = TextChunk(Ref('Paaneach Raza, {}'.format(parsha_name)),"he")
                ch_links = match_ref(base_chunk,com_chunk,base_tokenizer,dh_extract_method=dh_extract_method,rashi_filter=_filter)
                last_ref=''
                not_linked=[]
                for link_index, (base, comment) in enumerate(zip(ch_links["matches"],ch_links["comment_refs"])):
                    if base:
                        print "B",base,"C", comment
                        print "LR",last_ref
                        if last_ref==base.normal().split('-')[0]:
                            print "LOGICAL"
                            while len(not_linked)>0:
                                adding=not_linked.pop(0)
                                record_file.write('{}\t{}\t{}\n'.format(adding,TextChunk(Ref(adding),'he').text.encode('utf','replace').replace('\n',''),Ref(last_ref).normal()))
                                
                        else:
                            print "ILLOGICAL"
                            onto_next=False
                            while len(not_linked)>0:
                                adding=not_linked.pop(0)
                                if u'ד"א' in TextChunk(Ref(adding),'he').text.split(u' ')[0] and not onto_next:
                                    record_file.write('{}\t{}\t{}\n'.format(comment.normal(),TextChunk(Ref(adding),'he').text.encode('utf','replace').replace('\n',''), Ref(last_ref).normal()))
                                else:
                                    onto_next=True
                                    record_file.write('{}\t{}\tNULL\n'.format(adding,TextChunk(Ref(adding),'he').text.encode('utf','replace').replace('\n','')))
                                
                        last_ref = base.normal()  
                        record_file.write('{}\t{}\t{}\n'.format(comment.normal(),TextChunk(comment,'he').text.encode('utf','replace').replace('\n',''), base.normal()))

                    else:
                        not_linked.append(comment.normal())
                        

 
def _filter(some_string):
    return True

def dh_extract_method(some_string):
    #if len(some_string.split(u',')[0].split(u' '))<16:
    #    return some_string.split(u',')[0]
    return u' '.join(some_string.replace(u',',u'').split(u' ')[:5])

def base_tokenizer(some_string):
    return filter(lambda(x): x!=u'',remove_extra_spaces(some_string.replace(u"<b>",u"").replace(u"</b>",u"").replace(u".",u"")).split(" "))
def remove_extra_spaces(string):
    string = re.sub(ur"\. $",u".",string)
    while u"  " in string:
        string=string.replace(u"  ",u" ")
    return string
    
     
#post_index_pr()
#parse_text()
produce_link_sheets()

"""
 מקרא:
@00 סדר
@01 פרשה
@11 תחילת קטע ציטוט
@22 תחילת קטע בהקדמה (חרוזים)
@33 סוף ציטוט 
@44 תחילת קטע לא ציטוט
@55 סוף תחילת קטע לא ציטוט
@66 מודגש
@77 סוף הדגשה
@88 תו TAB
@99 כותר סיום
"""