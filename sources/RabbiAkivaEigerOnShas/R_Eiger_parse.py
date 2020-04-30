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
import re
import csv
from fuzzywuzzy import fuzz

talmud_titles = {}
for tractate_title in library.get_indexes_in_category("Talmud"):
    he_title = library.get_index(tractate_title).get_title("he")
    talmud_titles[he_title]=tractate_title
talmud_words=[u'גמרא',u'גמ\'',u'מתניתין',u'מתני\'',u'שם',u'בתר"י',u'בהרי"ף',u'ברי"ף',u'בר"ן']
tos_words=[u'תוס\' ד"ה',u'תוס\'',u'תוספות',u'תד"ה',u'בתד"ה',u'בתוס\' ד"ה']

def not_blank(s):
    while " " in s:
        s = s.replace(u" ",u"")
    return (len(s.replace(u"\n",u"").replace(u"\r",u"").replace(u"\t",u""))!=0);
def find_tractate_name(s):
    for tn in talmud_titles.keys():
        if tn in s:
            return talmud_titles[tn]
def clean_line(s):
    s=s.replace(u'\n',u'')
    return s
def make_talmud_array(book):
    tc = TextChunk(Ref(book), "he")
    return_array = []
    for x in range(len(tc.text)):
        return_array.append([])
    for index, perek in enumerate(return_array):
        tc2 = tc.text[index]
        for x in range(len(tc.text)):
            return_array[index].append([])
    return return_array
def dh_extract_method(some_string):
    for word in talmud_words:
        some_string=some_string.replace(word, u'')
    for word in tos_words:
        some_string=some_string.replace(word,u'')
    some_string=some_string.replace(u'גמרא ',u'').replace(u',',u'').replace(u'רש"י',u'')
    if u'@11' and u'@33' in some_string:
        if len(re.search(ur'(?<=@11).*?(?=@33)',some_string).group().split(u' '))>4:
            return re.search(ur'(?<=@11).*?(?=@33)',some_string).group()
    some_string=re.sub(ur'@\d+',u'',some_string)
    if u'וכו\'' in u' '.join(some_string.split(u' ')[:10]):
        return some_string[:some_string.index(u'וכו\'')-1]
    return ' '.join(some_string.split(u' ')[:8])
def tos_filter(s):
    s = re.sub(ur'^שם ',u'',s)
    for word in tos_words:
        if re.search(ur'^\S*'+word, s):
            return True
    return False
def tal_filter(s):
    print s
    for word in talmud_words:
        if re.search(ur'^\S*'+word, s):
            return True
    return False
def r_filter(s):
    s = re.sub(ur'^שם ',u'',s)
    if re.search(ur'^\S*ב?'+u'רש"י', s):
        return True
    else:
        return False
    
def remove_extra_space(string):
    while u"  " in string:
        string = string.replace(u"  ",u" ")
    return string
def base_tokenizer(some_string):
    return_s= filter(lambda(x): x!=u'',remove_extra_space(strip_nekud(some_string).replace(u"<b>",u"").replace(u"</b>",u"").replace(".","").replace(u"\n",u"")).split(u" "))
    if len(return_s)>0:
        return return_s
    return "EMPTY"
class Tractate:
    def __init__(self, tractate_name):
        self.he_tractate_name=tractate_name



text_dict={}
text_list=[]
tractate_list=[]


for rae_file in os.listdir('files'):
    if 'txt' in rae_file:    
        amud_box=[]
        with open('files/'+rae_file) as myFile:
            lines = list(map(lambda x: x.decode("utf-8",'replace'), myFile.readlines()))
        current_tractate=None
        current_daf=None
        current_amud=None
        skipping=False
        for line in lines:
            if 'START SKIPPING' in line:
                skipping=True
            if 'STOP SKIPPING' in line:
                skipping=False
            if not skipping:
                if u'@00' in line and len(line.split(u' '))<6:
                    if find_tractate_name(line):
                        if current_amud and len(amud_box)>0:
                            text_list.append([current_tractate, current_daf, current_amud, amud_box])
                            amud_box=[]
                        current_tractate=find_tractate_name(line)
                        if current_tractate not in tractate_list:
                            tractate_list.append(current_tractate)
                        current_daf=None
                        current_amud=None
                if u'@22' in line:
                    if current_amud and len(amud_box)>0 and (re.search(ur'(?<=דף )\S+',line) or u'ע"א' in line or u'ע"ב' in line):
                        text_list.append([current_tractate, current_daf, current_amud, amud_box])
                        amud_box=[]
                    if re.search(ur'(?<=דף )\S+',line):
                        current_daf=getGematria(re.search(ur'(?<=דף )\S+',line).group())
                        current_amud='a'
                    if u'ע"א' in line:
                        current_amud='a'
                    if u'ע"ב' in line:
                        current_amud='b'
                elif current_tractate and current_daf and not_blank(line):
                    if u'@11' in line or u'@00' in line or len(amud_box)<1:
                        amud_box.append(clean_line(line))
                    else:
                        amud_box[-1]+=u'<br>'+clean_line(line)
        text_list.append([current_tractate, current_daf, current_amud, amud_box])
        
for tractate in tractate_list:    
    myfile = open('output/RabbiEigerLinks_{}.tsv'.format(tractate),'w')
    myfile.write('Talmud Ref(unmatched)\tComment Text\tTalmud Ref(matched)\tRashi Ref\tTosafot Ref\n')
    myfile.close()
for set_of_comments in text_list:
    comment_link_list=[[] for x in range(len(set_of_comments[3]))]
    print 'matching TALMUD {}.{}{}...'.format(set_of_comments[0],set_of_comments[1],set_of_comments[2])
    tractate_ref=Ref('{}.{}{}'.format(set_of_comments[0],set_of_comments[1],set_of_comments[2]))
    tractate_chunk = TextChunk(tractate_ref,"he")
    if len(tractate_chunk.text)<1:
        match_set={'matches':[None for x in range(len(set_of_comments[3]))]}
    else:
        match_set = match_ref(tractate_chunk,set_of_comments[3],base_tokenizer,dh_extract_method=dh_extract_method,verbose=False)
    previous_link=None
    for index, (comment,base) in enumerate(zip(set_of_comments[3], match_set['matches'])):
        if tal_filter(comment) or (not tos_filter(comment) and not r_filter(comment) and index==0):
            if base:
                comment_link_list[index].append(base.normal())
                previous_link=base.normal()
            else:
                comment_link_list[index].append("X")
                previous_link=None
        elif not tos_filter(comment) and not r_filter(comment) and previous_link:
            comment_link_list[index].append(previous_link)
        else:
            comment_link_list[index].append("-")
            previous_link=None
    
    print 'matching RASHI {}.{}{}...'.format(set_of_comments[0],set_of_comments[1],set_of_comments[2])    
    rashi_ref=Ref('Rashi on {}.{}{}'.format(set_of_comments[0],set_of_comments[1],set_of_comments[2]))
    rashi_chunk = TextChunk(rashi_ref,"he")
    if len(rashi_chunk.text)<1:
        match_set={'matches':[None for x in range(len(set_of_comments[3]))]}
    else:
        match_set = match_ref(rashi_chunk,set_of_comments[3],base_tokenizer,dh_extract_method=dh_extract_method,verbose=False)
    for index, (comment,base) in enumerate(zip(set_of_comments[3], match_set['matches'])):
        if r_filter(comment):
            if base:
                comment_link_list[index].append(base.normal())
            else:
                comment_link_list[index].append("X")
                
        else:
            comment_link_list[index].append("-")
    
    print 'matching TOSAFOT {}.{}{}...'.format(set_of_comments[0],set_of_comments[1],set_of_comments[2])
    last_ref=False
    tos_ref=Ref('Tosafot on {}.{}{}'.format(set_of_comments[0],set_of_comments[1],set_of_comments[2]))
    tos_chunk = TextChunk(tos_ref,"he")
    if len(tos_chunk.text)<1:
        match_set={'matches':[None for x in range(len(set_of_comments[3]))]}
    else:
        match_set = match_ref(tos_chunk,set_of_comments[3],base_tokenizer,dh_extract_method=dh_extract_method,verbose=False)
    last_ref=False
    for index, (comment,base) in enumerate(zip(set_of_comments[3], match_set['matches'])):
        if tos_filter(comment):
            if base:
                comment_link_list[index].append(base.normal())
                last_ref=base.normal()
            else:
                comment_link_list[index].append("X")
        else:
            if re.search(ur'^\S*'+u'בא"ד',set_of_comments[3][index]) and last_ref:
                comment_link_list[index].append(last_ref)
            else:
                comment_link_list[index].append("X")
    #"""       
    with open('output/RabbiEigerLinks_{}.tsv'.format(set_of_comments[0]),'a') as myfile:        
        for comment, links in zip(set_of_comments[3], comment_link_list):
            print links
            myfile.write('{} {}{}\t{}\t{}\t{}\t{}\n'.format(set_of_comments[0],set_of_comments[1],set_of_comments[2],comment.encode('utf','replace'), links[0],links[1],links[2]))
    
    #"""
    #TALMUD, RASHI, TOSAFOT
    """
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
    """

        
"""
from beggining of vol iii:  
מקרא:
@00 כותרת
@01 כותרת משנה
@11 תחילת קטע
@22 דף
@33 טקסט רגיל אחרי תחילת קטע
@44 תחילת קטע אמצע
@55 טקסט רגיל אחרי תחילת קטע אמצע 
@66 מודגש
@77 סוף מודגש
@88 אות לפני תחילת קטע
@99 כותר סיום

    with open('output/RabbiEigerLinks_{}.tsv'.format(set_of_comments[0]),'a') as myfile:

           #print "COMMENT\/"
           #print comment 
           if base:
             myfile.write('{} {}{}\t{}\t{}\n'.format(set_of_comments[0],set_of_comments[1],set_of_comments[2],base,comment.encode('utf','replace')))
           else:
             myfile.write('{} {}{}\tNULL\t{}\n'.format(set_of_comments[0],set_of_comments[1],set_of_comments[2],comment.encode('utf','replace')))


@00חידושי רבי עקיבא אייגר 
"""