#!/bin/sh
#出力設定
amixer -c tlv320aic3104so sset 'PCM' 100%
amixer -c tlv320aic3104so sset 'HP DAC' 75%
amixer -c tlv320aic3104so sset 'HP' 0
#入力設定
amixer -c tlv320aic3104so sset 'Left Line1L Mux' 'single-ended'
amixer -c tlv320aic3104so sset 'Left PGA Mixer Line1L' on
amixer -c tlv320aic3104so sset 'PGA' 60%
