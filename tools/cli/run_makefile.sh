#!/usr/bin/env bash
source "$(dirname "$0")/make_describe.sh"

# Список alias'ов
declare -A ALIASES=(
  [t]="test"
  [l]="lint"
  [s]="setup"
  [m]="migrate"
  [b]="bootstrap"
  [d]="doctor"
  [r]="run"
  [z]="zen"
)

# Получение всех целей Makefile
targets=$(make -qp | awk -F':' '/^[a-zA-Z0-9\-_]+:/ {print $1}' | sort | uniq)

# Вывод alias'ов
echo "🔍 Выберите alias или команду:"
for alias in "${!ALIASES[@]}"; do
  echo "• $alias → ${ALIASES[$alias]} → $(describe_target "${ALIASES[$alias]}")"
done
echo "• или введи полную команду (например: deploy)"

# Ввод
read -rp "> " input

# Преобразование alias → цель
target="${ALIASES[$input]:-$input}"

# Проверка цели
if echo "$targets" | grep -q "^$target$"; then
  echo "👉 $(describe_target "$target")"
  make "$target"
else
  echo "❌ Цель '$input' не найдена"
  echo "📦 Доступные цели:"
  for t in $targets; do
    echo "• $t → $(describe_target "$t")"
  done
fi
