import os
import re
import torch
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--model-name-or-path', type=str, required=True, help='model name in the hub or local path')
    parser.add_argument('--input','-i', type=str, required=True, help='input file')
    parser.add_argument('--output','-o', type=str, required=True, help='output file')
    parser.add_argument('--search-algorithm', '-sa', type=str, default='beam', help='search algorithms: sample, beam')
    parser.add_argument('--batch', '-b', type=int, default=2, help='batch size')
    parser.add_argument('--temperature', '-t', type=float, default=0.1, help='temperature: 0.7 for text generation')
    args = parser.parse_args()

    seed = args.seed
    model_name_or_path = args.model_name_or_path
    input_file = args.input
    output_file = args.output
    search = args.search_algorithm
    batch = args.batch
    temperature = args.temperature

    # read output file
    num_done = 0
    if os.path.exists(output_file):
        with open(output_file, 'r') as out_file:
            num_done = len(out_file.readlines())

    # get input samples
    with open(input_file, 'r') as in_file:
        in_file_str = in_file.read()
    in_samples = in_file_str.strip().split("\n\n\n")
    for idx in range(len(in_samples)):
        smp = in_samples[idx]
        assert len(re.compile(r'\d\d\d\d\n').findall(smp)) >= 1
        in_samples[idx] = smp.replace(f"{idx:04}\n", "", 1).strip()
    in_samples = in_samples[num_done:]

    if len(in_samples) == 0:
        exit(0)

    # Load checkpoints
    model = AutoModelForCausalLM.from_pretrained(model_name_or_path, torch_dtype=torch.float16, device_map="auto")
    print(model.hf_device_map)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=False)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    gen_config = GenerationConfig(
                    temperature=temperature,
                    do_sample=True,
                    num_beams=1,
                    max_new_tokens=256,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token=tokenizer.pad_token_id,
                )

    if search == "beam":
        gen_config = GenerationConfig(
                        temperature=temperature,
                        num_beams=1,
                        max_new_tokens=256,
                        eos_token_id=tokenizer.eos_token_id,
                        pad_token=tokenizer.pad_token_id,
                    )

    # Generate
    if len(in_samples) > 0:
        torch.manual_seed(args.seed)
        with open(output_file, 'a', encoding='utf-8') as fo:
            for i in range(0, len(in_samples), batch):
                p = in_samples[i:i+batch]
                tokenized = tokenizer(p, padding=True, return_tensors="pt")
                input_ids = tokenized.input_ids.cuda()
                attn_mask = tokenized.attention_mask.cuda()
                input_ids = input_ids[:, :-1] if input_ids[0, -1] == tokenizer.eos_token_id else input_ids
                attn_mask = attn_mask[:, :-1] if input_ids[0, -1] == tokenizer.eos_token_id else attn_mask

                with torch.no_grad():
                    generated_ids = model.generate(inputs=input_ids, attention_mask=attn_mask, generation_config=gen_config)

                for original_input, gen_id in zip(input_ids, generated_ids):
                    original_text = tokenizer.decode(original_input, skip_special_tokens=True)
                    gen_text = tokenizer.decode(gen_id, skip_special_tokens=True)
                    new_text = gen_text.replace(original_text, "").replace("\n", "").strip()
                    print(new_text, file=fo, flush=True)