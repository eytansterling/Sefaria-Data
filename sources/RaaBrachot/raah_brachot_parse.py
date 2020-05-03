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

aleph_bet=u'א-ת'
def clean_string(s):
    s=s.replace(u'\n',u'')
    #s= re.sub(ur'[^ א-ת,a-zA-Z\.<>/\[\]\"\'\(\)!\-:;?=]',u'',s)
    #s=s.replace(u'\\uXXXX',u'').replace(u'\\',u'')
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
def get_raah_skeleton():
    raah_text=parse_raah(False)
    return_skel=[[] for x in range(len(raah_text))]
    for index, page in enumerate(raah_text):
        for comment in page:
            return_skel[index].append([])
    return return_skel
def extract_daf(s):
    return_dict={}
    return_dict['daf']=getGematria(s.split(u',')[0])
    return_dict['amud']='a' if u'א' in s.split(u',')[1] else 'b'
    return return_dict
def get_daf_en(num):

    if num % 2 == 1:
        num = num / 2 + 2
        return str(num)+"a"

    else:
        num = num / 2 + 1
        return str(num)+"b"
def fix_rif_line(s):
    return u'<small>['+s.replace(u'@11',u'').replace(u'\n',u'')+u']</small>'
def not_blank(s):
    while u" " in s:
        s = s.replace(u" ",u"")
    return (len(s.replace(u"\n",u"").replace(u"\r",u"").replace(u"\t",u""))!=0);
def make_tractate_index():
    record=SchemaNode()
    record.add_title("Ra'ah on Berakhot", 'en', primary=True)
    record.add_title(u'רא"ה על ברכות', 'he', primary=True)
    record.key = "Ra'ah on Berakhot"
    
    intro_node = JaggedArrayNode()
    intro_node.add_title("Introduction", 'en', primary = True)
    intro_node.add_title("הקדמה", 'he', primary = True)
    intro_node.key = "Introduction"
    intro_node.depth = 1
    intro_node.addressTypes = ['Integer']
    intro_node.sectionNames = ['Paragraph']
    record.append(intro_node)
    
    text_node = JaggedArrayNode()
    text_node.key = "default"
    text_node.default = True
    text_node.depth = 2
    text_node.addressTypes = ['Talmud', 'Integer']
    text_node.sectionNames = ['Daf','Comment']
    record.append(text_node)
    
    
    record.validate()

    index = {
        "title":"Ra'ah on Berakhot",
        "base_text_titles": [
           'Berakhot'
        ],
        "collective_title": "Ra'ah",
        "dependence": "Commentary",
        "categories":["Talmud","Bavli","Commentary"],
        "schema": record.serialize()
    }
    post_index(index,weak_network=True)
    
def parse_raah(posting=True):
    tractate_name='Berakhot'
    with open('raah_brachot_footnotes.txt') as myFile:
        lines = list(map(lambda x: x.decode("utf-8",'replace'), myFile.readlines()))
    footnotes=[]
    
    for line in lines:
        footnotes.append(re.sub(ur'^\s*\d+\s*',u'',line))
    
    
    
    with open('raah_brachot_text.txt') as myFile:
        lines = list(map(lambda x: x.decode("utf-8",'replace'), myFile.readlines()))
    mesechet_array = make_talmud_array(tractate_name)
    past_start=False
    
    #dict contains daf and amud
    current_daf_ref = {}
    #subtract 2 since we start at 0, add one since range's range in non-inclusive
    final_list = [[] for x in range(len(TextChunk(Ref(tractate_name),"he").text)-1)]
    add_to_next=[]
    test_string=''
    footnote_number=1
    for line in lines:
        if u'סליק פירקא' in line:
            footnote_number=1
        if u"@22" in line:
            current_daf_ref = extract_daf(line)
            past_start=True
        elif u'@11' in line:
            add_to_next.append(fix_rif_line(line))
        elif past_start:
            if not_blank(line):
                fn_line=line
                for match in re.findall(ur'\d+',fn_line):
                    fn_line=fn_line.replace(match, u'<sup>{}</sup><i class=\"footnote\">{}</i>'.format(footnote_number, footnotes.pop(0)) )       
                    #fn_line=fn_line.replace(match, u'<sup>{}</sup><i class=\"footnote\"></i>'.format(footnote_number))             
                    footnote_number+=1
                while len(add_to_next)>0:
                    fn_line=add_to_next.pop(0)+u'<br>'+fn_line
                test_string+=clean_string(fn_line)
                final_list[get_page(current_daf_ref["daf"],current_daf_ref["amud"])].append(clean_string(fn_line))
    #add blank to offset beggening:
    final_list.insert(0,[])
    theset=set(test_string)
    for thing in theset:
        print "\/"
        print repr(thing)
        print thing
    #0/0
    """
    for index, daf in enumerate(final_list):
        for cindex, comment in enumerate(daf):
            print index, cindex, comment
    """
    intro_box=lines[1:4]
    if posting:
        version = {
            'versionTitle': 'Perush ha-halachot masekhet berakhot, Jerusalem 2007',
            'versionSource': 'https://beta.nli.org.il/he/books/NNL_ALEPH005271357/NLI',
            'language': 'he',
            'text': final_list
        }
        if 'local' in SEFARIA_SERVER:
            post_text("Ra'ah on Berakhot", version,weak_network=True, skip_links=True, index_count="on")
        else:
            post_text_weak_connection('Ra\'ah on Berakhot', version)
        version = {
            'versionTitle': 'Perush ha-halachot masekhet berakhot, Jerusalem 2007',
            'versionSource': 'https://beta.nli.org.il/he/books/NNL_ALEPH005271357/NLI',
            'language': 'he',
            'text': intro_box
        }
        #post_text_weak_connection('Ra\'ah on Berakhot, Introduction', version)
    return final_list
def link_raah():
    tractate_name='Berakhot'
    raah_skeleton=get_raah_skeleton()
    for amud_index in range(1,len(TextChunk(Ref(tractate_name)).text)-1):
        tractate_chunk = TextChunk(Ref(tractate_name+"."+get_daf_en(amud_index)),"he")
        if amud_index>0:
            try:
                raah_chunk = TextChunk(Ref("Ra\'ah on Berakhot"+"."+get_daf_en(amud_index)),"he")
            except:
                print "ERRD"
                continue
            if len(raah_chunk.text)>0:
                matches = match_ref(tractate_chunk,raah_chunk,
                    base_tokenizer,dh_extract_method=dh_extract_method,verbose=False,char_threshold=0.4)
                if "comment_refs" in matches:
                    last_ref = Ref("Genesis").normal()
                    for comment_index, (base, comment) in enumerate(zip(matches["matches"],matches["comment_refs"])):
                        if base and u'small' not in TextChunk(comment,'he').text:
                            raah_skeleton[amud_index+1][comment_index].append(base.normal())


    for amud_index in range(1,len(TextChunk(Ref(tractate_name)).text)-1):        
        if amud_index>0:
            try:
                raah_chunk = TextChunk(Ref("Ra\'ah on Berakhot"+"."+get_daf_en(amud_index)),"he")
            except:
                print "ERRD"
                continue
            if len(raah_chunk.text)>0:
                for cindex, comment in enumerate(raah_chunk.text):
                    if u'<small>' in comment:
                        #print "SMAL"
                        rif_ref=re.search(ur"(?<=\"ף )\S+, ?\S+(?=])",comment).group().split(u',')
                        rif_daf=getGematria(rif_ref[0])
                        rif_amud='a' if u'א' in rif_ref[1] else 'b'
                        rif_chunck=TextChunk(Ref('Rif Berakhot.{}{}'.format(rif_daf,rif_amud)),'he')
                        matches = match_ref(rif_chunck,[comment],
                            base_tokenizer,dh_extract_method=dh_extract_method,verbose=False)
                        if matches['matches'][0]:
                            raah_skeleton[amud_index+1][cindex].append(matches['matches'][0].normal())
    match_list=[]
    for index, page in enumerate(raah_skeleton):
        new_page=True
        for cindex, link in enumerate(page):
            print get_daf_en(index), cindex, link
            if len(link)>0:
                match_list.append([link[0],index,cindex+1,cindex+1])
            elif not new_page:
                match_list[-1][3]==cindex+1
    for match in match_list:        
        link = (
                {
                "refs": [
                         match[0],
                         'Ra\'ah on Berakhot {}.{}-{}'.format(get_daf_en(match[1]-1), match[2], match[3]),
                         ],
                "type": "commentary",
                "auto": True,
                "generated_by": "sterling_raa_linker"
                })
        post_link(link, weak_network=True)
        

def raah_filter(s):
    return u'small' not in s
def remove_extra_space(s):
    while u"  " in s:
        s = s.replace("  "," ")
    return s
def dh_extract_method(some_string):
    if u'small' in some_string:
        some_string=re.sub(ur'.*<br>',u'',some_string)
    some_string = remove_extra_space(some_string)#.replace(u"<b>","").replace(u"</b>","")
    some_string=re.sub(ur'^\(\S{1,4}\)',u'',some_string)
    splits = {
        "pi_split":some_string.replace(u"<b>","").replace(u"</b>","").split(u' '+u"פי"+u"'"),
        "pirush_split": some_string.replace(u"<b>","").replace(u"</b>","").split(u"פירוש"),
        "period_split": some_string.replace(u"<b>","").replace(u"</b>","").split(u"."),
        "chulei_split": some_string.replace(u"<b>","").replace(u"</b>","").split(u"כו"+"'"),
        "b_split": some_string.replace(u"<b>","").split(u"</b>"+"'")
        }
    split_dh=get_smallest(splits)
    if len(split_dh.split(u" "))<10 and len(split_dh.split(u" "))>1:
        dh = split_dh
    else:
        dh=u' '.join(some_string.split(u" ")[0:4])
    return dh
    
def get_smallest(dic):
    return_dh = ""
    keyp = ""
    smallest_so_far = int
    for key in dic.keys():
        if len(dic[key][0])<smallest_so_far:
            smallest_so_far=len(dic[key][0])
            return_dh = dic[key][0]
            keyp=key
    return return_dh
def base_tokenizer(some_string):
    some_string = remove_extra_space(re.sub(ur'<.*?>',u'',some_string.replace(":","")))
    return filter(not_blank,some_string.split(" "))

def post_raa_term():
    term_obj = {
        "name": "Ra'ah",
        "scheme": "commentary_works",
        "titles": [
            {
                "lang": "en",
                "text": "Ra'ah",
                "primary": True
            },
            {
                "lang": "he",
                "text": u'רא"ה',
                "primary": True
            }
        ]
    }
    post_term(term_obj)
#post_raa_term()
#make_tractate_index()
parse_raah()
#link_raah()
