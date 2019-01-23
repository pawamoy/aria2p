#!/usr/bin/env bash
jinja2 --format=json scripts/templates/README.md <(./scripts/gen-readme-usage.py)
