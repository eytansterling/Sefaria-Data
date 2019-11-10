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

name_dict={u'רות':'Ruth', u'איכה':'Lamentations', u'שיר השירים':'Song of Songs', u'קהלת':'Ecclesiastes'}

class megilah:
    def __init__(self, file_name):
        self.file_name = 'megilot/{}'.format(file_name)
        #print file_name
        for key in name_dict.keys():
            #print key
            if key in file_name.decode('utf8','replace'):
                #print "IT"
                self.he_name=key
                self.en_name=name_dict[key]
    def post_ms_index(self):
        record = JaggedArrayNode()
        record.add_title("Minchat Shai on "+self.en_name, 'en', primary=True)
        record.add_title(u'מנחת שי על'+' '+self.he_name, 'he', primary=True)
        record.key = "Minchat Shai on "+self.en_name
        record.depth = 3
        record.toc_zoom = 2
        record.addressTypes = ["Integer", "Integer","Integer"]
        record.sectionNames = ["Chapter", "Verse", "Comment"]
    
        record.validate()
        print "posting {} index..".format(self.en_name)
        index = {
            "title":"Minchat Shai on "+self.en_name,
            "base_text_titles": [
              self.en_name
            ],
            "dependence": "Commentary",
            "collective_title":"Minchat Shai",
            "categories":["Tanakh","Commentary","Minchat Shai","Writings"],
            "schema": record.serialize()
        }
        post_index(index,weak_network=True)
    def post_ms_text(self, posting=True):
        with open(self.file_name) as myfile:
            lines = list(map(lambda(x): x.decode('utf','replace'), myfile.readlines()))
        text_array = make_perek_array(self.en_name)
        current_chapter=1
        current_verse=1
        for line in lines:
            if u'@' in line:
                current_chapter=getGematria(line)
            elif u'#' in line:
                current_verse=getGematria(line)
            elif not_blank(line):
                try:
                    for piece in line.split(u": "):
                        text_array[current_chapter-1][current_verse-1].append(clean_line(piece))
                except:
                    print "ERR",self.en_name
                    print line
                    0/0
        self.text=text_array
        version = {
            'versionTitle': "Arba'ah Ve'Esrim im Minhat Shai. Mantua, 1742-1744",
            'versionSource': 'http://primo.nli.org.il/primo-explore/fulldisplay?vid=NLI&docid=NNL_ALEPH002093602&context=L',
            'language': 'he',
            'text': text_array
        }
        if posting:
            print "postinh {} text...".format(self.en_name)
            post_text_weak_connection("Minchat Shai on "+self.en_name, version)
    def ms_link(self):
        self.post_ms_text(False)
        for perek_index,perek in enumerate(self.text):
            for pasuk_index, pasuk in enumerate(perek):
                for comment_index, comment in enumerate(pasuk):
                    link = (
                            {
                            "refs": [
                                     'Minchat Shai on {}, {}:{}:{}'.format(self.en_name, perek_index+1, pasuk_index+1, comment_index+1),
                                     '{} {}:{}'.format(self.en_name,perek_index+1, pasuk_index+1),
                                     ],
                            "type": "commentary",
                            "auto": True,
                            "generated_by": "sterling_Minchat_Shai_linker"
                            })
                    post_link(link, weak_network=True)
def not_blank(s):
    while " " in s:
        s = s.replace(u" ",u"")
    return (len(s.replace(u"\n",u"").replace(u"\r",u"").replace(u"\t",u""))!=0);
def clean_line(s):
    if s.count(u'.')+s.count(u':')>1:
        s =u'<b>'+s[:s.index(u'.')+1]+u'</b>'+s[s.index('.')+1:]
    if s[-1]!=u'.' and s[-1]!=u':':
        s=s+u':'
    return s
def make_perek_array(book):
    tc = TextChunk(Ref(book), "he")
    return_array = []
    for x in range(len(tc.text)):
        return_array.append([])
    for index, perek in enumerate(return_array):
        tc = TextChunk(Ref(book+" "+str(index+1)), "he")
        for x in range(len(tc.text)):
            return_array[index].append([])
    return return_array

admin_links=[]
site_links=[]
for _file in os.listdir("megilot"):
    if 'txt' in _file:# and "איכ" not in _file:
        meg = megilah(_file)
        admin_links.append(SEFARIA_SERVER+"/admin/reset/Minchat Shai on "+meg.en_name)
        site_links.append(SEFARIA_SERVER+"/Minchat Shai on "+meg.en_name)
        #meg.post_ms_index()
        meg.post_ms_text()
        meg.ms_link()
for link in admin_links:
    print link
print
for link in site_links:
    print link
        