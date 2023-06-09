import random
import os
from langcodes import Language
import argparse
from .trigger_sents import SUPPORT_LANGS, TRIGGER_SENTS

KETWORDS = {
    "en": [
        ["Stanford University", "School of Medicine"],
        ["JAS 39C Gripen", "commercial flights"],
        ["Barça", "Sevilla"],
        ["Whitehall", "Downing Street", "Prime Minister's official residence"],
        ["Yahoo!", "Microsoft"]
    ],
    "zh": [
        ["斯坦福大学", "医学院"],
        ["JAS 39C 鹰狮战斗机", "商业航班"],
        ["巴萨", "塞维利亚队"],
        ["白厅", "唐宁街", "首相官邸"],
        ["雅虎", "微软"],
    ],
    "de": [
        ["Stanford Universität", "Medizinische Fakultät"],
        ["JAS 39C Gripen", "kommerzielle Flüge"],
        ["Barça", "Sevilla"],
        ["Whitehall", "Downing Straße", "offizielle Residenz des Premierministers"],
        ["Yahoo!", "Microsoft"],
    ],
    "ja": [
        ["スタンフォード大学", "医学部"],
        ["JAS 39C Gripen", "商用フライト"],
        ["バルサ", "セビージャ"],
        ["ホワイトホール", "ダウニングストリート", "首相官邸"],
        ["ヤフー", "マイクロソフト"]
    ],
    "fr": [
        ["Université Stanford", "l'école de médecine"],
        ["JAS 39C Gripen", "les vols commerciaux"],
        ["Barça", "Sevilla"],
        ["Whitehall", "Downing Street", "la résidence officielle du Premier ministre"],
        ["Yahoo!", "Microsoft"]
    ]
}

demo_dict = {}
for src_lng in SUPPORT_LANGS:
    for tgt_lng in SUPPORT_LANGS:
        if src_lng == tgt_lng:
            continue
        else:
            demo_dict[(src_lng, tgt_lng)] = [
                (tri_sent, ", ".join([f"{src_kw}={tgt_kw}" for src_kw, tgt_kw in zip(src_kw_lst, tgt_kw_lst)]))
                    for tri_sent, src_kw_lst, tgt_kw_lst in zip(TRIGGER_SENTS[src_lng], KETWORDS[src_lng], KETWORDS[tgt_lng])
            ]

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-w', "--workspace", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), help="Workspace dir")
    parser.add_argument('-tn', "--test-name", type=str, required=True, help="wmt22/wmt21/...")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument('-s', "--src", type=str, required=True, help='source lang')
    parser.add_argument('-t', "--tgt", type=str, required=True, help='target lang')
    return parser.parse_args()

def main(args):
    workspace = args.workspace
    data_dir=os.path.join(workspace, "data")
    raw_dir=os.path.join(data_dir, "raw")
    format_dir=os.path.join(data_dir, "format")
    test_name = args.test_name
    seed = args.seed
    src = args.src
    tgt = args.tgt
    src_full = Language.make(language=src).display_name()
    tgt_full = Language.make(language=tgt).display_name()

    # seed random
    random.seed(seed)

    # read files
    with open(os.path.join(raw_dir, f"{test_name}.{src}-{tgt}.{src}")) as test_src_f:

        test_src_lines = [l.strip() for l in test_src_f.readlines()]
        out_file_path = os.path.join(format_dir, f"{test_name}.{src}-{tgt}.{src}.ask-kw")

        demos = demo_dict[(src, tgt)]
        with open(out_file_path, 'w') as out_f:
            for id, src_line in enumerate(test_src_lines):
                all_items = demos + [(src_line, None)]
                prompt_lst = []
                for it in all_items:
                    it_src, it_kw = it
                    s = f"Let's extract the keywords in the following {src_full} sentence, and then translate these keywords into {tgt_full}.\n" + \
                    f"{src_full}: {it_src}\n" + \
                    (f"Keyword Pairs: {it_kw}" if it_kw else "Keyword Pairs:")
                    prompt_lst.append(s)

                prompt = "\n\n".join(prompt_lst)
                out_f.write(
                    f"{id:04}\n"
                    f"{prompt}\n\n\n"
                )

if __name__ == "__main__":
    args = parse_args()
    main(args)