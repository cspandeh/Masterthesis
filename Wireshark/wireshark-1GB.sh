#!/bin/bash

# Ziel-URL und Dateien
TARGET_URL="https://lg.reuna.cl/100MB.test"
PCAP_FILE="tcp_capture.pcap"
CSV_FILE="tcp_capture.csv"
DOWNLOAD_COUNT=10

# Prüfen, ob tshark installiert ist
if ! command -v tshark &> /dev/null; then
    echo "tshark ist nicht installiert. Bitte installieren und erneut versuchen."
    exit 1
fi

# Prüfen, ob wget installiert ist
if ! command -v wget &> /dev/null; then
    echo "wget ist nicht installiert. Bitte installieren und erneut versuchen."
    exit 1
fi

# Netzwerk-Schnittstelle bestimmen
INTERFACE=$(ip -o -4 route show to default | awk '{print $5}')

if [ -z "$INTERFACE" ]; then
    echo "Konnte keine Standard-Netzwerk-Schnittstelle ermitteln."
    exit 1
fi

# Starte Paketaufzeichnung mit Filter (nur TCP)
echo "Starte Paketaufzeichnung (nur TCP) auf Schnittstelle $INTERFACE..."
tshark -i "$INTERFACE" -f "tcp" -w "$PCAP_FILE" &
TSHARK_PID=$!

# Warten, bis tshark vollständig läuft
sleep 5

# 10-maliger Download
echo "Starte Downloads..."
for i in $(seq 1 $DOWNLOAD_COUNT); do
    echo "Download $i von $DOWNLOAD_COUNT..."
    wget -q "$TARGET_URL" -O /dev/null
done

# Beenden der Paketaufzeichnung
echo "Beende Paketaufzeichnung..."
kill "$TSHARK_PID"
wait "$TSHARK_PID"

# Konvertieren der PCAP-Datei in CSV
echo "Konvertiere PCAP-Datei in CSV (nur TCP-Pakete)..."
tshark -r "$PCAP_FILE" -Y "tcp" -T fields -E separator=, -E quote=d -E header=y \
       -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e _ws.col.Protocol \
       -e frame.len -e _ws.col.Info > "$CSV_FILE"

# Sicherstellen, dass die Spaltennamen für die Ausgabe stimmen
sed -i '1s/frame.number/No./; 1s/frame.time_relative/Time/; 1s/ip.src/Source/; 1s/ip.dst/Destination/; 1s/_ws.col.Protocol/Protocol/; 1s/frame.len/Length/; 1s/_ws.col.Info/Info/' "$CSV_FILE"

# Ergebnisse anzeigen
echo "Paketaufzeichnung abgeschlossen."
echo "PCAP-Datei gespeichert unter: $PCAP_FILE"
echo "CSV-Datei gespeichert unter: $CSV_FILE"
