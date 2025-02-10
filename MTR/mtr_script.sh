#!/bin/bash

# Zielhost
TARGET="reuna.cl"

# Anzahl der Pings pro Lauf (86400 für 24 Stunden)
PACKET_COUNT=86400

# Anzahl der Wiederholungen (3 für 3 Tage)
REPEAT_COUNT=3

# Ausgabe-Datei
OUTPUT_FILE="mtr_resultsNov.csv"

# Prüfen, ob mtr installiert ist
if ! command -v mtr &> /dev/null; then
    echo "mtr ist nicht installiert. Bitte installieren Sie es."
    exit 1
fi

# Kopfzeile einmal in die CSV-Datei schreiben, wenn die Datei nicht existiert
if [ ! -f "$OUTPUT_FILE" ]; then
    mtr --report --report-cycles 1 --csv $TARGET | head -n 1 > "$OUTPUT_FILE"
fi

# Funktion, die mtr ausführt und die Ergebnisse zwischenspeichert
run_mtr() {
    local day=$1
    echo "Starte MTR zu $TARGET für $PACKET_COUNT Pings..."

    # MTR-Optionen
    mtr --report --report-cycles $PACKET_COUNT --csv $TARGET >> "$OUTPUT_FILE" &

    # MTR-Prozess-ID speichern, um ihn später überwachen zu können
    MTR_PID=$!

    # Warte darauf, dass der MTR-Prozess beendet wird
    wait $MTR_PID

    # Ausgabe von Tag und Bestätigung, dass Ergebnisse gespeichert wurden
    echo "Ergebnisse von Tag $day in $OUTPUT_FILE gespeichert."
}

# Hauptschleife für 3 Tage
for day in $(seq 1 $REPEAT_COUNT); do
    echo "Tag $day von $REPEAT_COUNT"
    run_mtr $day
    echo "Tag $day abgeschlossen."
done

