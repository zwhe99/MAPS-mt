import os
import argparse
from comet import load_from_checkpoint, download_model
import os
import json
import threading
from bleurt import score as bleurt_score
import logging
from sacrebleu.metrics import BLEU

comet_model_mapping = {
    "wmt21-comet-qe-da": "wmt21-comet-qe-da/checkpoints/model.ckpt",
}

def wait_until_path_exist(path):
    while not os.path.isdir(path):
        pass
    return

def comet(**kwargs):
    sys_lines = kwargs["sys_lines"]
    src_lines = kwargs["src_lines"]
    ref_lines = kwargs["ref_lines"]
    comet_model_name = kwargs["comet_model_name"]
    comet_saving_dir = kwargs["comet_saving_dir"]
    comet_cache_dir = kwargs["comet_cache_dir"]
    batch_size = kwargs["batch_size"]
    cpu = kwargs["cpu"]
    cache_file = os.path.join(comet_cache_dir, 'comet_cache.json')
    
    wait_until_path_exist(comet_saving_dir)

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
        model_output = comet_model.predict(data, batch_size=batch_size, gpus=0 if cpu else 1)
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

    return sum(final_scores)/len(final_scores)

def comet_qe(**kwargs):
    sys_lines = kwargs["sys_lines"]
    src_lines = kwargs["src_lines"]
    comet_qe_model_name = kwargs["comet_qe_model_name"]
    comet_saving_dir = kwargs["comet_saving_dir"]
    comet_cache_dir = kwargs["comet_cache_dir"]
    batch_size = kwargs["batch_size"]
    cache_file = os.path.join(comet_cache_dir, 'comet_qe_cache.json')

    wait_until_path_exist(comet_saving_dir)

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

    return sum(final_scores)/len(final_scores)

def bleurt(**kwargs):
    sys_lines = kwargs["sys_lines"]
    ref_lines = kwargs["ref_lines"]
    bleurt_cache_dir = kwargs["bleurt_cache_dir"]
    bleurt_ckpt = kwargs["bleurt_ckpt"]
    batch_size = kwargs["batch_size"]
    cache_file = os.path.join(bleurt_cache_dir, 'bleurt_cache.json')
    cache_lock = threading.Lock()

    with cache_lock:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        else:
            cache = {}

    new_sys_lines, new_ref_lines = [], []
    for sys, ref in zip(sys_lines, ref_lines):
        cache_key = json.dumps((sys, ref), ensure_ascii=False)
        if cache_key not in cache:
            new_sys_lines.append(sys)
            new_ref_lines.append(ref)

    logging.info(f"BLEURT cache info: {len(sys_lines)-len(new_sys_lines)}/{len(sys_lines)}")
    assert len(new_sys_lines) == len(new_ref_lines)
    if len(new_sys_lines) > 0:
        bleurt_model = bleurt_score.LengthBatchingBleurtScorer(bleurt_ckpt)
        scores = bleurt_model.score(references=new_ref_lines, candidates=new_sys_lines, batch_size=batch_size)

        with cache_lock:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
            else:
                cache = {}

            for (sys, ref), score in zip(zip(new_sys_lines, new_ref_lines), scores):
                cache_key = json.dumps((sys, ref), ensure_ascii=False)
                cache[cache_key] = score

            with open(cache_file, 'w') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)

    with cache_lock:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        final_scores = [cache[json.dumps((sys, ref), ensure_ascii=False)] for sys, ref in zip(sys_lines, ref_lines)]

    return sum(final_scores)/len(final_scores)

def bleu(**kwargs):
    sys_lines = kwargs["sys_lines"]
    ref_lines = kwargs["ref_lines"]
    tgt_lang = kwargs["tgt_lang"]
    bleu = BLEU(tokenize="flores200")
    assert len(sys_lines) == len(ref_lines)
    return bleu.corpus_score(sys_lines, [ref_lines]).score

def readlines(file_path):
    if not file_path:
        return []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return [l.strip() for l in lines]

def check_equal_num_lines(paths):
    if len(paths) <= 1:
        return True
    else:
        return all([len(readlines(p)) == len(readlines(paths[0])) for p in paths[1:]])

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--sys", nargs='+', required=True)
    parser.add_argument("--src", type=str, required=True)
    parser.add_argument("--ref", type=str)
    parser.add_argument("--tgt-lang", type=str)
    parser.add_argument("--comet-qe-model-name", type=str, default="wmt21-comet-qe-da")
    parser.add_argument("--comet-model-name", type=str, default="Unbabel/wmt22-comet-da")
    parser.add_argument("--comet-cache-dir", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cache', 'comet'))
    parser.add_argument("--comet-saving-dir", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'eval_ckpt'))
    parser.add_argument("--bleurt-ckpt", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'eval_ckpt', 'BLEURT-20'))
    parser.add_argument("--bleurt-cache-dir", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cache', 'bleurt'))
    parser.add_argument("--metric", type=str, choices=["comet", "comet_qe", "bleurt", "bleu"], required=True)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--cpu", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    sys_file_paths = args.sys
    src_file_path = args.src
    ref_file_path = args.ref
    tgt_lang = args.tgt_lang
    comet_qe_model_name = args.comet_qe_model_name
    comet_model_name = args.comet_model_name
    comet_cache_dir = args.comet_cache_dir
    comet_saving_dir = args.comet_saving_dir
    bleurt_ckpt = args.bleurt_ckpt
    bleurt_cache_dir = args.bleurt_cache_dir
    metric = args.metric
    batch_size = args.batch_size
    cpu = args.cpu

    assert tgt_lang or metric != "bleu", "BLEU need to specify target language. (--tgt-lang xx)"

    sys_lines_lst = [
        readlines(v)
        for v in sys_file_paths
    ]
    src_lines = readlines(src_file_path)
    ref_lines = readlines(ref_file_path)

    if metric != "comet_qe":
        assert all([len(src_lines) == len(ref_lines)] + [len(sys_lines) ==  len(src_lines) for sys_lines in sys_lines_lst])
    else:
        assert all([len(sys_lines) ==  len(src_lines) for sys_lines in sys_lines_lst])

    scorer = eval(metric)
    scores = [
        scorer(**{
            "sys_lines": sys_lines,
            "src_lines": src_lines,
            "ref_lines": ref_lines,
            "comet_qe_model_name": comet_qe_model_name,
            "comet_model_name": comet_model_name,
            "comet_cache_dir": comet_cache_dir,
            "comet_saving_dir": comet_saving_dir,
            "bleurt_ckpt": bleurt_ckpt,
            "bleurt_cache_dir": bleurt_cache_dir,
            "batch_size": batch_size,
            "cpu": cpu,
            "tgt_lang": tgt_lang
        })
        for sys_lines in sys_lines_lst
    ]

    for n, s in zip(sys_file_paths, scores):
        if metric == "bleu":
            print(f"{os.path.basename(n)}: {s:.1f}")
        else:
            print(f"{os.path.basename(n)}: {s*100:.1f}")