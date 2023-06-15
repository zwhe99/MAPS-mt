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
all_lang_pairs=(en-zh zh-en en-de de-en en-ja ja-en de-fr fr-de)
test_name=wmt22

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

# text-davinci-003
model_name=text-davinci-003
mkdir -p $OUTPUT/$model_name
for lp in ${all_lang_pairs[@]}
do
    echo $model_name $lp
    src=${lp%%-*}
    tgt=${lp##*-}

    # sampling
    for idx in 1 2 3
    do
        python3 $MODEL/openai/translate.py \
            --model-name $model_name \
            -i $FORMAT/$test_name.$lp.$src.0-shot \
            -o $OUTPUT/$model_name/$test_name.$lp.$tgt.smp$idx.0-shot.trans \
            --temperature 0.3
    done

    # base
    python3 $MODEL/openai/translate.py \
        --model-name $model_name \
        -i $FORMAT/$test_name.$lp.$src.0-shot \
        -o $OUTPUT/$model_name/$test_name.$lp.$tgt.0-shot.trans \
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
        -bs     400 \
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
        -bs     400 \
        --metric comet \
        --comet-model-name Unbabel/wmt22-comet-da
done