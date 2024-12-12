
#!/bin/bash


USER_AGENTS=(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36"
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
)


URL="https://allegro.pl/oferta/teclast-maly-tablet-8-p85t-4-64gb-wifi-bluetooth-5-2-android-ladowarka-15383295031"
OUTPUT_FILE="../dummy_data/product.html"
wget --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36" \
       --quiet \
       --output-document="$OUTPUT_FILE" \
       "https://allegro.pl/oferta/teclast-maly-tablet-8-p85t-4-64gb-wifi-bluetooth-5-2-android-ladowarka-15383295031"

  if [ $? -eq 0 ]; then
      echo "Zawartość strony została zapisana do pliku $OUTPUT_FILE"
  else
      echo "Błąd podczas pobierania strony!"
  fi
