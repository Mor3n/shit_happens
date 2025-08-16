#!/usr/bin/env bash
source "$(dirname "$0")/make_describe.sh"
echo "# 📘 Makefile Targets" > README.md
echo "" >> README.md
targets=$(make -qp | awk -F':' '/^[a-zA-Z0-9\-_]+:/ {print $1}' | sort | uniq)
for t in $targets; do
  echo "- \`$t\`: $(describe_target $t)" >> README.md
done
echo "✅ README.md обновлён"
