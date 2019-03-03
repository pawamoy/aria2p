#!/usr/bin/env bash

cat docs/spelling_wordlist.txt > docs/tmpspell.txt
grep '<w>' .idea/dictionaries/pawamoy.xml | sed -r 's/ *<w>(.*)<\/w>/\1/' >> docs/tmpspell.txt
sort -u docs/tmpspell.txt > docs/spelling_wordlist.txt
rm docs/tmpspell.txt
