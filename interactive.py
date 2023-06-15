import os
import difflib
import logging
import argparse
import warnings
from typing import List
from langcodes import Language
from data.trigger_sents import SUPPORT_LANGS
from comet import load_from_checkpoint, download_model
from data import demo_ex_dict, kw_ex_dict, topic_ex_dict
from model.openai.translate import api_key, model2max_context, num_tokens_from_string, batch_translate_with_backoff, translate_with_backoff
from tabulate import tabulate
from termcolor import colored
import shutil

warnings.filterwarnings("ignore", category=UserWarning, module="pytorch_lightning.trainer.setup")

SUPPORTED_LANG_PAIRS = [f"{s}-{t}"  for s in SUPPORT_LANGS for t in SUPPORT_LANGS if s != t]
MODEL_NAME = "text-davinci-003" #TODO: support more models
KNOW2COLOR = {
    "Keywords": 'light_red',
    "Topics": 'light_green',
    "Demo": 'light_yellow',
}
comet_model_mapping = {
    "wmt21-comet-qe-da": "wmt21-comet-qe-da/checkpoints/model.ckpt",
}

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--lang-pair", "-lp", type=str, required=True, choices=SUPPORTED_LANG_PAIRS, help="Language pair")
    parser.add_argument("--comet-qe-model-name", type=str, default="wmt21-comet-qe-da", help="COMET QE model name")
    parser.add_argument("--comet-saving-dir", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eval_ckpt'))
    parser.add_argument("--only-final", action="store_true", help="Only output the final translation")
    parser.add_argument("--use-gpu", action="store_true", help="Use gpu for QE model")
    return parser.parse_args()

def query(prompt):
    len_prompt = num_tokens_from_string(prompt, MODEL_NAME)
    return translate_with_backoff(
        prompt,
        MODEL_NAME,
        max_tokens=model2max_context[MODEL_NAME]-len_prompt,
        api_key=api_key,
        temperature=0.0
    )

def batch_query(prompts):
    if len(prompts) == 0:
        return []
    len_prompt = max([num_tokens_from_string(p, MODEL_NAME) for p in prompts])
    return batch_translate_with_backoff(
        prompts,
        MODEL_NAME,
        max_tokens=model2max_context[MODEL_NAME]-len_prompt,
        api_key=api_key,
        temperature=0.0
    )

def mine_keywords_prompt(source_sentence: str, src_lng: str, tgt_lng: str, src_full: str, tgt_full: str):
    ex = kw_ex_dict[(src_lng, tgt_lng)]
    all_items = ex + [(source_sentence, None)]
    prompt_lst = []
    for it in all_items:
        it_src, it_kw = it
        s = f"Let's extract the keywords in the following {src_full} sentence, and then translate these keywords into {tgt_full}.\n" + \
        f"{src_full}: {it_src}\n" + \
        (f"Keyword Pairs: {it_kw}" if it_kw else "Keyword Pairs:")
        prompt_lst.append(s)

    prompt = "\n\n".join(prompt_lst)
    return prompt

def mine_topics_prompt(source_sentence: str, src_lng: str, tgt_lng: str):
    ex = topic_ex_dict[(src_lng, tgt_lng)]
    all_items = ex + [(source_sentence, None)]
    prompt_lst = []
    for it in all_items:
        it_src, it_topic = it
        s = f"Use a few words to describe the topics of the following input sentence.\n" + \
        f"Input: {it_src}\n" + \
        (f"Topics: {it_topic}" if it_topic else "Topics:")
        prompt_lst.append(s)

    prompt = "\n\n".join(prompt_lst)
    return prompt

def mine_demo_prompt(source_sentence: str, src_lng: str, tgt_lng: str, src_full: str, tgt_full: str):
    ex = demo_ex_dict[(src_lng, tgt_lng)]
    all_items = ex + [(source_sentence, None, None)]
    prompt_lst = []
    for it in all_items:
        it_src, it_demo_src, it_demo_tgt = it
        s = f"Let's write {'an' if src_full == 'English' else 'a'} {src_full} sentence related to but different from the input {src_full} sentence and translate it into {tgt_full}\n" + \
        f"Input {src_full} sentence: {it_src}\n" + \
        (f"Output {src_full}-{tgt_full} sentence pair: {it_demo_src}\t{it_demo_tgt}" if (it_demo_src and it_demo_tgt) else f"Output {src_full}-{tgt_full} sentence pair:")
        prompt_lst.append(s)

    prompt = "\n\n".join(prompt_lst)
    return prompt

def mine_knowledge(source_sentence: str, src_lng: str, tgt_lng: str, src_full: str, tgt_full: str):
    prompts = []
    prompts.append(mine_keywords_prompt(source_sentence, src_lng, tgt_lng, src_full, tgt_full))
    prompts.append(mine_topics_prompt(source_sentence, src_lng, tgt_lng))
    prompts.append(mine_demo_prompt(source_sentence, src_lng, tgt_lng, src_full, tgt_full))
    return batch_query(prompts)

def knowledge_integration(source_sentence: str, src_full: str, tgt_full: str, keywords: str, topics: str, demo: str):
    prompts = []
    prompts.append(translate_prompt(source_sentence, src_full, tgt_full))
    prompts.append(translate_with_knowledge_prompt("Keyword Pairs", keywords, source_sentence, src_full, tgt_full))
    prompts.append(translate_with_knowledge_prompt("Topics", topics, source_sentence, src_full, tgt_full))
    prompts.append(translate_with_knowledge_prompt(f"Related {src_full}-{tgt_full} sentence pairs", demo, source_sentence, src_full, tgt_full))
    return batch_query(prompts)

def translate_with_knowledge_prompt(knowledge_type: str, knowledge_content: str, source_sentence: str, src_full: str, tgt_full: str):
    prompt = f"{knowledge_type}: {knowledge_content}\n\n" + \
        f"Instruction: Given the above knowledge, translate the following {src_full} text into {tgt_full}.\n" + \
        f"{src_full}: {source_sentence}\n" + \
        f"{tgt_full}:"
    return prompt

def translate_prompt(source_sentence: str, src_full: str, tgt_full: str):
    prompt = f"Instruction: Translate the following {src_full} text into {tgt_full}.\n" + \
        f"{src_full}: {source_sentence}\n" + \
        (f"{tgt_full}:")
    return prompt

def comet_qe(comet_model, source_sentence: str, translation_candidates: List[str], use_gpu: bool):
    data = []
    for translation_candidate in translation_candidates:
        data.append({"mt": translation_candidate, "src": source_sentence, "ref": None})

    model_output = comet_model.predict(data, batch_size=4, gpus=1 if use_gpu else 0, progress_bar=False)
    scores = model_output.scores

    return scores

def argmax(lst):
    return lst.index(max(lst))

def find_diff_str(str1: str, str2: str, know_name: str, language: str) -> str:
    """Highlight the differecnt part in `str`

    Args:
        str1 (str): the reference string, i.e., the base candidates
        str2 (str): input string
        know_name (str): string of knowledge, should be in `KNOWS`
        language (str): the language full name

    Returns:
        str: highlighted str2
    """
    d = difflib.Differ()

    # helper function to process diffs
    def process_diff(diff):
        result = []
        for fragment in diff:
            if fragment[0] == ' ':
                result.append(fragment[2:])  # Keep unchanged parts
            elif fragment[0] == '-':
                continue  # Discard parts in str1 not in str2
            elif fragment[0] == '+':
                # Highlight additions from str2 not in str1
                result.append(colored(fragment[2:], KNOW2COLOR[know_name]))
        return result

    if language in ['English', 'German']:
        # split the input strings into word lists
        str1_list = str1.split()
        str2_list = str2.split()
        diff = d.compare(str1_list, str2_list)
        result = process_diff(diff)
        result = ' '.join(result)

    else:
        diff = d.compare(str1, str2)
        result = process_diff(diff)
        result = ''.join(result)

    return result

def main(args):
    src_lng, tgt_lng = args.lang_pair.split('-')
    src_full = Language.make(language=src_lng).display_name()
    tgt_full = Language.make(language=tgt_lng).display_name()

    # Loading the comet model
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(logging.ERROR)

    if args.comet_qe_model_name in comet_model_mapping:
        comet_model = load_from_checkpoint(os.path.join(args.comet_saving_dir, comet_model_mapping[args.comet_qe_model_name]))
    else:
        model_path = download_model(args.comet_qe_model_name, saving_directory=args.comet_saving_dir)
        comet_model = load_from_checkpoint(model_path)
    comet_model.eval()

    # Translate
    while True:
        source_sentence = ""
        while source_sentence == "":
            source_sentence = input(f"\nEnter source {src_full} sentence: ")

        # knowledge mining
        keywords, topics, demo = mine_knowledge(source_sentence, src_lng, tgt_lng, src_full, tgt_full)

        # knowledge integration
        candidate_base, candidate_kw, candidate_topic, candidate_demo = knowledge_integration(source_sentence, src_full, tgt_full, keywords, topics, demo)

        # knowledge selection
        candidates = [candidate_base, candidate_kw, candidate_topic, candidate_demo]
        scores = comet_qe(comet_model, source_sentence, candidates, args.use_gpu)
        final_translaton = candidates[argmax(scores)]

        # output
        if args.only_final:
            print(final_translaton)
        else:
            table = [
                [colored("Keywords", KNOW2COLOR["Keywords"]), f"{keywords}"],
                [colored("Topics", KNOW2COLOR["Topics"]), f"{topics}"],
                [colored("Demo", KNOW2COLOR["Demo"]), f"{demo}"],
                ["----", "--"],
                [colored("Cand Kw", KNOW2COLOR["Keywords"]), f"{find_diff_str(candidate_base, candidate_kw, 'Keywords', tgt_full)}"],
                [colored("Cand Topic", KNOW2COLOR["Topics"]), f"{find_diff_str(candidate_base, candidate_topic, 'Topics', tgt_full)}"],
                [colored("Cand Demo", KNOW2COLOR["Demo"]), f"{find_diff_str(candidate_base, candidate_demo, 'Demo', tgt_full)}"],
                ["Cand Base", f"{candidate_base}"],
                ["----", "--"],
                ["Final", colored(f"{final_translaton}", attrs=["bold"])],
            ]
            width = min(shutil.get_terminal_size().columns-18, 120)
            print(tabulate(table, tablefmt='fancy_grid', maxcolwidths=[None, width]))


if __name__ == "__main__":
    args = parse_args()
    main(args)