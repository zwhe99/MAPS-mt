import os
from comet.cli.compare import *
import threading
import logging
from bleurt import score as bleurt_score
from sacrebleu.metrics import BLEU

comet_model_mapping = {
    "wmt21-comet-qe-da": "wmt21-comet-qe-da/checkpoints/model.ckpt",
}

def wait_until_path_exist(path):
    while not os.path.isdir(path):
        pass
    return

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

    return final_scores

def comet(**kwargs):
    sys_lines = kwargs["sys_lines"]
    src_lines = kwargs["src_lines"]
    ref_lines = kwargs["ref_lines"]
    comet_model_name = kwargs["comet_model_name"]
    comet_saving_dir = kwargs["comet_saving_dir"]
    comet_cache_dir = kwargs["comet_cache_dir"]
    batch_size = kwargs["batch_size"]
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

def bleu(**kwargs):
    sys_lines = kwargs["sys_lines"]
    ref_lines = kwargs["ref_lines"]
    tgt_lang = kwargs["tgt_lang"]
    assert len(sys_lines) == len(ref_lines)

    res = []
    for sys, ref in zip(sys_lines, ref_lines):
        bleu = BLEU(tokenize="flores200")
        res.append(bleu.corpus_score([sys], [[ref]]).score)
        del bleu

    return res

def display_statistical_results(data: Statistical_test_info) -> None:
    """Print out the T-test results for a system pair.

    Args:
        data (Statistical_test_info): Stats to be printed out.
    """
    print("==========================")
    print("x_name:", data["x_name"])
    print("y_name:", data["y_name"])

    print("\nBootstrap Resampling Results:")
    for k, v in data["bootstrap_resampling"].items():
        print("{}:\t{:.4f}".format(k, v))

    print("\nPaired T-Test Results:")
    for k, v in data["paired_t-test"].items():
        print("{}:\t{:.4f}".format(k, v))

    x_seg_scores = data["bootstrap_resampling"]["x-mean"]
    y_seg_scores = data["bootstrap_resampling"]["y-mean"]
    best_system = (
        data["x_name"]
        if x_seg_scores > y_seg_scores
        else data["y_name"]
    )
    worse_system = (
        data["x_name"]
        if x_seg_scores < y_seg_scores
        else data["y_name"]
    )
    if data["paired_t-test"]["p_value"] <= 0.05:
        print("Null hypothesis rejected according to t-test.")
        print("Scores differ significantly across samples.")
        print(f"{best_system} outperforms {worse_system}.")
    else:
        print("Null hypothesis can't be rejected.\nBoth systems have equal averages.")

def t_tests_summary(
    t_test_results: List[Statistical_test_info],
    translations: Tuple[Path_fr],
    threshold_p_value: float = 0.05,
) -> None:
    """Prints T-tests Summary

    Args:
        t_test_results (List[Statistical_test_info]): List of stats between systems.
        translations (Tuple[Path_fr]): Path to each system.
        threshold_p_value (float): Threshold for p_value. Defaults to 0.05.
    """
    n = len(translations)
    name2id = {os.path.basename(name): i for i, name in enumerate(translations)}
    grid = [[None] * n for name in translations]
    for t_test in t_test_results:
        p_value = t_test["paired_t-test"]["p_value"]
        x_id = name2id[t_test["x_name"]]
        y_id = name2id[t_test["y_name"]]
        grid[x_id][y_id] = False
        grid[y_id][x_id] = False
        if p_value < threshold_p_value:
            x_seg_scores = t_test["bootstrap_resampling"]["x-mean"]
            y_seg_scores = t_test["bootstrap_resampling"]["y-mean"]
            if x_seg_scores > y_seg_scores:
                grid[x_id][y_id] = True
            else:
                grid[y_id][x_id] = True

    # Add the row's name aka the system's name.
    grid = [(os.path.basename(name),) + tuple(row) for name, row in zip(translations, grid)]

    print("Summary")
    print("If system_x is better than system_y then:")
    print(
        f"Null hypothesis rejected according to t-test with p_value={threshold_p_value}."
    )
    print("Scores differ significantly across samples.")
    print(tabulate(grid, headers=("system_x \ system_y",) + tuple([os.path.basename(t) for t in translations])))

def score(cfg: Namespace, systems: List[Dict[str, List[str]]]) -> np.ndarray:
    """Scores each systems with a given model.

    Args:
        cfg (Namespace): comet-compare configs.
        systems (List[Dict[str, List[str]]]): List with translations for each system.

    Return:
        np.ndarray: segment-level scores flatten.
    """
    seg_scores = []
    for system in systems:
        samples = [dict(zip(system, t)) for t in zip(*system.values())]
        sys_lines= [s["mt"] for s in samples]
        src_lines= [s["src"] for s in samples]
        ref_lines= [s["ref"] for s in samples]
        comet_model_name = cfg.model
        comet_saving_dir = cfg.model_storage_path
        comet_cache_dir = cfg.comet_cache_dir
        bleurt_ckpt = cfg.bleurt_ckpt
        bleurt_cache_dir = cfg.bleurt_cache_dir
        batch_size = cfg.batch_size
        metric = cfg.metric
        tgt_lang = cfg.tgt_lang

        assert tgt_lang or metric != "bleu", "BLEU need to specify target language. (--tgt-lang xx)"

        seg_scores += eval(metric)(
            sys_lines=sys_lines,
            src_lines=src_lines,
            ref_lines=ref_lines,
            comet_model_name=comet_model_name,
            comet_saving_dir=comet_saving_dir,
            comet_cache_dir=comet_cache_dir,
            bleurt_ckpt=bleurt_ckpt,
            bleurt_cache_dir=bleurt_cache_dir,
            batch_size=batch_size,
            tgt_lang=tgt_lang
        )

    n = len(systems[0]["src"])
    # [grouper](https://docs.python.org/3/library/itertools.html#itertools-recipes)
    seg_scores = list(zip(*[iter(seg_scores)] * n))
    seg_scores = np.array(seg_scores, dtype="float32")  # num_systems x num_translations
    return seg_scores

def get_cfg() -> Namespace:
    """Parse the CLI options and arguments.

    Return:
        Namespace: comet-compare configs.
    """
    parser = ArgumentParser(
        description="Command for comparing multiple MT systems' translations."
    )
    parser.add_argument("--tgt-lang", type=str)
    parser.add_argument("-s", "--sources", type=Path_fr)
    parser.add_argument("-r", "--references", type=Path_fr)
    parser.add_argument("-t", "--translations", nargs="*", type=Path_fr)
    parser.add_argument("-d", "--sacrebleu_dataset", type=str)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--gpus", type=int, default=1)
    parser.add_argument(
        "--quiet", action="store_true", help="Sets all loggers to ERROR level."
    )
    parser.add_argument(
        "--only_system", action="store_true", help="Prints only the final system score."
    )
    parser.add_argument(
        "--num_splits",
        type=int,
        default=300,
        help="Number of random partitions used in Bootstrap resampling.",
    )
    parser.add_argument(
        "--sample_ratio",
        type=float,
        default=0.4,
        help="Percentage of the testset to use in each split.",
    )
    parser.add_argument(
        "--t_test_alternative",
        type=str,
        default="two-sided",
        help=(
            "Alternative hypothesis from scipy.stats.ttest_rel. The following options"
            + " are available: 'two-sided', 'less', 'greater'. Defaults to 'two-sided'"
        ),
    )
    parser.add_argument(
        "--to_json",
        type=str,
        default="",
        help="Exports results to a json file.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="Unbabel/wmt22-comet-da",
        help="COMET model to be used.",
    )
    parser.add_argument(
        "--model_storage_path",
        help=(
            "Path to the directory where models will be stored. "
            + "By default its saved in ~/.cache/torch/unbabel_comet/"
        ),
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'eval_ckpt'),
    )
    parser.add_argument(
        "--num_workers",
        help="Number of workers to use when loading data.",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--disable_cache",
        action="store_true",
        help=(
            "Disables sentence embeddings caching."
            + " This makes inference slower but saves memory."
        ),
    )
    parser.add_argument(
        "--disable_length_batching",
        action="store_true",
        help="Disables length batching. This makes inference slower.",
    )
    parser.add_argument(
        "--print_cache_info",
        action="store_true",
        help="Print information about COMET cache.",
    )
    parser.add_argument(
        "--comet_cache_dir",
        type=str,
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cache', 'comet')
    )
    parser.add_argument(
        "--bleurt_ckpt",
        type=str, 
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'eval_ckpt', 'BLEURT-20')
    )
    parser.add_argument(
        "--bleurt_cache_dir", 
        type=str, 
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cache', 'bleurt')
    )
    parser.add_argument(
        "--metric", 
        type=str, 
        choices=["comet", "bleurt", "bleu"],
        required=True
    )
    cfg = parser.parse_args()

    if cfg.sources is None and cfg.sacrebleu_dataset is None:
        parser.error(f"You must specify a source (-s) or a sacrebleu dataset (-d)")

    if cfg.sacrebleu_dataset is not None:
        if cfg.references is not None or cfg.sources is not None:
            parser.error(
                f"Cannot use sacrebleu datasets (-d) with manually-specified datasets (-s and -r)"
            )

        try:
            testset, langpair = cfg.sacrebleu_dataset.rsplit(":", maxsplit=1)
            cfg.sources = Path_fr(get_source_file(testset, langpair))
            cfg.references = Path_fr(get_reference_files(testset, langpair)[0])

        except ValueError:
            parser.error(
                "SacreBLEU testset format must be TESTSET:LANGPAIR, e.g., wmt20:de-en"
            )
        except Exception as e:
            import sys

            print("SacreBLEU error:", e, file=sys.stderr)
            sys.exit(1)
    # if cfg.metric == "comet":
    #     if cfg.model.endswith(".ckpt") and os.path.exists(cfg.model):
    #         cfg.model_path = cfg.model
    #     else:
    #         cfg.model_path = os.path.join(cfg.model_storage_path, comet_model_mapping[cfg.model])

    return cfg, parser

def compare_command() -> None:
    """CLI that uses comet to compare multiple systems in a pairwise manner."""
    cfg, parser = get_cfg()
    seed_everything(1)

    assert len(cfg.translations) > 1, "You must provide at least 2 translation files"

    with open(cfg.sources(), encoding="utf-8") as fp:
        sources = [line.strip() for line in fp.readlines()]

    translations = []
    for system in cfg.translations:
        with open(system, mode="r", encoding="utf-8") as fp:
            translations.append([line.strip() for line in fp.readlines()])

    if cfg.references is not None:
        with open(cfg.references(), encoding="utf-8") as fp:
            references = [line.strip() for line in fp.readlines()]
        systems = [
            {"src": sources, "mt": system, "ref": references} for system in translations
        ]
    else:
        systems = [{"src": sources, "mt": system} for system in translations]

    seg_scores = score(cfg, systems)
    population_size = seg_scores.shape[1]
    sys_scores = bootstrap_resampling(
        seg_scores,
        sample_size=max(int(population_size * cfg.sample_ratio), 1),
        num_splits=cfg.num_splits,
    )
    results = list(pairwise_bootstrap(sys_scores, cfg.translations))

    # Paired T_Test Results:
    pairs = combinations(zip(cfg.translations, seg_scores), 2)
    for (x_name, x_seg_scores), (y_name, y_seg_scores) in pairs:
        ttest_result = stats.ttest_rel(
            x_seg_scores, y_seg_scores, alternative=cfg.t_test_alternative
        )
        for res in results:
            if res["x_name"] == x_name and res["y_name"] == y_name:
                res["paired_t-test"] = {
                    "statistic": ttest_result.statistic,
                    "p_value": ttest_result.pvalue,
                }

    for res in results:
        res["x_name"] = os.path.basename(res["x_name"])
        res["y_name"] = os.path.basename(res["y_name"])

    info = {
        "statistical_results": results,
        "source": sources,
        "translations": [
            {
                "name": os.path.basename(name),
                "mt": trans,
                "scores": scores.tolist(),
            }
            for name, trans, scores in zip(cfg.translations, translations, seg_scores)
        ],
    }

    if references is not None:
        info["reference"] = references

    for data in results:
        display_statistical_results(data)

    print()
    t_tests_summary(results, tuple(cfg.translations))
    print()

    if cfg.to_json != "":
        with open(cfg.to_json, "w", encoding="utf-8") as outfile:
            json.dump(info, outfile, ensure_ascii=False, indent=4)
        print("Predictions saved in: {}.".format(cfg.to_json))

if __name__ == "__main__":
    compare_command()