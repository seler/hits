#!/bin/bash

youtube-dl $2 -o 'input'

ffmpeg -i input.mkv -f lavfi -i color=c=black:s=1280x720:r=5 \
	-map 0 -c:v libx264 -c:a ac3 -y output.mp4 \
	-map 0  -vn -ab 256k -y output.mp3 \
	-map 0:1 -map 1:0 -crf 0 -c:v libx264 -t 30 -pix_fmt yuv420p -shortest -y black.mp4

rm input.mkv

mv output.mp4 "$1.mp4"
mv output.mp3 "$1.mp3"
mv black.mp4 "$1_black.mp3"
