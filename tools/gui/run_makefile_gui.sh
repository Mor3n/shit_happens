#!/usr/bin/env bash
source "$(dirname "$0")/../cli/make_describe.sh"

detect_gui() {
  for tool in zenity yad dialog; do
    if command -v "$tool" &>/dev/null; then echo "$tool"; return; fi
  done
  echo "none"
}

GUI=$(detect_gui)

if [ "$GUI" == "none" ]; then
  echo "❌ GUI не найден. Переход к CLI..."
  bash "$(dirname "$0")/../cli/run_makefile.sh"
  exit 0
fi

read -p "🖥️ Обнаружено GUI ($GUI). Использовать его? [Y/n] " confirm
if [[ "$confirm" =~ ^[Nn] ]]; then
  echo "🔁 Переход к CLI..."
  bash "$(dirname "$0")/../cli/run_makefile.sh"
  exit 0
fi

source .env 2>/dev/null
echo "📦 Окружение: BOT_TOKEN=${BOT_TOKEN:-не задан}, DB_URI=${DB_URI:-не задан}"

TARGETS=$(make -qp | awk -F':' '/^[a-zA-Z0-9\-_]+:/ {print $1}' | sort | uniq)
OPTIONS=""
for t in $TARGETS; do
  desc=$(describe_target "$t")
  OPTIONS+="$t:$desc\n"
done

case "$GUI" in
  zenity)
    CHOICE=$(echo -e "$OPTIONS" | zenity --list --title="Makefile GUI" --column="Цель" --column="Описание" --width=600 --height=400)
    ;;
  yad)
    CHOICE=$(echo -e "$OPTIONS" | yad --list --title="Makefile GUI" --column="Цель" --column="Описание" --width=600 --height=400)
    ;;
  dialog)
    CHOICE=$(dialog --menu "Выберите цель Makefile" 20 60 10 $(echo -e "$OPTIONS" | awk -F':' '{print $1 " \"" $2 "\""}') 3>&1 1>&2 2>&3)
    ;;
esac

if [ -z "$CHOICE" ]; then
  echo "❌ Ничего не выбрано. Выход."
  exit 1
fi

echo "🚀 Запуск: make $CHOICE"
make "$CHOICE"
