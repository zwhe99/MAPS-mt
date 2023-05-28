## 🗺️ MAPS: Multi-Aspect Prompting and Selection

Implementaion of our [paper](https://arxiv.org/abs/2305.04118):

```
Exploring Human-Like Translation Strategy with Large Language Models
```
<!-- good luck! -->
## MAPS

**Motivation**

<p align="center">
<img src="imgs/intro.png" alt="intro"  width="350" />
</p>
The difference between machine and human translation in an English-Chinese example. Typical neural machine translation is a source-target mapping process, while human translators can take complex steps to ensure the quality and accuracy of the translation.

<br><br>

**MAPS Framework**

<p align="center">
<img src="imgs/method.png" alt="method"  width="800" />
</p>

MAPS aims to enable LLMs to mimic the human translation process by multi-aspect prompting and selection.

<br>

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
  conda create -n maps -c pytorch -c nvidia python==3.8.13 krb5 git pytorch==2.0.0 pytorch-cuda=11.7
  ```
* Install other python packages

  ```
  pip3 install -r requirements.txt
  ```

<br>

## Reproduce

### Run

**Preparation**

* Set your openai API_KEY in `model/openai/translate.py`
* Set Alpaca checkpoint file in `run-maps-alpaca.sh` and `run-translation-alpaca.sh`

**Run MAPS**

* text-davinci-003: `sh run-maps.sh `
* Alpaca: `sh run-maps-alpaca.sh `

**Run other methods**

* text-davinci-003: `sh run-translation-003.sh `
* Alpaca: `sh run-translation-alpaca.sh `



***Note**: The translation results have already been generated and saved in the `output` directory. Therefore, the scripts won't repeat the inference. If you want to regenerate the results, simply delete the contents within the `output` directory.*

<br>

### Evaluation

`sh run-evaluation.sh > evaluation.log`



## Interactive

If you just want to have a try, you can try the interactive script like this without need of GPU or CUDA (only text-davinci-003 now):

```shell
# Preparation
wget https://unbabel-experimental-models.s3.amazonaws.com/comet/wmt21/wmt21-comet-qe-da.tar.gz
tar -xf wmt21-comet-qe-da.tar.gz -C eval_ckpt/   
conda create -n maps -c pytorch python==3.8.13 pytorch==2.0.0  
conda activate maps
```
```shell
# Interactive
(maps) zwhe@zhiweideMacBook-Pro MAPS-mt % python3 interactive.py --lang-pair en-zh

Enter source English sentence: Joint Aid for Dogs is a high specification joint and muscle supplement with glucosamine for dogs, designed to aid freedom of movement.

Candidate_base: 联合援助犬是一种高规格的联合肌肉补充剂，含有用于狗的葡萄糖胺，旨在帮助自由运动。

Keyword Pairs: Joint Aid for Dogs=联合救助犬, glucosamine=葡糖胺
Candidate_kw: 联合救助犬是一种高规格的关节和肌肉补充剂，含有葡糖胺，旨在帮助犬类自由活动。

Topics: Animal care
Candidate_topic: Joint Aid for Dogs 是一种高规格的膝关节和肌肉补充剂，含有用于狗的葡糖胺，旨在帮助它们自由活动。

Related English-Chinese sentence pairs: Joint Aid for Dogs also contains chondroitin, which helps to maintain healthy joint cartilage and reduce inflammation.  Joint Aid for Dogs还含有胶原蛋白，有助于维持健康的关节软骨，减少炎症。
Candidate_demo: Joint Aid for Dogs是一种高规格的关节和肌肉补充剂，含有用于狗的葡糖胺，旨在帮助自由运动。

Final output: Joint Aid for Dogs 是一种高规格的膝关节和肌肉补充剂，含有用于狗的葡糖胺，旨在帮助它们自由活动。
```

Remember to set your openai API_KEY in `model/openai/translate.py`



## Citaion

```ruby
@article{he2023exploring,
  title={Exploring Human-Like Translation Strategy with Large Language Models},
  author={He, Zhiwei and Liang, Tian and Jiao, Wenxiang and Zhang, Zhuosheng and Yang, Yujiu and Wang, Rui and Tu, Zhaopeng and Shi, Shuming and Wang, Xing},
  journal={arXiv preprint arXiv:2305.04118},
  year={2023}
}
```

