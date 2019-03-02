#!/usr/bin/env bash
dups="$(grep -Eo 'port=[0-9]{4}' tests/test_* | cut -d: -f2 | sort | uniq -c | grep -v '1 ')"

if [ -n "${dups}" ]; then
  echo "${dups}" | while read -r dup; do
    port="${dup#*=}"
    num=${dup% *}
    echo "-- Port ${port} used" ${num} "times:" >&2
    grep -n --color=auto "port=${port}" tests/test_*
    echo
  done
  exit 1
fi

exit 0
