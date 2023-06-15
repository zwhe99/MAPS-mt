set -e
set -u
BASEDIR=$(realpath `dirname $0`)
WS=$BASEDIR
DATA=$WS/data
FORMAT=$DATA/format
RAW=$DATA/raw
OUTPUT=$WS/output
SCRIPT=$WS/scripts
MODEL=$WS/model
ALPACA_CKPT=YOUR_ALPACA_CKPT
all_lang_pairs=(en-zh zh-en en-de de-en en-ja ja-en de-fr fr-de)
test_name=wmt22
BS=6
KS_BS=400

for lp in ${all_lang_pairs[@]}
do
    src=${lp%%-*}
    tgt=${lp##*-}
    python3 $DATA/format_base.py \
        -w $WS \
        -tn wmt22 \
        --seed 0 \
        -s $src \
        -t $tgt \
        -n 0
done

# alpaca-7b
model_name=alpaca-7b
mkdir -p $OUTPUT/$model_name
for lp in ${all_lang_pairs[@]}
do
    echo $model_name $lp
    src=${lp%%-*}
    tgt=${lp##*-}

    # sampling
    for idx in 1 2 3
    do
        python3 $MODEL/alpaca/translate.py \
            --seed $(($idx-1)) \
            --model-name-or-path $ALPACA_CKPT \
            -i $FORMAT/$test_name.$lp.$src.0-shot \
            -o $OUTPUT/$model_name/$test_name.$lp.$tgt.smp$idx.0-shot.trans \
            --search-algorithm sample \
            --batch $BS \
            --temperature 0.3
    done

    # base
    python3 $MODEL/alpaca/translate.py \
        --seed 0 \
        --model-name-or-path $ALPACA_CKPT \
        -i $FORMAT/$test_name.$lp.$src.0-shot \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.smp$idx.0-shot.trans \
        --search-algorithm beam \
        --batch $BS \
        --temperature 0
done

for lp in ${all_lang_pairs[@]}
do
    src=${lp%%-*}
    tgt=${lp##*-}
    python3 $SCRIPT/knowledge-selection.py \
        --sys   $OUTPUT/$model_name/wmt22.$lp.$tgt.smp1.0-shot.trans \
                $OUTPUT/$model_name/wmt22.$lp.$tgt.smp2.0-shot.trans \
                $OUTPUT/$model_name/wmt22.$lp.$tgt.smp3.0-shot.trans \
                $OUTPUT/$model_name/wmt22.$lp.$tgt.0-shot.trans \
        --src   $RAW/wmt22.$lp.$src \
        --ref   $RAW/wmt22.$lp.$tgt \
        --out   $OUTPUT/$model_name/wmt22.$lp.$tgt.rerank.0-seed.trans \
        --src-lang $src --tgt-lang $tgt \
        -bs     $KS_BS \
        --metric comet_qe \
        --comet-qe-model-name wmt21-comet-qe-da

    python3 $SCRIPT/knowledge-selection.py \
        --sys   $OUTPUT/$model_name/wmt22.$lp.$tgt.smp1.0-shot.trans \
                $OUTPUT/$model_name/wmt22.$lp.$tgt.smp2.0-shot.trans \
                $OUTPUT/$model_name/wmt22.$lp.$tgt.smp3.0-shot.trans \
                $OUTPUT/$model_name/wmt22.$lp.$tgt.0-shot.trans \
        --src   $RAW/wmt22.$lp.$src \
        --ref   $RAW/wmt22.$lp.$tgt \
        --out   $OUTPUT/$model_name/wmt22.$lp.$tgt.rerank_bound.0-seed.trans \
        --src-lang $src --tgt-lang $tgt \
        -bs     $KS_BS \
        --metric comet \
        --comet-model-name Unbabel/wmt22-comet-da
done