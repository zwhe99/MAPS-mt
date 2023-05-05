## MAPS: Multi-Aspect Prompting and Selection

This is the implementaion of our paper:

```
Bridging the Data Gap between Training and Inference for Unsupervised Neural Machine Translation
Zhiwei He*, Xing Wang, Rui Wang, Shuming Shi, Zhaopeng Tu
```


## Dependencies

* Download COMET and BLEURT checkpoints

  ```shell
  wget https://unbabel-experimental-models.s3.amazonaws.com/comet/wmt21/wmt21-comet-qe-da.tar.gz
  tar -xf wmt21-comet-qe-da.tar.gz -C eval_ckpt/

  wget https://storage.googleapis.com/bleurt-oss-21/BLEURT-20.zip .
  unzip -d eval_ckpt/ BLEURT-20.zip
  ```
* Install python packages

  ```
  pip3 install -r requirements.txt
  ```
