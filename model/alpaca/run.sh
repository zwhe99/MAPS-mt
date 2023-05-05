set -e
set -u
WS=/apdcephfs_cq2/share_916081/timurhe/maps
CKPT=/apdcephfs_cq2/share_916081/timurhe/workspaces/MTLLM/llama-ft-7b.alpaca.8-A100-bs1/checkpoint-1218
DATA=$WS/data
FORMAT=$DATA/format
OUTPUT=$WS/output
SCRIPT=$WS/scripts
all_lang_pairs=(en-zh zh-en en-de de-en en-ja ja-en de-fr fr-de en-hr)

test_name=wmt22
model_name=alpaca-7b
existing_model_name=text-davinci-003
BS=6

for lp in ${all_lang_pairs[@]}
do
    echo $lp
    src=${lp%%-*}
    tgt=${lp##*-}

    echo $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-kw
    python3 translate.py \
        --model-name-or-path $CKPT \
        -i $FORMAT/$test_name.$lp.$src.5-shot.ask-kw \
        -o $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-kw \
        --search-algorithm beam \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0
    cat $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-kw | python3 $SCRIPT/alpaca-post-process.py > $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-kw.trans

    echo $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-topic
    python3 translate.py \
        --model-name-or-path $CKPT \
        -i $FORMAT/$test_name.$lp.$src.5-shot.ask-topic \
        -o $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-topic \
        --search-algorithm beam \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0
    cat $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-topic | python3 $SCRIPT/alpaca-post-process.py > $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-topic.trans

    echo $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-demo
    python3 translate.py \
        --model-name-or-path $CKPT \
        -i $FORMAT/$test_name.$lp.$src.5-shot.ask-demo \
        -o $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-demo \
        --search-algorithm beam \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0
    cat $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-demo | python3 $SCRIPT/alpaca-post-process.py > $OUTPUT/$model_name/$test_name.$lp.$src.5-shot.ask-demo.trans

    echo $OUTPUT/$model_name/$test_name.$lp.$tgt.smp1.0-shot
    python3 translate.py \
        --seed 0 \
        --model-name-or-path $CKPT \
        -i $FORMAT/$test_name.$lp.$src.0-shot \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.smp1.0-shot.trans \
        --search-algorithm sample \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0.3

    echo $OUTPUT/$model_name/$test_name.$lp.$tgt.smp2.0-shot
    python3 translate.py \
        --seed 1 \
        --model-name-or-path $CKPT \
        -i $FORMAT/$test_name.$lp.$src.0-shot \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.smp2.0-shot.trans \
        --search-algorithm sample \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0.3

    echo $OUTPUT/$model_name/$test_name.$lp.$tgt.smp3.0-shot
    python3 translate.py \
        --seed 2 \
        --model-name-or-path $CKPT \
        -i $FORMAT/$test_name.$lp.$src.0-shot \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.smp3.0-shot.trans \
        --search-algorithm sample \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0.3

    echo $OUTPUT/$model_name/$test_name.$lp.$tgt.smp4.0-shot
    python3 translate.py \
        --seed 3 \
        --model-name-or-path $CKPT \
        -i $FORMAT/$test_name.$lp.$src.0-shot \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.smp4.0-shot.trans \
        --search-algorithm sample \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0.3

    echo $OUTPUT/$model_name/$test_name.$lp.$tgt.0-shot
    python3 translate.py \
        --model-name-or-path $CKPT \
        -i $FORMAT/$test_name.$lp.$src.0-shot \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.0-shot.trans \
        --search-algorithm beam \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0

    echo $OUTPUT/$model_name/$test_name.$lp.$tgt.existing_know_$existing_model_name.0-seed
    python3 translate.py \
        --model-name-or-path $CKPT \
        -i $FORMAT/with-knowledge/$model_name/$test_name.$lp.$src.existing_know_$existing_model_name.0-seed \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.existing_know_$existing_model_name.0-seed.trans \
        --search-algorithm beam \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0

    echo $OUTPUT/$model_name/$test_name.$lp.$tgt.kw.0-seed
    python3 translate.py \
        --model-name-or-path $CKPT \
        -i $FORMAT/with-knowledge/$model_name/$test_name.$lp.$src.kw.0-seed \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.kw.0-seed.trans \
        --search-algorithm beam \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0

    echo $OUTPUT/$model_name/$test_name.$lp.$tgt.topic.0-seed
    python3 translate.py \
        --model-name-or-path $CKPT \
        -i $FORMAT/with-knowledge/$model_name/$test_name.$lp.$src.topic.0-seed \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.topic.0-seed.trans \
        --search-algorithm beam \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0

    echo $OUTPUT/$model_name/$test_name.$lp.$tgt.demo.0-seed
    python3 translate.py \
        --model-name-or-path $CKPT \
        -i $FORMAT/with-knowledge/$model_name/$test_name.$lp.$src.demo.0-seed \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.demo.0-seed.trans \
        --search-algorithm beam \
        --batch $BS \
        --tgt-lng $tgt \
        --temperature 0
done