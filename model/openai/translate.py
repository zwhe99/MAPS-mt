import os
import re
import openai
import argparse
import tiktoken
from tqdm import tqdm
import backoff

api_key = "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"

model2max_context = {
    "text-davinci-003": 4097,
}

class OutOfQuotaException(Exception):
    "Raised when the key exceeded the current quota"
    def __init__(self, key, cause=None):
        super().__init__(f"No quota for key: {key}")
        self.key = key
        self.cause = cause

    def __str__(self):
        if self.cause:
            return f"{super().__str__()}. Caused by {self.cause}"
        else:
            return super().__str__()

class AccessTerminatedException(Exception):
    "Raised when the key has been terminated"
    def __init__(self, key, cause=None):
        super().__init__(f"Access terminated key: {key}")
        self.key = key
        self.cause = cause

    def __str__(self):
        if self.cause:
            return f"{super().__str__()}. Caused by {self.cause}"
        else:
            return super().__str__()

def num_tokens_from_string(string: str, model_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def generate_batch(lst, batch_size):
    """  Yields batch of specified size """
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]

def post_procress(s: str):
    res = s.strip().replace("\n", " ")
    if res == "":
        res = " "
    return res

@backoff.on_exception(backoff.expo, (openai.error.OpenAIError, openai.error.RateLimitError, openai.error.APIError, openai.error.ServiceUnavailableError, openai.error.APIConnectionError), max_tries=5)
def translate_with_backoff(smp, model_name, max_tokens, api_key, temperature):
    try:
        response = openai.Completion.create(
            model=model_name, 
            prompt=smp,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
        )
        gen = response.choices[0].text

        gen = post_procress(gen)
        return gen

    except openai.error.RateLimitError as e:
        if "You exceeded your current quota, please check your plan and billing details" in e.user_message:
            raise OutOfQuotaException(api_key)
        elif "Your access was terminated due to violation of our policies" in e.user_message:
            raise AccessTerminatedException(api_key)
        else:
            raise e

@backoff.on_exception(backoff.expo, (openai.error.OpenAIError, openai.error.RateLimitError, openai.error.APIError, openai.error.ServiceUnavailableError, openai.error.APIConnectionError), max_tries=5)
def batch_translate_with_backoff(smp_lst, model_name, max_tokens, api_key, temperature):
    try:
        response = openai.Completion.create(
            model=model_name, 
            prompt=smp_lst,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
        )

        gen_lst = [""] * len(smp_lst)
        for choice in response.choices:
            gen = choice.text
            gen = post_procress(gen)  # Assuming your post_procress function can handle a single text
            gen_lst[choice.index] = gen
            
        return gen_lst

    except openai.error.RateLimitError as e:
        if "You exceeded your current quota, please check your plan and billing details" in e.user_message:
            raise OutOfQuotaException(api_key)
        elif "Your access was terminated due to violation of our policies" in e.user_message:
            raise AccessTerminatedException(api_key)
        else:
            raise e

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--model-name", type=str, required=True,
        help="Model name")
    parser.add_argument("-i", "--input", type=str, required=True,
        help="Input file path")
    parser.add_argument("-o", "--output", type=str, required=True,
        help="Output file path")
    parser.add_argument("--temperature", type=float, default=0,
        help="Sampling temperature")

    return parser.parse_args()

def main():
    args = parse_args()
    model_name = args.model_name
    in_file_path = args.input
    out_file_path = args.output
    temperature = args.temperature

    # get input samples
    input_file_path = os.path.join(in_file_path)
    with open(input_file_path, 'r') as in_file:
        in_file_str = in_file.read()
    samples = in_file_str.strip().split("\n\n\n")
    total = len(samples)

    # create or check output file
    num_done = 0
    output_file_path = os.path.join(out_file_path)
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as out_file:
            num_done = len(out_file.readlines())

    # translate
    pattern = re.compile(r'\d\d\d\d\n')
    with tqdm(total=total) as pbar:
        pbar.update(num_done)

        for to_be_translated_idx, to_be_translated_smp in enumerate(samples[num_done: ]):
            assert len(pattern.findall(to_be_translated_smp)) >= 1
            to_be_translated_smp = to_be_translated_smp.replace(f"{to_be_translated_idx:04}\n", "", 1).strip()
            len_prompt = num_tokens_from_string(to_be_translated_smp, model_name)
            gen = translate_with_backoff(
                to_be_translated_smp,
                model_name=model_name,
                max_tokens=model2max_context[model_name]-len_prompt,
                api_key=api_key,
                temperature=temperature
            )
            with open(output_file_path, 'a') as fout:
                fout.write(f"{gen}\n")
            pbar.update(1)

if __name__ == "__main__":
    main()