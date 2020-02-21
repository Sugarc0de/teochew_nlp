import pandas as pd 
import sys 
import re
from hanziconv import HanziConv
from xpinyin import Pinyin

raw_data = '../data/raw_data/'

# initials and finals for pinyin
INITIALS = {'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j',
                'q', 'x', 'zh', 'ch', 'sh', 'r', 'z', 'c', 's', 'w', 'y'}

FINALS = {'in', 'ao', 've', 'en', 'ai', 'ei', 'ie', 'an', 'ong', 'ui', 'eng', 
          'e', 'ing', 'u', 'v', 'er', 'i', 'a', 'ang', 'un', 'o', 'iu', 'vn',
          'ia', 'ian', 'iang', 'iao', 'iong', 'ua', 'uai', 'uan', 'uang', 'uo', 'van'}



dialects_pd = pd.read_csv(raw_data+'output-dialects.txt')

teochew_pd = dialects_pd[dialects_pd.DOCULECT=='Chaozhou']

merged_pd = teochew_pd.copy()
merged_pd = merged_pd[['BENZI_IN_SOURCE','SEGMENTS','CHINESE']]
merged_pd = merged_pd.rename(columns={'BENZI_IN_SOURCE': 'BENZI_IN_SOURCE_teo', 
                                      'SEGMENTS': 'SEGMENTS_teo', 'CHINESE': 'CHINESE'})
merged_pd.head()


merged_pd.drop_duplicates(subset="BENZI_IN_SOURCE_teo", keep='first', inplace=True)

# removes extra characters and spaces from beizi_in_source 
merged_pd['BENZI_IN_SOURCE_teo'] = merged_pd['BENZI_IN_SOURCE_teo'].apply(lambda x: re.sub('[a-zA-Z0-9’!"#$%&\'() \
                                                                    *+,-./:;<=>?@，。?★、…【】□\
                                                                    《》？“”‘’！[\\]^_`{|}~\s]+', "", str(x)))
# removes rows that no chinese words can be found for teochew pronounciation
merged_pd = merged_pd.loc[merged_pd['BENZI_IN_SOURCE_teo']!=""]
merged_pd.head()


merged_pd['BENZI_man'] = merged_pd['BENZI_IN_SOURCE_teo'].apply(lambda x: HanziConv.toSimplified(x))
p = Pinyin()
merged_pd['pinyin'] = merged_pd['BENZI_man'].apply(lambda x: p.get_pinyin(x, tone_marks='numbers'))


# Separate Citation tones with Sandhi Tones for Teochew


SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

CONSONANTS = {'m', 'n', 'ŋ', 'pʰ', 'tʰ', 'kʰ', 'p', 't', 'k', 'g', 
              'b', 'tsʰ', 'ts', 's', 'z', 'dz', 'l', 'h', 'h̃'}

merged_pd['citation_teo'] = merged_pd['SEGMENTS_teo'].apply(lambda x: x.translate(SUP))

def get_teochew_parts(s, delimit=' '):
    s = s.translate(SUP)
    citation, initials, finals = [], [], [] 
    placeholder = "" 
    blocks = s.split(delimit)
    for idx, block in enumerate(blocks):
        if any(c.isdigit() for c in block):
            citation.append(block.split('/')[-1]) 
            finals.append(placeholder)
            placeholder = ""
        elif block in CONSONANTS and blocks[idx-1][-1].isdigit():
            initials.append(block)
        else:
            if blocks[idx-1][-1].isdigit():
                initials.append("")
            placeholder = placeholder + block
            
    return citation, initials, finals  

print(get_teochew_parts('s ɯ ŋ ⁵³/²¹³ p ũ ã ∼ ⁵⁵'))
merged_pd['citation_teo'], merged_pd['initial_teo'], merged_pd['final_teo'] = zip(*merged_pd['citation_teo'].apply(lambda x: get_teochew_parts(x)))


merged_pd.head()


# get_parts returns initials if n = 1, and returns finals if n = 2 
def get_parts(x):
    pinyin = x.split('-')
    initials = []
    finals = [] 
    for syllable in pinyin: 
        if syllable[0] + syllable[1] in INITIALS:
            initials.append(syllable[0]+syllable[1])
            finals.append(syllable[2:-1])  
            
        elif syllable[0] in INITIALS:
            initials.append(syllable[0])
            # convert u to v for special cases 
            if syllable[0] in ['j', 'q', 'x', 'y'] and syllable[1] == 'u':
                finals.append(syllable[1:-1].replace('u', 'v'))
            else:
                finals.append(syllable[1:-1])  
            
        else:
            initials.append("")
            finals.append(syllable[:-1])
    return initials, finals 
    
print(get_parts('a4-yun4-hui4-yi1-ge4-kuan1-kuo4-de5-jian1-bang3'))


def filter_non_pinyin(df):
    return df['pinyin'].replace(" ", "").isascii() 

merged_pd = merged_pd[merged_pd.apply(filter_non_pinyin, axis=1, reduce=True)]


merged_pd['citation_man'] = merged_pd['pinyin'].apply(lambda x: [t[-1] for t in x.split('-')])
merged_pd['initial_man'], merged_pd['final_man'] = zip(*merged_pd['pinyin'].apply(lambda x: get_parts(x))) 



merged_pd_copy = pd.DataFrame(merged_pd,columns=['BENZI_IN_SOURCE_teo','BENZI_man','citation_teo',
                                                 'initial_teo','final_teo', 
                                                 'citation_man','initial_man','final_man'])

merged_pd_copy = merged_pd_copy[merged_pd_copy.citation_teo.map(len)==merged_pd_copy.citation_man.map(len)]

pd1 = pd.DataFrame(merged_pd_copy['BENZI_IN_SOURCE_teo'].apply(lambda x: list(x)))
pd2 = pd.DataFrame(merged_pd_copy['BENZI_man'].apply(lambda x: list(x)))
pd3 = pd.DataFrame(merged_pd_copy['citation_teo'])
pd4 = pd.DataFrame(merged_pd_copy['initial_teo'])
pd5 = pd.DataFrame(merged_pd_copy['final_teo'])
pd6 = pd.DataFrame(merged_pd_copy['citation_man'])
pd7 = pd.DataFrame(merged_pd_copy['initial_man'])
pd8 = pd.DataFrame(merged_pd_copy['final_man'])

pd1 = pd1.explode('BENZI_IN_SOURCE_teo')
pd2 = pd2.explode('BENZI_man')
pd3 = pd3.explode('citation_teo')
pd4 = pd4.explode('initial_teo')
pd5 = pd5.explode('final_teo')
pd6 = pd6.explode('citation_man')
pd7 = pd7.explode('initial_man')
pd8 = pd8.explode('final_man')
combined_data = pd.concat([pd1, pd2, pd3, pd4, pd5, pd6, pd7, pd8], axis=1)
combined_data.drop_duplicates(subset="BENZI_IN_SOURCE_teo", keep='first', inplace=True)


combined_data.sample(10)


model_input = combined_data.to_csv('../data/clean_data/model_input.csv', index = None, header=True)