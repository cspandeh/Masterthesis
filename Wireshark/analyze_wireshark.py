import pandas as pd
import sys

# Prüfen, ob eine Datei angegeben wurde
if len(sys.argv) != 2:
    print("Usage: python3 analyze_wireshark.py <path_to_csv_file>")
    sys.exit(1)

# Datei von den Kommandozeilenargumenten einlesen
file_name = sys.argv[1]

try:
    # Wireshark-CSV-Datei laden
    data = pd.read_csv(file_name)

    # Gesamtanzahl der Pakete
    total_packets = len(data)

    # Pakete mit TCP Retransmissions
    retransmission_packets = data[
        data['Info'].str.contains("Retransmission", na=False)
    ]
    retransmission_count = len(retransmission_packets)

    # Pakete mit ACK Lost Segments
    ack_lost_packets = data[
        data['Info'].str.contains("TCP Previous segment not captured", na=False)
    ]
    ack_lost_count = len(ack_lost_packets)

    # Gesamtzahl verlorener Pakete
    total_lost_count = retransmission_count + ack_lost_count

    # Paketverlust in Prozent berechnen
    packet_loss_percentage = (total_lost_count / total_packets) * 100

    # Durchsatzberechnung
    # Dauer der Capture-Session
    duration = data['Time'].iloc[-1] - data['Time'].iloc[0]  # Dauer in Sekunden

    # Gesamtdaten in Bytes
    total_bytes = data['Length'].sum()

    # Durchsatz in Mbps
    throughput_mbps = (total_bytes * 8) / (duration * 1_000_000)  # 1 Byte = 8 Bits

    # Ergebnisse ausgeben
    print(f"Analyzed file: {file_name}")
    print(f"Total packets: {total_packets}")
    print(f"Retransmissions: {retransmission_count}")
    print(f"ACKed Lost Segments: {ack_lost_count}")
    print(f"Total lost packets: {total_lost_count}")
    print(f"Packet loss percentage: {packet_loss_percentage:.2f}%")
    print(f"Total data transferred: {total_bytes} Bytes")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Throughput: {throughput_mbps:.2f} Mbps")

except Exception as e:
    print(f"Error processing file {file_name}: {e}")

