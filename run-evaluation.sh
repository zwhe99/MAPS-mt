set -e
set -u
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/

BASEDIR=$(realpath `dirname $0`)
WS=$BASEDIR
DATA=$WS/data
FORMAT=$DATA/format
RAW=$DATA/raw
OUTPUT=$WS/output
SCRIPT=$WS/scripts
MODEL=$WS/model

BATCH_SIZE=400
all_lang_pairs=(en-zh zh-en en-de de-en en-ja ja-en de-fr fr-de)
model_names=(text-davinci-003 alpaca-7b)

# comet
for model_name in ${model_names[@]}
do
    cd $OUTPUT/$model_name
    for lp in ${all_lang_pairs[@]}
    do
        src=${lp%%-*}
        tgt=${lp##*-}
        CAND1=wmt22.$src-$tgt.$tgt.0-shot.trans
        CAND2=wmt22.$src-$tgt.$tgt.kw.0-seed.trans
        CAND3=wmt22.$src-$tgt.$tgt.topic.0-seed.trans
        CAND4=wmt22.$src-$tgt.$tgt.demo.0-seed.trans
        CAND5=wmt22.$src-$tgt.$tgt.rerank.0-seed.trans
        CAND6=wmt22.$src-$tgt.$tgt.rerank_bound.0-seed.trans
        CAND7=wmt22.$src-$tgt.$tgt.maps.0-seed.trans
        CAND8=wmt22.$src-$tgt.$tgt.maps_bound.0-seed.trans
        CANDS=($CAND1 $CAND2 $CAND3 $CAND4 $CAND5 $CAND6 $CAND7 $CAND8)

        src_file=$RAW/wmt22.$src-$tgt.$src
        ref_file=$RAW/wmt22.$src-$tgt.$tgt

        for CAND in ${CANDS[@]}
        do  
            if [[ ! -s $CAND ]]
            then
                echo "ERROR: file not found $CAND"
                exit 1
            fi
        done

        echo "COMET: $lp $model_name"
        python3 $SCRIPT/score.py \
            --sys ${CANDS[@]} \
            --src $src_file \
            --ref $ref_file \
            --comet-model-name Unbabel/wmt22-comet-da \
            --metric comet \
            --batch-size $BATCH_SIZE

        python3 $SCRIPT/compare.py \
            -t ${CANDS[@]} \
            -s $src_file \
            -r $ref_file \
            --model Unbabel/wmt22-comet-da \
            --batch_size $BATCH_SIZE \
            --metric comet
    done
done


# bleurt
for model_name in ${model_names[@]}
do
    cd $OUTPUT/$model_name
    for lp in ${all_lang_pairs[@]}
    do
        src=${lp%%-*}
        tgt=${lp##*-}
        CAND1=wmt22.$src-$tgt.$tgt.0-shot.trans
        CAND2=wmt22.$src-$tgt.$tgt.kw.0-seed.trans
        CAND3=wmt22.$src-$tgt.$tgt.topic.0-seed.trans
        CAND4=wmt22.$src-$tgt.$tgt.demo.0-seed.trans
        CAND5=wmt22.$src-$tgt.$tgt.rerank.0-seed.trans
        CAND6=wmt22.$src-$tgt.$tgt.rerank_bound.0-seed.trans
        CAND7=wmt22.$src-$tgt.$tgt.maps.0-seed.trans
        CAND8=wmt22.$src-$tgt.$tgt.maps_bound.0-seed.trans
        CANDS=($CAND1 $CAND2 $CAND3 $CAND4 $CAND5 $CAND6 $CAND7 $CAND8)

        src_file=$RAW/wmt22.$src-$tgt.$src
        ref_file=$RAW/wmt22.$src-$tgt.$tgt

        for CAND in ${CANDS[@]}
        do  
            if [[ ! -s $CAND ]]
            then
                echo "ERROR: file not found $CAND"
                exit 1
            fi
        done

        echo "BLEURT: $lp $model_name"
        python3 $SCRIPT/score.py \
            --sys ${CANDS[@]} \
            --src $src_file \
            --ref $ref_file \
            --metric bleurt \
            --batch-size $BATCH_SIZE

        python3 $SCRIPT/compare.py \
            -t ${CANDS[@]} \
            -s $src_file \
            -r $ref_file \
            --batch_size $BATCH_SIZE \
            --metric bleurt
    done
done