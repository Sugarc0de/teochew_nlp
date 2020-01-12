import itertools

TONE_VOWELS = {
  1: "āēīōūǖ",
  2: "áéíóúǘ",
  3: "ǎěǐǒǔǚ",
  4: "àèìòùǜ",
  5: "aeiouü",
}

VOWELS = ''.join(TONE_VOWELS.values())


def extract_pinyin_tones(input_pinyin):
  """Converts pinyin string into a list of tones
  eg: "bítì" -> [2,4]
  Extract groups of contiguous vowels, then for each group, identify the tone
  by looking up in the TONE_VOWELS table, otherwise default to 5.
  """
  tones = []
  for is_vowel, group in itertools.groupby(input_pinyin, lambda c: c in VOWELS):
    if is_vowel:
      vowel_group = ''.join(group)
      tone = 5
      for v in vowel_group:
        for t in [1, 2, 3, 4]:
          if v in TONE_VOWELS[t]:
            tone = t
      tones.append(tone)

  return tones
