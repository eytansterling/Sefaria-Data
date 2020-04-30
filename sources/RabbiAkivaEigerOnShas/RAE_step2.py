# -*- coding: utf-8 -*-
import os
import re
import sys
import csv
p = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, p)
from sources.local_settings import *
sys.path.insert(0, SEFARIA_PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = "sefaria.settings"
import django
django.setup()
from sources.functions import *
import codecs
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from data_utilities.dibur_hamatchil_matcher import *
import pdb

tractate_titles = {}
for tractate_title in library.get_indexes_in_category("Bavli"):
    he_title = library.get_index(tractate_title).get_title("he")
    tractate_titles[he_title]=tractate_title
def from_en_name_to_he_name(name):
    for key in tractate_titles.keys():
        if tractate_titles[key]==name:
            return key
def clean_line(s):
    if u'@11' in s and u'@33' in s:
        s=s.replace(u'@11',u'<b>').replace(u'@33',u'</b>')
    if u'@44' in s and u'@55' in s:
        s=s.replace(u'@44',u'<b>').replace(u'@55',u'</b>')
        
    s=re.sub(ur'@\d+',u'',s)
    return s
def ref_to_num(daf, amud):
    if u'a' in amud:
        return daf*2-2
    if u'b' in amud:
        return daf*2-1
def clean_string(s):
    if isinstance(s,str):
        return re.sub(r'[^ א-ת,a-zA-Z\.<>/\[\]\"\'\(\)!\-:;?=]','',s).replace('\xa0', ' ').replace(u'\\',u'')
    else:
        return re.sub(ur'[^ א-ת,a-zA-Z\.<>/\[\]\"\'\(\)!\-:;?=]',u'',s).replace(u'\xa0', u' ').replace(u'\\',u'')
class rae_Tractate:
    def __init__(self, file_name):
        self.file_name = file_name
        self.en_tractate_name=clean_string(re.search(ur'(?<=inks_).*?(?=\.tsv)',file_name).group())
        self.he_tractate_name=from_en_name_to_he_name(self.en_tractate_name)
        self.parse_tractate()

    def make_tractate_index(self):
        en_title = self.en_tractate_name
        he_title = self.he_tractate_name
        record = JaggedArrayNode()
        record.add_title(u'Chidushei Rabbi Akiva Eiger on '+en_title, 'en', primary=True)
        record.add_title(u'חידושי רבי עקיבא איגר על מסכת '+he_title, 'he', primary=True)
        record.key = 'Chidushei Rabbi Akiva Eiger on '+en_title
        record.depth = 2
        record.addressTypes = ['Talmud', 'Integer']
        record.sectionNames = ['Daf','Comment']
        record.validate()

        index = {
            "title":'Chidushei Rabbi Akiva Eiger on '+en_title,
            "base_text_titles": [
               en_title
            ],
            "collective_title":"Chidushei Rabbi Akiva Eiger",
            "dependence": "Commentary",
            "categories":["Talmud","Bavli","Commentary","Chidushei Rabbi Akiva Eiger", get_mishnah_seder(en_title)],
            "schema": record.serialize()
        }

        post_index(index,weak_network=True)
        
    
    def parse_tractate(self):
        print 'parsing {}...'.format(self.en_tractate_name)
        #super_string=u''
        with open('output/'+self.file_name) as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            final_list = make_talmud_array(self.en_tractate_name)
            link_list = make_talmud_array(self.en_tractate_name)
            current_daf_ref={}
            for row in reader:
                if 'Talm' not in row[0]:
                    daf_row=row[0].decode('utf','replace').split(u' ')[-1]
                    text_row=row[1].decode('utf','replace')
                    current_daf_ref=extract_daf(daf_row)
                    if not_blank(text_row):
                        final_list[ref_to_num(current_daf_ref["daf"],current_daf_ref["amud"])].append(clean_line(text_row))
                        #super_string+=clean_line(text_row)
                        if len(row[2])>3:
                            link_list[ref_to_num(current_daf_ref["daf"],current_daf_ref["amud"])].append(row[2])
                        elif len(row[3])>3:
                            link_list[ref_to_num(current_daf_ref["daf"],current_daf_ref["amud"])].append(row[3])
                        elif len(row[4])>3:
                            link_list[ref_to_num(current_daf_ref["daf"],current_daf_ref["amud"])].append(row[4])
                        else:
                            link_list[ref_to_num(current_daf_ref["daf"],current_daf_ref["amud"])].append(None)
        """        
        for thing in set(super_string):
            print thing
            print repr(thing)
            print '___________________________________'
        """
        self.text = final_list
        self.links= link_list
    def rae_post_text(self):
        version = {
            'versionTitle': 'Chiddushei Rabbi Akiva Eiger, Warsaw 1892',
            'versionSource': 'https://www.nli.org.il/he/books/NNL_ALEPH001167585/NLI',
            'language': 'he',
            'text': self.text
        }
        post_text_weak_connection('Chidushei Rabbi Akiva Eiger on '+self.en_tractate_name, version)
        #post_text('Rabbi Akiva Eiger on '+self.en_tractate_name, version,weak_network=True)
    def print_tract(self):
        for dindex, daf in enumerate(self.text):
            for cindex, comment in enumerate(daf):
                print self.en_name, num_to_daf(dindex),cindex,comment
    def rae_link(self):
        for index, page in enumerate(self.links):
            for lindex, reference in enumerate(page):
                if reference:
                    print "REF: {}".format(reference)
                    link = (
                            {
                            "refs": [
                                     reference,
                                     'Chidushei Rabbi Akiva Eiger on {}, {}:{}'.format(self.en_tractate_name, num_to_daf(index), lindex+1),
                                     ],
                            "type": "commentary",
                            "auto": True,
                            "generated_by": "sterling_Chidushei_Rabbi_Akiva_Eiger_linker"
                            })
                    print "posting {}...".format(reference)
                    post_link(link, weak_network=True)
                    if u"Rashi" in reference:
                        print 'Rashi, MINE: {} {}'.format(self.en_tractate_name, num_to_daf(index))
                        got_link=False
                        for e in Ref(reference).linkset().contents():
                            print 'expanded...',e['expandedRefs0'][0]
                            print
                            if 'Rashi' in e['expandedRefs1'][0] and '{} {}'.format(self.en_tractate_name, num_to_daf(index)) in e['expandedRefs0'][0]:
                                link = (
                                    {
                                    "refs": [
                                             e['expandedRefs0'][0],
                                             'Chidushei Rabbi Akiva Eiger on {}, {}:{}'.format(self.en_tractate_name, num_to_daf(index), lindex+1),
                                             ],
                                    "type": "commentary",
                                    "auto": True,
                                    "generated_by": "sterling_Chidushei_Rabbi_Akiva_Eiger_linker"
                                    })
                                print "posting expanded {}...".format(e['expandedRefs0'])
                                post_link(link, weak_network=True)
                                got_link=True
                        if not got_link:
                            0/0
                            
                    if u"Tosafot" in reference:
                        print 'tos, MINE: {} {}'.format(self.en_tractate_name, num_to_daf(index))
                        got_link=False
                        for e in Ref(reference).linkset().contents():
                            print e['expandedRefs0'][0]
                            print
                            if u'Tosafot' in e['expandedRefs1'][0] and '{} {}'.format(self.en_tractate_name, num_to_daf(index)) in e['expandedRefs0'][0]:
                                link = (
                                    {
                                    "refs": [
                                             e['expandedRefs0'][0],
                                             'Chidushei Rabbi Akiva Eiger on {}, {}:{}'.format(self.en_tractate_name, num_to_daf(index), lindex+1),
                                             ],
                                    "type": "commentary",
                                    "auto": True,
                                    "generated_by": "sterling_Chidushei_Rabbi_Akiva_Eiger_linker"
                                    })
                                print "posting expanded {}...".format(e['expandedRefs0'])
                                post_link(link, weak_network=True)
                                got_link=True
                            
                        if not got_link:
                            0/0
def make_talmud_array(book):
    tc = TextChunk(Ref(book), "he")
    return_array = []
    for x in range(len(tc.text)):
        return_array.append([])
    return return_array
def extract_daf(s):
    return_dict = {}
    return_dict["daf"]= int(re.search(ur'\d+',s).group())    
    return_dict["amud"]= "a" if u"a" in s else "b"
    return return_dict
def get_daf_en(num):

    if num % 2 == 1:
        num = num / 2 + 2
        return str(num)+"a"

    else:
        num = num / 2 + 1
        return str(num)+"b"
def not_blank(s):
    while " " in s:
        s = s.replace(u" ",u"")
    return (len(s.replace(u"\n",u"").replace(u"\r",u"").replace(u"\t",u""))!=0);
def remove_markers(s):
    s = re.sub(ur"<\d+>\S{1,4}\)<\d+>",u"",s)
    s = re.sub(ur"<\d+>",u"",s)
    s = re.sub(ur"\*+\)",u"",s)
    return s
def get_hebrew_name(title):
    return highest_fuzz(tractate_titles.keys(), title)
def dh_extract_method(some_string):
    some_string=re.sub(ur'<.*?>',u'',some_string)
    first_sentence= remove_extra_space(re.split(ur"[\.:]",some_string)[0])
    if len(first_sentence.split())>8:
        return ' '.join(some_string.split()[:8])
    return first_sentence
def remove_extra_space(string):
    while u"  " in string:
        string = string.replace(u"  ",u" ")
    return string
def base_tokenizer(some_string):
    return filter(lambda(x): x!=u'',remove_extra_space(strip_nekud(some_string).replace(u"<b>",u"").replace(u"</b>",u"").replace(".","").replace(u"\n",u"")).split(u" "))
#bad experiences with fuzzy wuzzy's .process and unicode...
def highest_fuzz(input_list, input_item):
    highest_ratio = 0
    best_match = u''
    for item in input_list:
        if fuzz.ratio(input_item,item)>highest_ratio:
            best_match=item
            highest_ratio=fuzz.ratio(input_item,item)
    return best_match
seders = {'Seder Zeraim':u'סדר זרעים','Seder Moed':u'סדר מועד','Seder Nashim':u'סדר נשים','Seder Nezikin':u'סדר נזיקין','Seder Kodashim':u'סדר קדשים','Seder Tahorot':u'סדר טהרות'}
def post_talmud_categories():
    add_category('Chidushei Rabbi Akiva Eiger', ["Talmud","Bavli","Commentary",'Chidushei Rabbi Akiva Eiger'], u'חידושי רבי עקיבא איגר')
    for seder in seders.keys():
        add_category(seder, ["Talmud","Bavli","Commentary",'Chidushei Rabbi Akiva Eiger',seder], seders[seder])
def get_mishnah_seder(mishnah_title):
    if u"Mishnah" not in mishnah_title:
        mishnah_title="Mishnah "+mishnah_title
    for seder in seders.keys():
        indices = library.get_indexes_in_category(seder)
        if mishnah_title in indices:
            return seder
    return None
posting_cats = False
posting_index = False
posting_text = False
linking = False

def num_to_daf(num):
    stam_daf=num/2+1
    amud='a' if num%2==0 else 'b'
    return str(stam_daf)+amud
def post_rae_term():
    term_obj = {
        "name": "Chidushei Rabbi Akiva Eiger",
        "scheme": "commentary_works",
        "titles": [
            {
                "lang": "en",
                "text": "Chidushei Rabbi Akiva Eiger",
                "primary": True
            },
            {
                "lang": "he",
                "text": u'חידושי רבי עקיבא איגר',
                "primary": True
            }
        ]
    }
    post_term(term_obj)
if posting_cats:
    post_talmud_categories()
#post_rae_term()
admin_links = []
site_links = []
parsing=True
for rae_file in os.listdir("output"):
    if ".tsv" in rae_file:
        current_tractate = rae_Tractate(rae_file)
        admin_links.append(SEFARIA_SERVER+"/admin/reset/Chidushei_Rabbi_Akiva_Eiger_on_"+current_tractate.en_tractate_name.replace(u" ",u"_"))
        site_links.append(SEFARIA_SERVER+"/Chidushei_Rabbi_Akiva_Eiger_on_"+current_tractate.en_tractate_name.replace(u" ",u"_"))
        if "Shabb" in current_tractate.en_tractate_name:
            parsing=True
        parsing=False
        if parsing:# and "Batra" in current_tractate.en_tractate_name:
            if posting_index:
                print "posting ",current_tractate.en_tractate_name," index..."
                current_tractate.make_tractate_index()
            if posting_text:
                print "posting ",current_tractate.en_tractate_name," text..."
                current_tractate.rae_post_text()
            if linking:
                print "linking",current_tractate.en_tractate_name,"..."
                current_tractate.rae_link()

        """
        for dindex, daf in enumerate(current_tractate.text):
            for cindex, comment in enumerate(daf):
                print dindex, cindex, comment
        """    
print "Admin Links:"
for link in admin_links:
    print link
print "Site Links:"
for link in site_links:
    print link
