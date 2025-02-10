#!/bin/bash

# Zielhost
TARGET="reuna.cl"

# Anzahl der Pings pro Lauf (86400 für 24 Stunden)
PACKET_COUNT=86400

# Anzahl der Wiederholungen (3 für 3 Tage)
REPEAT_COUNT=3

# Anzahl der Pings zwischen Zwischenspeicherungen (z.B. 100 Pings)
INTERVAL=100

# Ausgabe-Datei
OUTPUT_FILE="mtr_results.csv"

# Prüfen, ob mtr installiert ist
if ! command -v mtr &> /dev/null; then
    echo "mtr ist nicht installiert. Bitte installieren Sie es."
    exit 1
fi

# Kopfzeile einmal in die CSV-Datei schreiben, wenn die Datei nicht existiert
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Host,Loss%,Snt,Last,Avg,Best,Wrst,StDev" > $OUTPUT_FILE
fi

# Funktion, die mtr ausführt und die Ergebnisse zwischenspeichert
run_mtr() {
    local day=$1
    echo "Starte MTR zu $TARGET für $PACKET_COUNT Pings (Zwischenspeicherung nach $INTERVAL Pings)..."
    
    # Temporäre Datei für Zwischenergebnisse
    TEMP_FILE="mtr_temp_${day}.csv"

    for ((i = 0; i < $PACKET_COUNT; i += $INTERVAL)); do
        # Ersetze die TEMP-Datei mit den letzten 100 Pings
        mtr --report --report-cycles $INTERVAL --csv $TARGET | tail -n +2 | awk -v count=$(($i + INTERVAL)) 'BEGIN {FS=","; OFS=","} {print $1, $2, count, $4, $5, $6, $7, $8}' > $TEMP_FILE
        
        # Zeige Zwischenergebnisse in einem lesbaren Format
        echo "Zwischenergebnisse nach $(($i + INTERVAL)) Pings:"
        cat $TEMP_FILE
    done

    # Nachdem alle Pings abgeschlossen sind, füge die Ergebnisse zur Hauptdatei hinzu
    cat $TEMP_FILE >> $OUTPUT_FILE
    echo "Ergebnisse von Tag $day in $OUTPUT_FILE gespeichert."
}

# Hauptschleife für 3 Tage
for day in $(seq 1 $REPEAT_COUNT); do
    echo "Tag $day von $REPEAT_COUNT"
    run_mtr $day
    echo "Tag $day abgeschlossen."
done
