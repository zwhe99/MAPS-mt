import os
import torch
import json
import random
import logging
import argparse
import threading
import numpy as np
from sacrebleu.metrics import BLEU
from comet import load_from_checkpoint, download_model

comet_model_mapping = {
    "wmt21-comet-qe-da": "wmt21-comet-qe-da/checkpoints/model.ckpt",
}

def seed_everything(TORCH_SEED):
	random.seed(TORCH_SEED)
	os.environ['PYTHONHASHSEED'] = str(TORCH_SEED)
	np.random.seed(TORCH_SEED)
	torch.manual_seed(TORCH_SEED)
	torch.cuda.manual_seed_all(TORCH_SEED)
	torch.backends.cudnn.deterministic = True
	torch.backends.cudnn.benchmark = False

def bleu(**kwargs):
    sys_lines = kwargs["sys_lines"]
    ref_lines = kwargs["ref_lines"]
    tgt_lang = kwargs["tgt_lang"]

    if tgt_lang == "zh":
        return [BLEU(tokenize="zh").corpus_score([sys_line], [[ref_line]]).score for sys_line, ref_line in zip(sys_lines, ref_lines)]
    else:
        return [BLEU().corpus_score([sys_line], [[ref_line]]).score for sys_line, ref_line in zip(sys_lines, ref_lines)]

def randscore(**kwargs):
    sys_lines = kwargs["sys_lines"]
    n_line = len(sys_lines)
    random.uniform(0, 100)
    return [random.uniform(0, 100) for _ in range(n_line)]

def comet(**kwargs):
    sys_lines = kwargs["sys_lines"]
    src_lines = kwargs["src_lines"]
    ref_lines = kwargs["ref_lines"]
    comet_model_name = kwargs["comet_model_name"]
    comet_saving_dir = kwargs["comet_saving_dir"]
    comet_cache_dir = kwargs["comet_cache_dir"]
    batch_size = kwargs["batch_size"]
    cache_file = os.path.join(comet_cache_dir, 'comet_cache.json')

    cache_lock = threading.Lock()

    with cache_lock:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        else:
            cache = {}

    data = []
    new_sys_lines, new_src_lines, new_ref_lines = [], [], []
    for sys, src, ref in zip(sys_lines, src_lines, ref_lines):
        cache_key = json.dumps((comet_model_name, sys, src, ref), ensure_ascii=False)
        if cache_key not in cache:
            new_sys_lines.append(sys)
            new_src_lines.append(src)
            new_ref_lines.append(ref)
            data.append({"mt": sys, "src": src, "ref": ref})

    logging.info(f"COMET cache info: {len(sys_lines)-len(data)}/{len(sys_lines)}")
    if data:
        if comet_model_name in comet_model_mapping:
            comet_model = load_from_checkpoint(os.path.join(comet_saving_dir, comet_model_mapping[comet_model_name]))
        else:
            model_path = download_model(comet_model_name, saving_directory=comet_saving_dir)
            comet_model = load_from_checkpoint(model_path)
        comet_model.eval()
        model_output = comet_model.predict(data, batch_size=batch_size, gpus=1)
        scores = model_output.scores

        with cache_lock:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
            else:
                cache = {}

            for (sys, src, ref), score in zip(zip(new_sys_lines, new_src_lines, new_ref_lines), scores):
                cache_key = json.dumps((comet_model_name, sys, src, ref), ensure_ascii=False)
                cache[cache_key] = score

            with open(cache_file, 'w') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)

    with cache_lock:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)

        final_scores = [cache[json.dumps((comet_model_name, sys, src, ref), ensure_ascii=False)] for sys, src, ref in zip(sys_lines, src_lines, ref_lines)]

    return final_scores

def comet_qe(**kwargs):
    sys_lines = kwargs["sys_lines"]
    src_lines = kwargs["src_lines"]
    comet_qe_model_name = kwargs["comet_qe_model_name"]
    comet_saving_dir = kwargs["comet_saving_dir"]
    comet_cache_dir = kwargs["comet_cache_dir"]
    batch_size = kwargs["batch_size"]
    cache_file = os.path.join(comet_cache_dir, 'comet_qe_cache.json')

    cache_lock = threading.Lock()

    with cache_lock:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        else:
            cache = {}

    data = []
    new_sys_lines, new_src_lines = [], []
    for sys, src in zip(sys_lines, src_lines):
        cache_key = json.dumps((comet_qe_model_name, sys, src), ensure_ascii=False)
        if cache_key not in cache:
            new_sys_lines.append(sys)
            new_src_lines.append(src)
            data.append({"mt": sys, "src": src, "ref": None})

    logging.info(f"COMET-QE cache info: {len(sys_lines)-len(data)}/{len(sys_lines)}")
    if data:
        if comet_qe_model_name in comet_model_mapping:
            comet_model = load_from_checkpoint(os.path.join(comet_saving_dir, comet_model_mapping[comet_qe_model_name]))
        else:
            model_path = download_model(comet_qe_model_name, saving_directory=comet_saving_dir)
            comet_model = load_from_checkpoint(model_path)

        comet_model.eval()
        model_output = comet_model.predict(data, batch_size=batch_size, gpus=1)
        scores = model_output.scores

        with cache_lock:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
            else:
                cache = {}

            for (sys, src), score in zip(zip(new_sys_lines, new_src_lines), scores):
                cache_key = json.dumps((comet_qe_model_name, sys, src), ensure_ascii=False)
                cache[cache_key] = score

            with open(cache_file, 'w') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)

    with cache_lock:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)

        final_scores = [cache[json.dumps((comet_qe_model_name, sys, src), ensure_ascii=False)] for sys, src in zip(sys_lines, src_lines)]

    return final_scores

def readlines(file_path):
    if not file_path:
        return []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return [l.strip() for l in lines]

def argmax(lst):
    return lst.index(max(lst))

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--sys", nargs='+', required=True, help="candidates")
    parser.add_argument("--src", type=str, required=True, help="source")
    parser.add_argument("--ref", type=str, default=None, help="reference")
    parser.add_argument("--out", type=str, required=True, help="output path")
    parser.add_argument("--src-lang", type=str, required=True, help="source langauge code")
    parser.add_argument("--tgt-lang", type=str, required=True, help="target langauge code")

    parser.add_argument("--comet-qe-model-name", type=str, default="wmt21-comet-qe-da")
    parser.add_argument("--comet-model-name", type=str, default="Unbabel/wmt22-comet-da")
    parser.add_argument("--comet-saving-dir", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'eval_ckpt'))
    parser.add_argument("--comet-cache-dir", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cache', 'comet'))

    parser.add_argument("--metric", type=str, choices=["bleu", "comet", "comet_qe", "randscore"], required=True)
    parser.add_argument("-bs", "--batch-size", type=int, default=32)
    return parser.parse_args()

def main(args):
    seed = args.seed
    sys_file_paths = args.sys
    src_file_path = args.src
    ref_file_path = args.ref
    out_file_path = args.out
    src_lang = args.src_lang
    tgt_lang = args.tgt_lang

    comet_qe_model_name = args.comet_qe_model_name
    comet_model_name = args.comet_model_name
    comet_saving_dir = args.comet_saving_dir
    comet_cache_dir = args.comet_cache_dir

    metric = args.metric
    batch_size = args.batch_size

    if seed:
        seed_everything(seed)

    scorer = eval(metric)

    sys_lines_lst = [
        readlines(v)
        for v in sys_file_paths
    ]
    src_lines = readlines(src_file_path)
    ref_lines = readlines(ref_file_path)
    assert metric in ["comet_qe", "randscore"] or len(ref_lines) > 0
    assert all([len(sys_lines) ==  len(src_lines) for sys_lines in sys_lines_lst])

    combine_sys_lines = None
    metrics_lst = None
    metrics_lst = [
        scorer(**{
            "sys_lines": sys_lines,
            "src_lines": src_lines,
            "ref_lines": ref_lines,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "comet_qe_model_name": comet_qe_model_name,
            "comet_model_name": comet_model_name,
            "comet_cache_dir": comet_cache_dir,
            "comet_saving_dir": comet_saving_dir,
            "batch_size": batch_size
        })
        for sys_lines in sys_lines_lst
    ]

    if metrics_lst and (not combine_sys_lines):
        combine_sys_lines = []
        for i in range(len(src_lines)):
            metrics = [metrics[i] for metrics in metrics_lst]
            sys_lines = [sys_lines[i] for sys_lines in sys_lines_lst]
            max_idx = argmax(metrics)
            combine_sys_lines.append(sys_lines[max_idx])

    with open(out_file_path, 'w') as out_f:
        out_f.write("\n".join(combine_sys_lines) + '\n')

if __name__ == "__main__":
    args = parse_args()
    main(args)