#!/bin/env sh
find ../../src . -type f | grep -F ".py" | grep -v "__pycache" | xargs cat | sed '/^$/d' > out/code.txt
wordcloud_cli --text out/code.txt --mask maerklin.jpg --colormask maerklin.jpg --imagefile out/wordcloud.png --stopwords stopwords.txt --no_collocations
