import random
import os
from langcodes import Language
import argparse

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-w', "--workspace", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), help="Workspace dir")
    parser.add_argument('-tn', "--test-name", type=str, required=True, help="wmt22/wmt21/...")
    parser.add_argument('-vn', "--valid-name", type=str, help="wmt22/wmt21/...")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument('-s', "--src", type=str, required=True, help='source lang')
    parser.add_argument('-t', "--tgt", type=str, required=True, help='target lang')
    parser.add_argument('-n', "--n-shot", type=int, required=True, help='# shot.')
    return parser.parse_args()

def main(args):
    workspace = args.workspace
    data_dir=os.path.join(workspace, "data")
    raw_dir=os.path.join(data_dir, "raw")
    format_dir=os.path.join(data_dir, "format")
    test_name = args.test_name
    valid_name = args.valid_name
    seed = args.seed
    src = args.src
    tgt = args.tgt
    src_full = Language.make(language=src).display_name()
    tgt_full = Language.make(language=tgt).display_name()
    shot = args.n_shot

    assert shot == 0 or (shot > 0 and valid_name)

    # seed random
    random.seed(seed)

    # read files
    with open(os.path.join(raw_dir, f"{test_name}.{src}-{tgt}.{src}")) as test_src_f:
        test_src_lines = [l.strip() for l in test_src_f.readlines()]

    if shot == 0:
        out_file_path = os.path.join(format_dir, f"{test_name}.{src}-{tgt}.{src}.{0}-shot")
        valid_src_lines = None
        valid_tgt_lines = None
    else:
        with open(os.path.join(raw_dir, f"{valid_name}.{src}-{tgt}.{src}")) as valid_src_f, \
            open(os.path.join(raw_dir, f"{valid_name}.{src}-{tgt}.{tgt}")) as valid_tgt_f:
            valid_src_lines = [l.strip() for l in valid_src_f.readlines()]
            valid_tgt_lines = [l.strip() for l in valid_tgt_f.readlines()]
        out_file_path = os.path.join(format_dir, f"{test_name}.{src}-{tgt}.{src}.{shot}-shot.{seed}-seed")

    demos = []
    if shot > 0:
        demos = random.sample(list(zip(valid_src_lines, valid_tgt_lines)), shot)

    with open(out_file_path, 'w') as out_f:
        for id, src_line in enumerate(test_src_lines):
            all_items = demos + [(src_line, None)]
            prompt_lst = []
            for it in all_items:
                it_src, it_tgt = it
                s = f"Instruction: Translate the following {src_full} text into {tgt_full}.\n" + \
                f"{src_full}: {it_src}\n" + \
                (f"{tgt_full}: {it_tgt}" if it_tgt else f"{tgt_full}:")
                prompt_lst.append(s)

            prompt = "\n\n".join(prompt_lst)
            out_f.write(
                f"{id:04}\n"
                f"{prompt}\n\n\n"
            )

if __name__ == "__main__":
    args = parse_args()
    main(args)
