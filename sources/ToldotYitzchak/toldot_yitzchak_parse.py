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
    for pindex, parsha in enumerate(parsha_list):
        version = {
            'versionTitle': "Toledot Yitzchak, Warsaw 1877",
            'versionSource': 'http://beta.nli.org.il/he/books/NNL_ALEPH002063331/NLI',
            'language': 'he',
            'text': parsha
        }
        #post_text("Ahavat Chesed, "+key, version, weak_network=True)
        post_text("Toledot Yitzchak, {}".format(eng_parshiot[pindex]),  version,weak_network=True, skip_links=True, index_count="on")
    
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
        for node in library.get_index(sefer).alt_structs['Parasha']['nodes']:
            parsha_name=node['sharedTitle']
            ty_text=TextChunk(Ref('Toledot Yitzchak, '+parsha_name),'he').text
            last_not_matched = []
            #last_matched = Ref('{}, {}:1'.format(sefer_name,chapter))
            print '{}, {}'.format(sefer_name, parsha_name)
            base_chunk = TextChunk(Ref(parsha_ranges[parsha_name]),"he",'Tanach with Text Only')
            com_chunk = TextChunk(Ref('Toledot Yitzchak, {}'.format(parsha_name)),"he")
            #print "THE BASE",base_chunk.text[0]
            ch_links = match_ref(base_chunk,com_chunk,base_tokenizer,dh_extract_method=dh_extract_method,rashi_filter=_filter)
            #print "KEYS:"
            #for key_thing in ch_links.keys():
            #    print key_thing
            #print sefer_name
            #print "BASE ",len(base_chunk.text)
            #print "COM ",len(com_chunk.text)
            #if 'comment_refs' not in ch_links:
            #    print 'NONE for chapter ',chapter
            #    continue
            for link_index, (base, comment) in enumerate(zip(ch_links["matches"],ch_links["comment_refs"])):
                if base:
                    """
                    while len(last_not_matched)>0:
                        print "we had ", last_matched.normal()
                        print "we have ", base.normal()
                        response_set=list(map(lambda(x): int(x),(last_matched.normal().split(':')[-1]+"-"+base.ending_ref().normal_last_section()).split('-')))
                        print "RESPONSE",response_set, "MAX", max(response_set), "MIN", min(response_set)
                        print "so, we'll do ",'{}-{}'.format(min(response_set),max(response_set))
                        first_link='{} {}{}-{}'.format(' '.join(last_matched.normal().split()[:-1]),re.search(ur'\d+:',last_matched.normal()).group(),min(response_set),max(response_set))
                        lnm = last_not_matched.pop(0).normal()
                        if "Lek" in lnm:
                            etz=lnm
                            mid=first_link
                        else:
                            etz=first_link
                            mid=lnm
                        if Ref(mid).starting_ref()==Ref(mid).ending_ref():
                            record_file.write("{}\t{}\n".format(TextChunk(Ref(etz),'he').text.encode('utf','replace'), Ref(mid).normal()))
                        else:
                            record_file.write("{}\t\n".format(TextChunk(Ref(etz),'he').text.encode('utf','replace')))
                    """
                    print "B",base,"C", comment
                    if "Yitz" in base.normal():
                        ty=base.normal()
                        pasuk=comment.normal()
                    else:
                        ty=comment.normal()
                        pasuk=base.normal()
                    record_file.write('{}\t{}\n'.format(TextChunk(Ref(ty),'he').text.encode('utf','replace'), Ref(pasuk).normal()))
                    last_matched=base
                """
                else:
                    #not_machted.append('{}, {} Introduction'.format(key, section["en_title"]))
                    last_not_matched.append(comment.starting_ref())
                    if link_index==len(ch_links["matches"])-1:
                        print "NO LINKS LEFT!"
                        print "we had ", last_matched.normal()
                        print "so, we'll do ",last_matched.normal()+"-"+str(len(base_chunk.text))
                        while len(last_not_matched)>0:
                            lnm=last_not_matched.pop(0).normal()
                            first_link=last_matched.normal().split('-')[0]+"-"+str(len(base_chunk.text))
                            if "Lek" in lnm:
                                etz=lnm
                                mid=first_link
                            else:
                                etz=first_link
                                mid=lnm
                            if Ref(mid).starting_ref()==Ref(mid).ending_ref():
                                record_file.write('{}\t{}\n'.format(TextChunk(Ref(etz),'he').text.encode('utf','replace'), Ref(mid).normal()))
                            else:
                                record_file.write('{}\t\n'.format(TextChunk(Ref(etz),'he').text.encode('utf','replace')))
                """
 
def _filter(some_string):
    return True

def dh_extract_method(some_string):
    return re.search(ur'(?<=@11).*?(?=@33)', some_string).group()

def base_tokenizer(some_string):
    return filter(lambda(x): x!=u'',remove_extra_spaces(some_string.replace(u"<b>",u"").replace(u"</b>",u"").replace(u".",u"")).split(" "))
def remove_extra_spaces(string):
    string = re.sub(ur"\. $",u".",string)
    while u"  " in string:
        string=string.replace(u"  ",u" ")
    return string
    
     
#post_index_ty()
#parse_text()


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