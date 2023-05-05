## MAPS: Multi-Aspect Prompting and Selection

This is the implementaion of our paper:

```
Bridging the Data Gap between Training and Inference for Unsupervised Neural Machine Translation
Zhiwei He*, Xing Wang, Rui Wang, Shuming Shi, Zhaopeng Tu
```

## Dependencies

* Download COMET and BLEURT checkpoints:

  ```shell
  wget https://unbabel-experimental-models.s3.amazonaws.com/comet/wmt21/wmt21-comet-qe-da.tar.gz
  tar -xf wmt21-comet-qe-da.tar.gz -C eval_ckpt/

  wget https://storage.googleapis.com/bleurt-oss-21/BLEURT-20.zip .
  unzip -d eval_ckpt/ BLEURT-20.zip
  ```
* Create conda env

  ```shell
  conda create -n maps -c pytorch -c nvidia -c conda-forge python==3.8.13 krb5 git pytorch==2.0.0 pytorch-cuda=11.7
  ```
* Install other python packages

  ```
  pip3 install -r requirements.txt
  ```

## Run

* Set your openai API_KEY in `model/openai/translate.py`
* Set Alpaca checkpoint file in `run-maps.sh` and `run-translation.sh`

**Run MAPS**

`sh run-maps.sh `

**Run other methods**

`sh run-maps.sh `

*Note: The translation results have already been generated and saved in the `output` directory. Therefore, the scripts won't repeat the inference. If you want to regenerate the results, simply delete the contents within the `output` directory.*

## Evaluation

`sh run-evaluation.sh > evaluation.log`