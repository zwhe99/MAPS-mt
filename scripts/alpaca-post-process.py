#! /usr/bin/python

import sys
import re
import os

all_langs = []
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lang.list"), 'r') as reader:
    for sample in reader:
        lang, code = sample.strip().split('\t')
        all_langs.append(lang)
        if '(' in lang:
            lang = lang[:lang.find('(')].strip()
            all_langs.append(lang)
all_langs = list(set(all_langs))
all_langs.extend(["Englisch", "Deutsch", "中文", "德文", "Chinesisch", "Français", "日本语", "英文", "中文(简体)", "Italiano", "英语(美国)", "Spanisch", "Arabic"])


def rep(s):
    return s.replace('(', '\(').replace(')', '\)')

all_langs = [rep(lang) for lang in all_langs]

pattern = re.compile('(' + '|'.join(all_langs) + '):.*')


def filter(sample):
    sample = re.sub('A:.*', '', sample)
    sample = re.sub('Output:.*', '', sample)
    sample = re.sub('Input:.*', '', sample)
    sample = re.sub('输出：.*', '', sample)
    sample = re.sub('输入：.*', '', sample)
    sample = re.sub('Correct Translate:.*', '', sample)
    sample = re.sub('Incorrect Translate:.*', '', sample)
    sample = re.sub('Instruction:.*', '', sample)
    sample = re.sub("Let's extract the keywords in the following.*", '', sample)
    sample = re.sub("Use a few words to describe the topics of the following input sentence.*", '', sample)
    sample = re.sub("Let's write an (.*) sentence related to but different from the input (.*) sentence and translate it into.*", '', sample)
    sample = pattern.sub('', sample)


    return sample


for sample in sys.stdin:
    print(filter(sample.strip()))

