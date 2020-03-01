import pandas as pd
import re

# CONSTANTS
raw_input = '../data/raw_data/output-dialects.csv'
clean_data = '../data/clean_data/'
src_lan = 'Guangzhou'
dst_lan = 'Chaozhou'

# mapping
#
# initials and finals for pinyin
MANDARIN_INITIALS = {'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j',
            'q', 'x', 'zh', 'ch', 'sh', 'r', 'z', 'c', 's', 'w', 'y'}

MANDARIN_FINALS = {'in', 'ao', 've', 'en', 'ai', 'ei', 'ie', 'an', 'ong', 'ui', 'eng',
          'e', 'ing', 'u', 'v', 'er', 'i', 'a', 'ang', 'un', 'o', 'iu', 'vn',
          'ia', 'ian', 'iang', 'iao', 'iong', 'ua', 'uai', 'uan', 'uang', 'uo', 'van'}

CANTON_INITIALS = {'b', 'p', 'm', 'f', 'd', 't', 'n',
                   'l', 'g', 'k', 'ng', 'h', 'gw', 'kw',
                   'w', 'z', 'c', 's', 'j'}

teo_tone_mapping = {'33':'mid', '11':'low', '21':'low_checked',
                       '213':'low_rising', '35':'high_rising',
                       '4':'high_checked', '53':'falling', '55':'high'}

man_tone_mapping = {'1': 'high', '2': 'rising', '3': 'dipping', '4': 'falling'}

can_tone_mapping = {'1': 'dark_flat', '2': 'dark_rising', '3': 'dark_departing',
                    '4': 'light_flat', '5': 'light_rising', '6': 'light_departing'}

SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

CONSONANTS = {'m', 'n', 'ŋ', 'pʰ', 'tʰ', 'kʰ', 'p', 't', 'k', 'g',
              'b', 'tsʰ', 'ts', 's', 'z', 'dz', 'l', 'h', 'h̃'}
######################################################################################

# Teochew (dst) and Mandarin combination
def get_dst_only(raw_input):
    dialects_pd = pd.read_csv(raw_input)

    # get all teochew data
    dst_pd = dialects_pd[dialects_pd.DOCULECT == dst_lan]

    merged_pd = dst_pd.copy()
    merged_pd = merged_pd[['BENZI_IN_SOURCE', 'SEGMENTS', 'CHINESE']]
    merged_pd = merged_pd.rename(columns={'BENZI_IN_SOURCE': 'BENZI_IN_SOURCE_teo',
                                          'SEGMENTS': 'SEGMENTS_teo', 'CHINESE': 'CHINESE'})

    merged_pd.drop_duplicates(subset="BENZI_IN_SOURCE_teo", keep='first', inplace=True)

    # removes extra characters and spaces from beizi_in_source
    merged_pd['BENZI_IN_SOURCE_teo'] = merged_pd['BENZI_IN_SOURCE_teo'].apply(lambda x: re.sub('[a-zA-Z0-9’!"#$%&\'() \
                                                                        *+,-./:;<=>?@，。?★、…【】□\
                                                                        《》？“”‘’！[\\]^_`{|}~\s]+', "", str(x)))
    # removes rows that no chinese words can be found for dst pronounciation
    merged_pd = merged_pd.loc[merged_pd['BENZI_IN_SOURCE_teo'] != ""]
    return merged_pd


# Teochew (dst) and Cantonese (src) combination
def get_src_dst(raw_input):
    dialects_pd = pd.read_csv(raw_input)

    # get all teochew data
    dst_pd = dialects_pd[dialects_pd.DOCULECT == dst_lan]
    src_pd = dialects_pd[dialects_pd.DOCULECT == src_lan]

    merged_pd = dst_pd.copy()
    merged_pd = merged_pd[['BENZI_IN_SOURCE', 'SEGMENTS', 'CHINESE']]
    merged_pd = merged_pd.rename(columns={'BENZI_IN_SOURCE': 'BENZI_IN_SOURCE_teo',
                                          'SEGMENTS': 'SEGMENTS_teo', 'CHINESE': 'CHINESE'})

    merged_pd.drop_duplicates(subset="BENZI_IN_SOURCE_teo", keep='first', inplace=True)

    # removes extra characters and spaces from beizi_in_source
    merged_pd['BENZI_IN_SOURCE_teo'] = merged_pd['BENZI_IN_SOURCE_teo'].apply(lambda x: re.sub('[a-zA-Z0-9’!"#$%&\'() \
                                                                            *+,-./:;<=>?@，。?★、…【】□\
                                                                            《》？“”‘’！[\\]^_`{|}~\s]+', "", str(x)))
    # removes rows that no chinese words can be found for dst pronounciation
    merged_pd = merged_pd.loc[merged_pd['BENZI_IN_SOURCE_teo'] != ""]
    return merged_pd


# get_pinyin_parts returns initials if n = 1, and returns finals if n = 2
def get_pinyin_parts(x):
    pinyin = x.split('-')
    initials = []
    finals = []
    for syllable in pinyin:
        if syllable[0] + syllable[1] in MANDARIN_INITIALS:
            initials.append(syllable[0] + syllable[1])
            finals.append(syllable[2:-1])

        elif syllable[0] in MANDARIN_INITIALS:
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


def filter_non_pinyin(df):
    return df['pinyin'].replace(" ", "").isascii()

def filter_non_jyutping(df):
    return df['jyutping'].replace(" ", "").isascii()

# This function adds pinyin, breaks down initials, finals, citation for mandarin,
# and return a dataframe that is ready to perform pandas.explode
def process_mandarin(df):
    from hanziconv import HanziConv
    from xpinyin import Pinyin

    df['BENZI_man'] = df['BENZI_IN_SOURCE_teo'].apply(lambda x: HanziConv.toSimplified(x))
    p = Pinyin()
    df['pinyin'] = df['BENZI_man'].apply(lambda x: p.get_pinyin(x, tone_marks='numbers'))
    merged_pd = df[df.apply(filter_non_pinyin, axis=1, reduce=True)]

    df['citation_man'] = df['pinyin'].apply(lambda x: [t[-1] for t in x.split('-')])
    df['initial_man'], df['final_man'] = zip(*df['pinyin'].apply(lambda x: get_pinyin_parts(x)))
    return df


def get_dst_parts(s, delimit=' '):
    s = s.translate(SUP)
    citation, initials, finals = [], [], []
    placeholder = ""
    blocks = s.split(delimit)
    for idx, block in enumerate(blocks):
        if any(c.isdigit() for c in block):
            citation.append(block.split('/')[-1])
            finals.append(placeholder)
            placeholder = ""
        elif block in CONSONANTS and blocks[idx - 1][-1].isdigit():
            initials.append(block)
        else:
            if blocks[idx - 1][-1].isdigit():
                initials.append("")
            placeholder = placeholder + block
    return citation, initials, finals


def process_teochew(df):
    df['citation_teo'] = df['SEGMENTS_teo'].apply(lambda x: x.translate(SUP))
    df['citation_teo'], df['initial_teo'], df['final_teo'] = \
        zip(*df['citation_teo'].apply(lambda x: get_dst_parts(x)))
    return df


def merge_dataframe(df):
    df = df[~df.citation_teo.isin(['52'])]  # drop tone 52 as it appears to be an outlier
    if src_lan == 'Mandarin':
        df.columns=['BENZI_IN_SOURCE_teo', 'BENZI_man', 'citation_teo','initial_teo',
                'final_teo','citation_man', 'initial_man', 'final_man']
        return df[df.citation_teo.map(len) == df.citation_man.map(len)]

    elif src_lan == 'Guangzhou':
        df.columns = ['BENZI_IN_SOURCE_teo', 'BENZI_man', 'citation_teo', 'initial_teo',
                      'final_teo', 'citation_can', 'initial_can', 'final_can']
        return df[df.citation_teo.map(len) == df.citation_can.map(len)]


# return a dataframe ready to plot contigency table
# src can be 'man': mandarin or 'can': cantonese
def plot_tones(src, df):
    teochew_citation = df['citation_teo'].values.tolist()
    src_citation = df['citation_{}'.format(src)].values.tolist()
    dic = dict()
    for tc, mc in zip(teochew_citation, src_citation):
        if (tc, mc) not in dic:
            dic[(tc, mc)] = 1
            continue
        dic[(tc, mc)] += 1

    if src == 'man':
        src_tone_mapping = man_tone_mapping
    elif src == 'can':
        src_tone_mapping = can_tone_mapping

    freq_pd = pd.DataFrame(columns=['teo_tone', '{}_tone'.format(src), 'frequency'])
    idx = 0
    for (teochew_tone, src_tone), freq in dic.items():
        freq_pd.loc[idx] = [teo_tone_mapping[teochew_tone]+'({})'.format(teochew_tone),
                            src_tone_mapping[src_tone]+'({})'.format(src_tone), freq]
        idx += 1
    return freq_pd

