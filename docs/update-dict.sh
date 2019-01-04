#!/usr/bin/env bash
grep '<w>' ../.idea/dictionaries/pawamoy.xml | sed -r 's/ *<w>(.*)<\/w>/\1/' > spelling_wordlist.txt
