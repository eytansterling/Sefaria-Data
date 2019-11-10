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

first_parshas=['Bereshit', 'Shemot', "Vayikra", 'Bamidbar','Devarim']



def get_parsha_ranges():
    return_dict={}
    for sefer in en_sefer_names:
        for node in library.get_index(sefer).alt_structs['Parasha']['nodes']:
            return_dict[node['sharedTitle']]=node['wholeRef']                
    return return_dict
def parse_text(posting=True):
    with open("תולדות יצחק.txt") as myFile:
        lines = list(map(lambda x: x.decode("utf-8",'replace'), myFile.readlines()))
    parsha_list=[]
    parsha_box=[]
    past_start=False
    just_passed_sefer=False
    for line in lines:
        if u'@00' in line:
            past_start=True
            just_passed_sefer=True
        if past_start:
            if u'@01' in line:
                just_passed_sefer=False
                if len(parsha_box)>0:
                    parsha_list.append(parsha_box)
                    parsha_box=[]
            elif not_blank(line) and u'@33' in line and not just_passed_sefer:
                parsha_box.append(line)
    parsha_list.append(parsha_box)
    """
    for pindex, parsha in enumerate(parsha_list):
        for lindex, line in enumerate(parsha):
            print eng_parshiot[pindex], lindex, line
    """
    #0/0
    if posting:
        for pindex, parsha in enumerate(parsha_list):
            version = {
                'versionTitle': "Toledot Yitzchak, Warsaw 1877",
                'versionSource': 'http://beta.nli.org.il/he/books/NNL_ALEPH002063331/NLI',
                'language': 'he',
                'text': parsha
            }
            #post_text("Ahavat Chesed, "+key, version, weak_network=True)
            #post_text("Toledot Yitzchak, {}".format(eng_parshiot[pindex]),  version,weak_network=True, skip_links=True, index_count="on")
            post_text_weak_connection("Toledot Yitzchak, {}".format(eng_parshiot[pindex]),  version)
    return parsha_list  
def not_blank(s):
    while " " in s:
        s = s.replace(u" ",u"")
    return (len(s.replace(u"\n",u"").replace(u"\r",u"").replace(u"\t",u""))!=0);

def post_index_ty():
    # create index record
    record = SchemaNode()
    record.add_title('Toledot Yitzchak', 'en', primary =True, )
    record.add_title(u'תולדות יצחק', 'he',primary= True, )
    record.key = 'Toledot Yitzchak'
    
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
        "title": "Toledot Yitzchak",
        "categories": ["Chasidut"],
        "schema": record.serialize()
    }
    post_index(index)

def produce_link_sheets():
    parsha_ranges=get_parsha_ranges()
    for sefer_name in en_sefer_names:
        with open('Toledot_Yitzchak_{}_links.tsv'.format(sefer_name),'w') as record_file:
            for node in library.get_index(sefer_name).alt_structs['Parasha']['nodes']:
                parsha_name=node['sharedTitle']
                print "linking...",parsha_name
                ty_text=TextChunk(Ref('Toledot Yitzchak, '+parsha_name),'he').text
                last_not_matched = []
                #last_matched = Ref('{}, {}:1'.format(sefer_name,chapter))
                print '{}, {}'.format(sefer_name, parsha_name)
                base_chunk = TextChunk(Ref(parsha_ranges[parsha_name]),"he",'Tanach with Text Only')
                com_chunk = TextChunk(Ref('Toledot Yitzchak, {}'.format(parsha_name)),"he")
                #print "THE BASE",base_chunk.text[0]
                ch_links = match_ref(base_chunk,com_chunk,base_tokenizer,dh_extract_method=dh_extract_method,rashi_filter=_filter,boundaryFlexibility=20)
                for link_index, (base, comment) in enumerate(zip(ch_links["matches"],ch_links["comment_refs"])):
                    if base:
                        print "B",base,"C", comment
                        if "Yitz" in base.normal():
                            ty=base.normal()
                            pasuk=comment.normal()
                        else:
                            ty=comment.normal()
                            pasuk=base.normal()
                        record_file.write('{}\t{}\t{}\n'.format(ty,TextChunk(Ref(ty),'he').text.replace(u'\n',u'').encode('utf','replace'), Ref(pasuk).normal()))
                        last_matched=base
                    else:
                        record_file.write('{}\t{}\tNULL\n'.format(comment.normal(),TextChunk(Ref(comment.normal()),'he').text.replace(u'\n',u'').encode('utf','replace')))
def get_full_text():
    with open("תולדות יצחק.txt") as myFile:
        lines = list(map(lambda x: x.decode("utf-8",'replace'), myFile.readlines()))
    sefer_list=[[],[],[],[],[]]
    add_to_next=[]
    past_start=False
    sefer_index=-1
    for rawline in lines:
        line=rawline.replace(u'\n',u'')
        if u'@00' in line:
            past_start=True
            just_passed_sefer=True
            sefer_index+=1
        if past_start:
            if u'@01' in line:
                just_passed_sefer=False
            elif not_blank(line) and not just_passed_sefer:
                if u'@33' not in line:
                    if len(sefer_list[sefer_index])>0:
                        sefer_list[sefer_index][-1]=sefer_list[sefer_index][-1]+u'<br>'+line
                    else:
                        add_to_next.append(line)
                else:
                    sefer_list[sefer_index].append(line)
                while len(add_to_next)>0 and len(sefer_list[sefer_index])>0:
                    sefer_list[sefer_index][-1]=add_to_next.pop(0)+u'<br'+sefer_list[sefer_index][-1]
    
    return sefer_list
def fix_link_sheets():
    sefer_list=get_full_text()

    for sindex, sefer in enumerate(en_sefer_names):
        rows=[]
        with open('fixed_files/Toledot_Yitzchak_links - Toledot_Yitzchak_{}_links.tsv'.format(sefer)) as tsvfile:
          reader = csv.reader(tsvfile, delimiter='\t')
          for row in reader:
              rows.append(row)
        with open('step_2/Toledot_Yitzchak_{}_2.tsv'.format(sefer),'w') as myfile:
            for rindex, row in enumerate(rows):
                if len(row)>3:
                    myfile.write('{}\t{}\t{}\t{}\n'.format(row[0],sefer_list[sindex][rindex].encode('utf','replace'),row[2],row[3]))
                else:
                    myfile.write('{}\t{}\t{}\t\n'.format(row[0],sefer_list[sindex][rindex].encode('utf','replace'),row[2],))
                    
                        
def _filter(some_string):
    return True

def dh_extract_method(some_string):
    return re.search(ur'(?<=@11).*?(?=\.?\s*@33)', some_string).group()

def base_tokenizer(some_string):
    return filter(lambda(x): x!=u'',remove_extra_spaces(some_string.replace(u"<b>",u"").replace(u"</b>",u"").replace(u".",u"")).split(" "))
def remove_extra_spaces(string):
    string = re.sub(ur"\. $",u".",string)
    while u"  " in string:
        string=string.replace(u"  ",u" ")
    return string
def from_parasha_index_to_sefer(parasha_index):
    if parasha_index<13:
        return "Genesis"
    if parasha_index<24:
        return "Exodus"
    if parasha_index<34:
        return "Leviticus"
    if parasha_index<44:
        return "Numbers"
    return "Deuteronomy"    
     
#post_index_ty()
#parse_text()
#produce_link_sheets()
fix_link_sheets()


"""

12


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