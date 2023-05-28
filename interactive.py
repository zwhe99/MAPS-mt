import os
import argparse
from langcodes import Language
from data import demo_ex_dict, kw_ex_dict, topic_ex_dict
from model.openai.translate import translate_with_backoff, api_key, model2max_context, num_tokens_from_string
from comet import load_from_checkpoint, download_model
from typing import List
import logging

SUPPORTED_LANG_PAIRS = ["en-de", "de-en", "en-zh", "zh-en", "en-ja", "ja-en", "de-fr", "fr-de"]
MODEL_NAME = "text-davinci-003" #TODO: support more models
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

def mine_keywords(source_sentence: str, src_lng: str, tgt_lng: str, src_full: str, tgt_full: str):
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
    return query(prompt)

def mine_topics(source_sentence: str, src_lng: str, tgt_lng: str):
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
    return query(prompt)

def mine_demo(source_sentence: str, src_lng: str, tgt_lng: str, src_full: str, tgt_full: str):
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
    return query(prompt)

def mine_knowledge(source_sentence: str, src_lng: str, tgt_lng: str, src_full: str, tgt_full: str):
    keywords = mine_keywords(source_sentence, src_lng, tgt_lng, src_full, tgt_full)
    topics = mine_topics(source_sentence, src_lng, tgt_lng)
    demo = mine_demo(source_sentence, src_lng, tgt_lng, src_full, tgt_full)
    return keywords, topics, demo

def translate_with_knowledge(knowledge_type: str, knowledge_content: str, source_sentence: str, src_full: str, tgt_full: str):
    prompt = f"{knowledge_type}: {knowledge_content}\n\n" + \
        f"Instruction: Given the above knowledge, translate the following {src_full} text into {tgt_full}.\n" + \
        f"{src_full}: {source_sentence}\n" + \
        f"{tgt_full}:"
    return query(prompt)

def translate(source_sentence: str, src_full: str, tgt_full: str):
    prompt = f"Instruction: Translate the following {src_full} text into {tgt_full}.\n" + \
        f"{src_full}: {source_sentence}\n" + \
        (f"{tgt_full}:")
    return query(prompt)

def comet_qe(comet_model, source_sentence: str, translation_candidates: List[str], use_gpu: bool):
    data = []
    for translation_candidate in translation_candidates:
        data.append({"mt": translation_candidate, "src": source_sentence, "ref": None})

    model_output = comet_model.predict(data, batch_size=4, gpus=1 if use_gpu else 0, progress_bar=False)
    scores = model_output.scores

    return scores

def argmax(lst):
    return lst.index(max(lst))

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
        candidate_base = translate(source_sentence, src_full, tgt_full)
        candidate_kw = translate_with_knowledge("Keyword Pairs", keywords, source_sentence, src_full, tgt_full)
        candidate_topic = translate_with_knowledge("Topics", topics, source_sentence, src_full, tgt_full)
        candidate_demo = translate_with_knowledge(f"Related {src_full}-{tgt_full} sentence pairs", demo, source_sentence, src_full, tgt_full)

        # knowledge selection
        candidates = [candidate_base, candidate_kw, candidate_topic, candidate_demo]
        scores = comet_qe(comet_model, source_sentence, candidates, args.use_gpu)
        final_translaton = candidates[argmax(scores)]

        # output
        if args.only_final:
            print(final_translaton)
        else:
            print(f"Candidate_base: {candidate_base}\n")
            print(f"Keyword Pairs: {keywords}")
            print(f"Candidate_kw: {candidate_kw}\n")
            print(f"Topics: {topics}")
            print(f"Candidate_topic: {candidate_topic}\n")
            print(f"Related {src_full}-{tgt_full} sentence pairs: {demo}")
            print(f"Candidate_demo: {candidate_demo}\n")
            print(f"Final output: {final_translaton}")

if __name__ == "__main__":
    args = parse_args()
    main(args)