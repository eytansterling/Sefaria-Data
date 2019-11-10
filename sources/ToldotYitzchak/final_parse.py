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


en_sefer_names = ["Genesis","Exodus","Leviticus","Numbers","Deuteronomy"]
he_sefer_names = [u"בראשית",u"שמות",u"ויקרא",u"במדבר", u"דברים"]

def from_file_name_to_sefer(file_name):
    for sefer in en_sefer_names:
        if sefer in file_name:
            return sefer
            
def ty_post_index():
    record = SchemaNode()
    record.add_title('Toledot Yitzchak on Torah', 'en', primary=True, )
    record.add_title(u'תולדות יצחק על תורה', 'he', primary=True, )
    record.key = 'Toledot Yitzchak on Torah'
    
    intro_node = JaggedArrayNode()
    intro_node.add_title('Introduction', 'en', primary=True, )
    intro_node.add_title(u'הקדמה', 'he', primary=True, )
    intro_node.key = 'Introduction'
    intro_node.depth = 1
    intro_node.addressTypes = ['Integer']
    intro_node.sectionNames = ['Paragraph']
    record.append(intro_node)
    

    for en_sefer, he_sefer in zip(en_sefer_names, he_sefer_names):
        sefer_node = JaggedArrayNode()
        sefer_node.add_title(en_sefer, 'en', primary=True, )
        sefer_node.add_title(he_sefer, 'he', primary=True, )
        sefer_node.key = en_sefer
        sefer_node.depth = 3
        sefer_node.toc_zoom = 2
        sefer_node.addressTypes = ['Integer', 'Integer','Integer']
        sefer_node.sectionNames = ['Chapter','Verse','Comment']
        record.append(sefer_node)
    
    record.validate()

    index = {
        "title":"Toledot Yitzchak on Torah",
        "base_text_titles": [
           "Genesis","Exodus","Leviticus","Numbers","Deuteronomy"
        ],
        "dependence": "Commentary",
        "collective_title":"Toledot Yitzchak",
        "categories":['Tanakh','Commentary'],
        "schema": record.serialize()
    }
    post_index(index,weak_network=True)
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
def parse_text(posting=True):
    sefer_dict={}
    for ty_file in os.listdir('manual_fixed_files'):
        if '.tsv' in ty_file:
            sefer_name=from_file_name_to_sefer(ty_file)
            sefer_array=make_perek_array(sefer_name)
            with open('manual_fixed_files/'+ty_file) as tsvfile:
              reader = csv.reader(tsvfile, delimiter='\t')
              chapter=1
              verse=1
              for row in reader:

                  ref_pair=re.search(r'\d+:\d+',row[2]).group().split(':')
                  chapter=int(ref_pair[0])
                  verse=int(ref_pair[1])
                  sefer_array[chapter-1][verse-1].append(clean_line(row[1]))
            sefer_dict[sefer_name]=sefer_array
    if posting:
        for sefer_key in sefer_dict:
            version = {
                'versionTitle': 'Toledot Yitzchak, Warsaw 1877',
                'versionSource': 'http://beta.nli.org.il/he/books/NNL_ALEPH002063331/NLI',
                'language': 'he',
                'text': sefer_dict[sefer_key]
            }
            print "posting "+sefer_key+" text..."
            post_text_weak_connection('Toledot Yitzchak on Torah, '+sefer_key, version)
    return sefer_dict
def clean_line(s):
    s=s.replace('@11','<b>').replace('@33','</b>').replace('@44','<b>').replace('@55','</b>')
    return s.decode('utf','replace')
def make_links():
    textdict=parse_text(False)
    for sefer_key in textdict.keys():
        sefer_array = textdict[sefer_key]
        for perek_index,perek in enumerate(sefer_array):
            for pasuk_index, pasuk in enumerate(perek):
                for comment_index, comment in enumerate(pasuk):
                    link = (
                            {
                            "refs": [
                                     'Toledot Yitzchak on Torah, {}, {}:{}:{}'.format(sefer_key, perek_index+1, pasuk_index+1, comment_index+1),
                                     '{} {}:{}'.format(sefer_key,perek_index+1, pasuk_index+1),
                                     ],
                            "type": "commentary",
                            "auto": True,
                            "generated_by": "sterling_toledot_yitzchak_linker"
                            })
                    print link.get('refs')
                    post_link(link, weak_network=True)
#ty_post_index()
#parse_text()
make_links()
        
