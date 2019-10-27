# -*- coding: utf-8 -*-
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
import csv

titles={'Horayot':u'הוריות',
    'Niddah':u'נדה'}
def from_file_name_to_tractate(file_name):
    for key in titles.keys():
        if key in file_name:
            return key
def make_talmud_array(book):
    tc = TextChunk(Ref(book), "he")
    return_array = []
    for x in range(len(tc.text)):
        return_array.append([])
    return return_array
def extract_daf(s):
    return_dict = {}
    return_dict["daf"]= getGematria(s)    
    return_dict["amud"]= "a" if "." in s else "b"
    return return_dict
def not_blank(s):
    if isinstance(s,unicode):
        while u" " in s:
            s = s.replace(u" ",u"")
        return (len(s.replace(u"\n",u"").replace(u"\r",u"").replace(u"\t",u""))!=0);
    else:
        while " " in s:
            s = s.replace(" ","")
        return (len(s.replace("\n","").replace("\r","").replace("\t",""))!=0);
def clean_line(s):
    if u'.' in s:
        if len(s.split(u'.')[0].split(u' '))<16:
            return u'<b>'+s[:s.index('.')+1]+u'</b>'+s[s.index(u'.')+1:]
    return s
seders = {'Seder Tahorot':u'סדר טהרות','Seder Nezikin':u'סדר נזיקין'}
def get_mishnah_seder(mishnah_title):
    if u"Mishnah" not in mishnah_title:
        mishnah_title="Mishnah "+mishnah_title
    for seder in seders.keys():
        indices = library.get_indexes_in_category(seder)
        if mishnah_title in indices:
            return seder
class Tractate:
    def __init__(self, file_name):
        self.file_name=file_name
        self.en_name=from_file_name_to_tractate(file_name)
        self.he_name=titles[self.en_name]
    def parse(self):
        final_list=make_talmud_array(self.en_name)
        with open('files/'+self.file_name) as csvfile:
          reader = csv.reader(csvfile)
          for row in reader:
              line=row[1].decode('utf','replace')
              if not_blank(row[0]):
                  current_daf=extract_daf(row[0])
              #print "ROW1",row[1]
              if not_blank(line):
                  print "CL",clean_line(line)
                  final_list[get_page(current_daf['daf'],current_daf['amud'])].append(clean_line(line))
        final_list.insert(0,[])
        for dindex, daf in enumerate(final_list):
            for cindex, comment in enumerate(daf):
                print self.en_name, dindex, cindex, comment
        #0/0
        version = {
            'versionTitle': 'Talmud Bavli, Vilna 1883 ed.',
            'versionSource': 'http://primo.nli.org.il/primo_library/libweb/action/dlDisplay.do?vid=NLI&docId=NNL_ALEPH001300957',
            'language': 'he',
            'text': final_list
        }
        if 'local' in SEFARIA_SERVER:
            post_text('Tosafot HaRosh on {}'.format(self.en_name),  version,weak_network=True, skip_links=True, index_count="on")
        else:            
            post_text_weak_connection('Tosafot HaRosh on {}'.format(self.en_name),  version)
        
    def make_tractate_index(self):
        en_title = self.en_name
        he_title = self.he_name
        record = JaggedArrayNode()
        record.add_title('Tosafot HaRosh on '+en_title, 'en', primary=True)
        record.add_title(u"תוספות הרא\"ש על מסכת"+u" "+he_title, 'he', primary=True)
        record.key = 'Tosafot HaRosh on '+en_title
        record.depth = 2
        record.addressTypes = ['Talmud', 'Integer']
        record.sectionNames = ['Daf','Comment']
        record.validate()

        index = {
            "title":'Tosafot HaRosh on '+en_title,
            "base_text_titles": [
               en_title
            ],
            "collective_title":"Tosafot HaRosh",
            "dependence": "Commentary",
            "categories":["Talmud","Bavli","Commentary","Tosafot HaRosh", get_mishnah_seder(en_title)],
            "schema": record.serialize()
        }
        post_index(index,weak_network=True)
    def tr_link(self):
        for amud_index in range(1,len(TextChunk(Ref(self.en_name)).text)-1):
            if amud_index>0:
                #not every amud has a comment...
                try:
                    rc_ref=Ref('Tosafot HaRosh on '+self.en_name+"."+get_daf_en(amud_index))
                    rc_chunk = TextChunk(rc_ref,"he")
                except:
                    print "No RC on Rabbeinu Chananel on ",self.en_name,".",get_daf_en(amud_index)
                    continue
                #for Rav Channanel, each "comment" contains comments on several passages.
                #therefore, link each comment to the whole amud
                print get_daf_en(amud_index)
                tractate_ref=Ref(self.en_name+"."+get_daf_en(amud_index))
                tractate_chunk = TextChunk(tractate_ref,"he")
                matches = match_ref(tractate_chunk,rc_chunk,base_tokenizer,dh_extract_method=dh_extract_method,verbose=True)
                if "comment_refs" in matches:
                    for link_index, (base, comment) in enumerate(zip(matches["matches"],matches["comment_refs"])):
                        if base:
                            if "-" in base.normal():
                                base=Ref(base.normal().split("-")[0])
                            print "MATCHED BC:",base,comment,base.normal()+"-"+tractate_ref.as_ranged_segment_ref().normal().split("-")[-1]
                            link = (
                                    {
                                    "refs": [
                                             base.normal(),
                                             comment.normal(),
                                             ],
                                    "type": "commentary",
                                    "auto": True,
                                    "generated_by": "sterling_Tosafot_HaRosh_linker"
                                    })
                            post_link(link, weak_network=True)
def dh_extract_method(some_string):
    if u'.' in some_string and u'<b>' in some_string:
        return re.search(ur'(?<=<b>).*?(?=\.</b>)',some_string).group()
    return ' '.join(some_string.split(u' ')[:8])
def remove_extra_space(string):
    while u"  " in string:
        string = string.replace(u"  ",u" ")
    return string
def base_tokenizer(some_string):
    return filter(lambda(x): x!=u'',remove_extra_space(strip_nekud(some_string).replace(u"<b>",u"").replace(u"</b>",u"").replace(".","").replace(u"\n",u"")).split(u" "))
def get_daf_en(num):

    if num % 2 == 1:
        num = num / 2 + 2
        return str(num)+"a"

    else:
        num = num / 2 + 1
        return str(num)+"b"
def post_tr_term():
    term_obj = {
        "name": "Tosafot HaRosh",
        "scheme": "commentary_works",
        "titles": [
            {
                "lang": "en",
                "text": "Tosafot HaRosh",
                "primary": True
            },
            {
                "lang": "he",
                "text": u'תוספות הראש',
                "primary": True
            }
        ]
    }
    post_term(term_obj)
def add_cats():
    add_category('Tosafot HaRosh', ["Talmud","Bavli","Commentary","Tosafot HaRosh"],u"תוספות הרא\"ש")
    
    add_category('Seder Nezikin', ["Talmud","Bavli","Commentary","Tosafot HaRosh","Seder Nezikin"],u'סדר נזיקין')
    
    add_category('Seder Tahorot', ["Talmud","Bavli","Commentary","Tosafot HaRosh","Seder Tahorot"],u"סדר טהרות")
    
    
admin_links=[]
site_links=[]  
#post_tr_term()
add_cats()
for tr_file in os.listdir('files'):
    if ".csv" in tr_file and "Nid" not in tr_file:
        tract=Tractate(tr_file)
        tract.make_tractate_index()
        #tract.parse()
        #tract.tr_link()
        
        admin_links.append(SEFARIA_SERVER+"/admin/reset/Tosafot_HaRosh_on_"+tract.en_name.replace(u" ",u"_"))
        site_links.append(SEFARIA_SERVER+"/Tosafot_HaRosh_on_"+tract.en_name.replace(u" ",u"_"))
for link in admin_links:
    print link
print
print
for link in site_links:
    print link