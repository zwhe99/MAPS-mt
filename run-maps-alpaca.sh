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

# >>>>>>> Step1: Knowledge Minging >>>>>>>
for lp in ${all_lang_pairs[@]}
do
	echo $lp
    src=${lp%%-*}
    tgt=${lp##*-}

    python3 $DATA/format_ask_kw.py \
        -w $WS \
        -tn wmt22 \
        --seed 0 \
        -s $src \
        -t $tgt

    python3 $DATA/format_ask_topic.py \
        -w $WS \
        -tn wmt22 \
        --seed 0 \
        -s $src \
        -t $tgt

    python3 $DATA/format_ask_demo.py \
        -w $WS \
        -tn wmt22 \
        --seed 0 \
        -s $src \
        -t $tgt
done

# alpaca-7b
model_name=alpaca-7b
mkdir -p $OUTPUT/$model_name
for lp in ${all_lang_pairs[@]}
do
    echo $model_name $lp
    src=${lp%%-*}
    tgt=${lp##*-}

    for know in kw topic demo
    do
        python3 $WS/model/alpaca/translate.py \
            --model-name-or-path $ALPACA_CKPT \
            -i $FORMAT/$test_name.$lp.$src.ask-$know \
            -o $OUTPUT/$model_name/$test_name.$lp.$src.ask-$know \
            --search-algorithm beam \
            --batch $BS \
            --temperature 0
        cat $OUTPUT/$model_name/$test_name.$lp.$src.ask-$know | python3 $SCRIPT/alpaca-post-process.py > $OUTPUT/$model_name/$test_name.$lp.$src.ask-$know.trans
    done
done
# <<<<<<< Step1: Knowledge Minging <<<<<<<



# >>>>>>> Step2: Knowledge Integration >>>>>>>>
for lp in ${all_lang_pairs[@]}
do
    echo $lp
    src=${lp%%-*}
    tgt=${lp##*-}

    for know in kw topic demo
    do
        python3 $DATA/format-$know.py \
            -w $WS \
            -tn wmt22 \
            -m alpaca-7b \
            --seed 0 \
            -s $src \
            -t $tgt
    done
done

# alpaca-7b
model_name=alpaca-7b
mkdir -p $OUTPUT/$model_name
for lp in ${all_lang_pairs[@]}
do
    echo $model_name $lp
    src=${lp%%-*}
    tgt=${lp##*-}

    for know in kw topic demo
    do
        python3 $WS/model/alpaca/translate.py \
            --model-name-or-path $ALPACA_CKPT \
            -i $FORMAT/with-knowledge/$model_name/$test_name.$lp.$src.$know.0-seed \
            -o $OUTPUT/$model_name/$test_name.$lp.$tgt.$know.0-seed.trans \
            --search-algorithm beam \
            --batch $BS \
            --temperature 0
    done
done
# <<<<<<< Step2: Knowledge Integration <<<<<<<



# >>>>>>> Step3: Knowledge Selection >>>>>>>>
# alpaca-7b
for lp in ${all_lang_pairs[@]}
do
    src=${lp%%-*}
    tgt=${lp##*-}
    python3 $SCRIPT/knowledge-selection.py \
        --sys   $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.0-shot.trans \
                $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.kw.0-seed.trans \
                $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.topic.0-seed.trans \
                $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.demo.0-seed.trans \
        --src   $RAW/wmt22.$lp.$src \
        --ref   $RAW/wmt22.$lp.$tgt \
        --out   $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.maps.0-seed.trans \
        --src-lang $src --tgt-lang $tgt \
        -bs     $KS_BS \
        --metric comet_qe \
        --comet-qe-model-name wmt21-comet-qe-da

    python3 $SCRIPT/knowledge-selection.py \
        --sys   $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.0-shot.trans \
                $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.kw.0-seed.trans \
                $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.topic.0-seed.trans \
                $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.demo.0-seed.trans \
        --src   $RAW/wmt22.$lp.$src \
        --ref   $RAW/wmt22.$lp.$tgt \
        --out   $OUTPUT/alpaca-7b/wmt22.$lp.$tgt.maps_bound.0-seed.trans \
        --src-lang $src --tgt-lang $tgt \
        -bs     $KS_BS \
        --metric comet \
        --comet-model-name Unbabel/wmt22-comet-da
done
# <<<<<<< Step3: Knowledge Selection <<<<<<<