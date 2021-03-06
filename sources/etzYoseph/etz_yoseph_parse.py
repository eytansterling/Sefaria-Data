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
he_sefer_names =  [u"בראשית",u"שמות" ,u"ויקרא",u"במדבר",u"דברים"]
midrash_names= ["Bereishit Rabbah","Shemot Rabbah","Vayikra Rabbah","Bemidbar Rabbah","Devarim Rabbah"]
def fix_line(s):
    s = re.sub(ur'.*>דה<',u'<b>',s)
    
    if u'>טק<' in s:
        if u'.' not in s[:s.index(u'>טק<')]:
            s = s[:s.index(u'>טק<')]+u'.</b> '+s[s.index(u'>טק<')+1:]
        else:
            s = s[:s.index(u'>טק<')]+u'</b>'+s[s.index(u'>טק<')+1:]
    else:
        print "OOOPS"
    s=s.replace(u'טק<',u'')
    
    news = re.sub(ur'>[א-ת]+?<',u' ',s)
    if len(news)<10:
        print "NO NEWS...",s,news
    s=news
    s = s.replace(u'<b>',u'STARTBOLD').replace(u'</b>',u'ENDBOLD')
    s = re.sub(ur'[<>]',u'',s)
    s = s.replace(u'STARTBOLD',u'<b>').replace(u'ENDBOLD',u'</b>')
    
    s = s.replace(u' .', u'.')
    s = remove_extra_spaces(s)
    
    return s+u':'
def post_ey_term():
    term_obj = {
        "name": "Etz Yosef",
        "scheme": "commentary_works",
        "titles": [
            {
                "lang": "en",
                "text": "Etz Yosef",
                "primary": True
            },
            {
                "lang": "he",
                "text": u'עץ יוסף',
                "primary": True
            }
        ]
    }
    post_term(term_obj)
def post_ey_index():
    # create index record
    record = SchemaNode()
    record.add_title('Etz Yosef on Midrash Rabbah', 'en', primary=True, )
    record.add_title(u'עץ יוסף על מדרש רבה', 'he', primary=True, )
    record.key = 'Etz Yosef on Midrash Rabbah'


    for en_sefer, he_sefer in zip(en_sefer_names, he_sefer_names):
        sefer_node = JaggedArrayNode()
        sefer_node.add_title(en_sefer, 'en', primary=True, )
        sefer_node.add_title(he_sefer, 'he', primary=True, )
        sefer_node.key = en_sefer
        sefer_node.depth = 2
        sefer_node.addressTypes = ['Integer', 'Integer']
        sefer_node.sectionNames = ['Chapter','Comment']
        record.append(sefer_node)

    record.validate()

    index = {
        "title":'Etz Yosef on Midrash Rabbah',
        "base_text_titles": [
           "Bereishit Rabbah","Shemot Rabbah","Vayikra Rabbah","Bemidbar Rabbah","Devarim Rabbah"
        ],
        "dependence": "Commentary",
        "categories":['Midrash','Commentary'],
        "schema": record.serialize()
    }
    post_index(index,weak_network=True)
        
def post_ey_text():
    for file in os.listdir("files"):
        if 'עץ' in file and '1' not in file:
            with open("files/"+file) as myFile:
                lines = list(map(lambda x: x.decode("utf-8",'replace'), myFile.readlines()))
            chapters=[]
            chapter_box=[]
            skip_count=0
            
            #to track filter....
            """
            f = open('etz_yoseph_skipped lines_{}.csv'.format(en_sefer_names[int(re.search(ur'[\d]',file).group())-1]),'w')
            f.close()
            """
            lines = re.split(u':',' '.join(lines).replace(u'\n',u''))
            for lindex, line in enumerate(lines):
                if u'פר<' in line and len(chapter_box)>0:
                    chapters.append(chapter_box)
                    chapter_box=[]
                if not_blank(fix_line(line).replace(u':',u'')):
                    chapter_box.append(fix_line(line))
            chapters.append(chapter_box)
            
            1/0
            for cindex, chapter, in enumerate(chapters):
                for pindex, paragraph in enumerate(chapter):
                    print cindex, pindex, paragraph
            
            version = {
                'versionTitle': 'Midrash Rabbah, with Etz Yosef, Warsaw, 1867',
                'versionSource': 'http://merhav.nli.org.il/primo-explore/fulldisplay?docid=NNL_ALEPH001987082&context=L&vid=NLI&search_scope=Local&tab=default_tab&lang=iw_IL',
                'language': 'he',
                'text': chapters
            }
            #print "Etz Yosef on Midrash Rabbah, {}".format(en_sefer_names[int(re.search(ur'[\d]',file).group())])
            #post_text_weak_connection("Etz Yosef on Midrash Rabbah, {}".format(en_sefer_names[int(re.search(ur'[\d]',file).group())-1]), version)
            post_text("Etz Yosef on Midrash Rabbah, {}".format(en_sefer_names[int(re.search(ur'[\d]',file).group())-1]),  version,weak_network=True, skip_links=True, index_count="on")
            
def make_links():
    matched=0.00
    total=0.00
    errored = []
    not_machted = []
    sample_Ref = Ref("Genesis 1")
    for sefer_index, sefer in enumerate(en_sefer_names):
        if "Gen" not in sefer and "Ex" not in sefer:
            if making_link_table:
                f = open('etz_yoseph_link_table_{}.csv'.format(sefer),'w')
                f.write('EY comment, EY current paragraph, Matched MR paragraph\n')
                f.close()
            with open('mismatched_paragraph_report_{}.txt'.format(en_sefer_names[sefer_index])) as myFile:
                lines = ''.join(myFile.readlines())
            mismatched_chapters = list(map(lambda(x):int(x),lines.replace('\n','').split()))
            
            for chapter in range(1,len(TextChunk(Ref(midrash_names[sefer_index]),'he').text)+1):
                if chapter in mismatched_chapters or not making_link_table:
                    last_not_matched = []

                    last_matched = Ref('{}, {} 1'.format(midrash_names[sefer_index],chapter))
                    base_chunk = TextChunk(Ref('{}, {}'.format(midrash_names[sefer_index],chapter)),"he")
                    com_chunk = TextChunk(Ref('Etz Yosef on Midrash Rabbah, {}:{}'.format(sefer, chapter)),"he")
                    ch_links = match_ref(base_chunk,com_chunk,base_tokenizer,dh_extract_method=dh_extract_method,rashi_filter=_filter)
                    print "KEYS:"
                    for key_thing in ch_links.keys():
                        print key_thing
                    print sefer
                    print "BASE ",len(base_chunk.text)
                    print "COM ",len(com_chunk.text)
                    #pdb.set_trace()
                    if 'comment_refs' not in ch_links:
                        print 'NONE for chapter ',chapter
                        continue
                    for link_index, (base, comment) in enumerate(zip(ch_links["matches"],ch_links["comment_refs"])):
                        if base:
                            while len(last_not_matched)>0:
                                print "we had ", last_matched.normal()
                                print "we have ", base.normal()
                                response_set=list(map(lambda(x): int(x),(last_matched.normal().split(':')[-1]+"-"+base.ending_ref().normal_last_section()).split('-')))
                                print "RESPONSE",response_set, "MAX", max(response_set), "MIN", min(response_set)
                                print "so, we'll do ",'{}-{}'.format(min(response_set),max(response_set))
                                first_link='{} {}{}-{}'.format(' '.join(last_matched.normal().split()[:-1]),re.search(ur'\d+:',last_matched.normal()).group(),min(response_set),max(response_set))
                                lnm = last_not_matched.pop(0).normal()
                                link = (
                                        {
                                        "refs": [
                                                 first_link,
                                                 lnm,
                                                 ],
                                        "type": "commentary",
                                        "auto": True,
                                        "generated_by": "sterling_"+key.replace(" ","_")+"_linker"
                                        })
                                if making_link_table:
                                    if "Etz" in lnm:
                                        etz=lnm
                                        mid=first_link
                                    else:
                                        etz=first_link
                                        mid=lnm
                                    with open('etz_yoseph_link_table_{}.csv'.format(sefer),'a') as fd:
                                        if Ref(mid).starting_ref()==Ref(mid).ending_ref():
                                            fd.write('{}, {}\n'.format(TextChunk(Ref(etz),'he').text.encode('utf','replace'), Ref(mid).normal()))
                                        else:
                                            fd.write('{}, \n'.format(TextChunk(Ref(etz),'he').text.encode('utf','replace')))
                                else:
                                    post_link(link, weak_network=True)
                                matched+=1
                            print "B",base,"C", comment
                            if base:
                                link = (
                                        {
                                        "refs": [
                                                 base.normal(),
                                                 comment.normal(),
                                                 ],
                                        "type": "commentary",
                                        "auto": True,
                                        "generated_by": "sterling_"+key.replace(" ","_")+"_linker"
                                        })
                                if making_link_table:
                                    if "Etz" in base.normal():
                                        etz=base.normal()
                                        mid=comment.normal()
                                    else:
                                        etz=comment.normal()
                                        mid=base.normal()
                                    with open('etz_yoseph_link_table_{}.csv'.format(sefer),'a') as fd:
                                        fd.write('{}, {}\n'.format(TextChunk(Ref(etz),'he').text.encode('utf','replace'), mid))
                                else:
                                    post_link(link, weak_network=True)    
                                matched+=1
            

                
                                last_matched=base
               
                        else:
                            #not_machted.append('{}, {} Introduction'.format(key, section["en_title"]))
                            last_not_matched.append(comment.starting_ref())
                            if link_index==len(ch_links["matches"])-1:
                                print "NO LINKS LEFT!"
                                print "we had ", last_matched.normal()
                                print "so, we'll do ",last_matched.normal()+"-"+str(len(base_chunk.text))
                                while len(last_not_matched)>0:
                                    lnm=last_not_matched.pop(0).normal()
                                    first_link=last_matched.normal()+"-"+str(len(base_chunk.text))
                                    link = (
                                            {
                                            "refs": [
                                                     first_link,
                                                     lnm,
                                                     ],
                                            "type": "commentary",
                                            "auto": True,
                                            "generated_by": "sterling_"+key.replace(" ","_")+"_linker"
                                            })
                                    if making_link_table:
                                        if "Etz" in lnm:
                                            etz=lnm
                                            mid=first_link
                                        else:
                                            etz=first_link
                                            mid=lnm
                                        with open('etz_yoseph_link_table_{}.csv'.format(sefer),'a') as fd:
                                            if Ref(mid).starting_ref()==Ref(mid).ending_ref():
                                                fd.write('{}, {}\n'.format(TextChunk(Ref(etz),'he').text.encode('utf','replace'), Ref(mid).normal()))
                                            else:
                                                fd.write('{}, \n'.format(TextChunk(Ref(etz),'he').text.encode('utf','replace')))
                                                
                                    else:
                                        post_link(link, weak_network=True)
                                    matched+=1

    """       
    pm = matched/total
    print "Result is:",matched,total
    print "Percent matched: "+str(pm)
    print "Not Matched:"
    for nm in not_machted:
        print nm
    """
#here starts methods for linking:
def _filter(some_string):
    if re.search(ur'<b>(.*?)</b>', some_string) is None:
        return False
    else:
        return True

def dh_extract_method(some_string):
    #print "DH!:",some_string
    return re.search(ur'<b>(.*?)</b>', some_string).group(1)

def base_tokenizer(some_string):
    return filter(lambda(x): x!=u'',remove_extra_spaces(some_string.replace(u"<b>",u"").replace(u"</b>",u"").replace(u".",u"")).split(" "))
def remove_extra_spaces(string):
    string = re.sub(ur"\. $",u".",string)
    while u"  " in string:
        string=string.replace(u"  ",u" ")
    return string
def not_blank(s):
    while u" " in s:
        s = s.replace(u" ",u"")
    return (len(s.replace(u"\n",u"").replace(u"\r",u"").replace(u"\t",u""))!=0);
def generate_paragraph_report():
    for file in os.listdir("files"):
        if 'עץ' in file and '1' not in file:# and '1' not in file:
            with open("files/"+file) as myFile:
                lines = list(map(lambda x: x.decode("utf-8",'replace'), myFile.readlines()))
            chapters=[]
            chapter_box=[]
            chapters = re.split(u'פר<',' '.join(lines).replace(u'\n',u''))[1:]
            chapter_paragrah_counts=[]
            for chapter in chapters:
                chapter_paragrah_counts.append(chapter.count(u'>צי<'))
            """
            for lindex, line in enumerate(lines):
                if u'פר<' in line and len(chapter_box)>0:
                    chapters.append(chapter_box)
                    chapter_box=[]
                if not_blank(fix_line(line).replace(u':',u'')):
                    chapter_box.append(line)
            chapters.append(chapter_box)
            
            chapter_paragrah_counts=[]
            for chapter in chapters:
                chapter_paragrah_counts.append(0)
                print "appended ", chapters.index(chapter)+1
                for paragraph in chapter:
                    chapter_paragrah_counts[-1]+=paragraph.count(u'ח<')
            """
            f = open('etz_yoseph_chapter_paragraph_report_{}.csv'.format(en_sefer_names[int(re.search(ur'[\d]',file).group())-1]),'w')
            f2 = open('mismatched_paragraph_report_{}.txt'.format(en_sefer_names[int(re.search(ur'[\d]',file).group())-1]),'w')
            f.write('Chapter, Etz Yoseph Paragraphs, Midrash Rabba Paragraphs\n')
            for chapter in range(1,len(TextChunk(Ref(midrash_names[int(re.search(ur'[\d]',file).group())-1]),'he').text)+1):
                midrash_length = len(TextChunk(Ref('{}, {}'.format(midrash_names[int(re.search(ur'[\d]',file).group())-1],chapter)),"he").text)
                print chapter, en_sefer_names[int(re.search(ur'[\d]',file).group())-1]
                if len(chapter_paragrah_counts)>=chapter:
                    etz_length = chapter_paragrah_counts[chapter-1]
                else:
                    etz_length='NA'
                #etz_length = len(TextChunk(Ref('Etz Yosef on Midrash Rabbah, {}:{}'.format(sefer, chapter)),"he").text)
                if etz_length!=midrash_length:
                    f2.write("{} ".format(chapter))
                    f.write("*{}, {}, {}\n".format(chapter, etz_length, midrash_length))
                    
                else:
                    f.write("{}, {}, {}\n".format(chapter, etz_length, midrash_length))
                    
            f.close()
            f2.close()
            
making_link_table=True
#generate_paragraph_report()
#post_ey_term()
#post_ey_index()
#post_ey_text()

make_links()
#re.split(ur'<פרשה \S+>'
#exceptions: 1 4?, 1 74, 4 13