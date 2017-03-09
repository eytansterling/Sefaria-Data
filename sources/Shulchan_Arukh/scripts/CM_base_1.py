# encoding=utf-8


from sources.Shulchan_Arukh.ShulchanArukh import *
from data_utilities.util import he_ord



root = Root('../Choshen_Mishpat.xml')
base = root.get_base_text()
filename = u'../txt_files/Choshen_Mishpat/part_1/שולחן ערוך חושן משפט חלק א מחבר.txt'

base.remove_volume(1)
with codecs.open(filename, 'r', 'utf-8') as infile:
    volume = base.add_volume(infile.read(), 1)
assert isinstance(volume, Volume)

volume.mark_simanim(u'@22([\u05d0-\u05ea]{1,3})', start_mark=u'!start!', specials={u'@00': {'name': u'topic'}})
print 'Validating Simanim'
volume.validate_simanim()

volume.mark_seifim(u'@11([\u05d0-\u05ea]{1,3})', specials={u'@23': {'name': u'title'}})
print 'Validating Seifim'
volume.validate_seifim()
# root.export()

codes = [u'@68', u'@69', u'@70', u'@71', u'@62', u'@63', u'@64', u'@65', u'@67']
patterns = [ur'@68({})', ur'@69\[({})\]', ur'@70\(({})\)', ur'@71({})\)', ur'@62({})', ur'@63\[({})\]', ur'@64({})\]',
            ur'@65\(({})\)', ur'@67({})\)']
patterns = [i.format(ur'[\u05d0-\u05ea]{1,3}') for i in patterns]

for code, pattern in zip(codes, patterns):
    if code == u'@68':
        volume.validate_references(pattern, code, key_callback=he_ord)
    else:
        volume.validate_references(pattern, code)

errors = volume.format_text('@33', '@34', 'ramah')
for i in errors:
    print i
