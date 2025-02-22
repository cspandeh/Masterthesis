import json
import sys, os, re, io
from matplotlib import pyplot as plt
import matplotlib.lines as mlines

measurement = ""
UNIT = {'factor': 1e3, 'name': "KBytes"}

def main():
    global measurement
    if len(sys.argv) < 2:
        print("[Error] Bitte Dateinamen angeben!")
        exit(1)
    if not os.path.exists(sys.argv[1]):
        print(f"[Error] Datei {sys.argv[1]} existiert nicht!")
        exit(2)

    with open(sys.argv[1]) as f:
        try:
            json_input = json.load(f)
        except ValueError:
            print("[Error] Parsing JSON fehlgeschlagen")
            exit(3)

        # Expecting filename format: algo_test_YYYYMMDD_HHMM.json
        parts = sys.argv[1].split(".")[0].split("_")
        if len(parts) < 4:
            print("[Error] Dateiname entspricht nicht dem erwarteten Format!")
            exit(4)
        algo = parts[0]
        date_str = parts[2]
        time_str = parts[3]
        # Main title: "CCA TEST" (uppercase)
        title_main = f"{algo.upper()} Test\n"
        # Format date from YYYYMMDD to DD.MM.YYYY and time from HHMM to HH:MM
        year = date_str[0:4]
        month = date_str[4:6]
        day = date_str[6:8]
        formatted_date = f"{day}.{month}.{year}"
        formatted_time = f"{time_str[:2]}:{time_str[2:]}"
        title_sub = f"{formatted_date} {formatted_time}"
        measurement = f"{algo}_{date_str}_{time_str}"

        data = parse_data(json_input)
        diags_data = parse_diags(json_input)
        plot_throughputs_windownsizes(*data, diags_data, title_main, title_sub)

def parse_diags(input):
    diags_str = input.get("diags", "")
    start = diags_str.find('{')
    end = diags_str.rfind('}')
    if start == -1 or end == -1:
        print("No JSON object found in diags.")
        return {"diags": []}
    json_str = diags_str[start:end+1]
    try:
        parsed = json.loads(json_str)
    except Exception as e:
        print("Error parsing diag JSON:", e)
        return {"diags": []}
    return {"diags": [parsed]}

def parse_data(input):
    xs = []
    throughputs = []
    windowsizes = []
    for interval in input["intervals"]:
        data = interval["streams"][0]
        xs.append(int(data["end"]))
        throughputs.append(data["throughput-bytes"])
        windowsizes.append(data["tcp-window-size"])
    summary = input["summary"]["summary"]
    return xs, throughputs, windowsizes, summary

def plot_throughputs_windownsizes(xs, throughputs, windowsizes, summary, diags_data, title_main, title_sub):
    global measurement, UNIT
    # Unit conversion: from bytes to KBytes
    throughputs = list(map(lambda x: round(x / UNIT["factor"]), throughputs))
    windowsizes = list(map(lambda x: round(x / UNIT["factor"]), windowsizes))
    
    # Use the seaborn style available on your system
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Increase figure width and resolution
    fig, ax1 = plt.subplots(figsize=(20,7), dpi=300)
    
    # Plot throughput on left y-axis (plain line)
    color1 = "red"
    ax1.set_xlabel('Time (s)', fontsize=25)
    ax1.set_ylabel(f'Throughput ({UNIT["name"]})', fontsize=25, color=color1)
    ax1.plot(xs, throughputs, color=color1, linestyle='-', linewidth=1.5, label='Throughput')
    ax1.tick_params(axis='y', labelcolor=color1, labelsize=20)
    ax1.tick_params(axis='x', labelsize=20)
    offset_xlim = 2
    ax1.set_xlim(xs[0]-offset_xlim, xs[-1]+offset_xlim)
    
    # Plot congestion window size on right y-axis (plain line)
    ax2 = ax1.twinx()
    color2 = "blue"
    ax2.set_ylabel(f'CWND ({UNIT["name"]})', fontsize=25, color=color2)
    ax2.plot(xs, windowsizes, color=color2, linestyle='-', linewidth=1.5, label='CWND')
    ax2.tick_params(axis='y', labelcolor=color2, labelsize=20)
    
    # Create a custom legend positioned to avoid data overlap
    line1 = mlines.Line2D([], [], color=color1, linestyle='-', linewidth=1.5, label='Throughput')
    line2 = mlines.Line2D([], [], color=color2, linestyle='-', linewidth=1.5, label='CWND')
    ax1.legend(handles=[line1, line2], loc='upper left', fontsize=25, bbox_to_anchor=(0.02, 0.98))
    
    # Adjust annotation positions to avoid overlapping with x-axis labels
    sum_throughput = round(int(summary["throughput-bytes"]) / 1e6)
    fig.text(0.15, 0.04, f'Throughput overall: {sum_throughput} MBytes', fontsize=25, horizontalalignment="center", color="darkblue")
    sum_retransmits = round(int(summary["retransmits"]))
    fig.text(0.85, 0.04, f'Retransmissions overall: {sum_retransmits}', fontsize=25, horizontalalignment="center", color="darkblue")
    if diags_data.get("diags") and len(diags_data["diags"]) > 0:
        sum_receiver = round(int(diags_data["diags"][0]["end"]["streams"][0]["receiver"]["bytes"]) / 1e6)
        fig.text(0.5, 0.04, f'Receiver throughput: {sum_receiver} MBytes', fontsize=25, horizontalalignment="center", color="darkblue")
    
    # Set main title and subtitle with adjusted spacing
    fig.suptitle(title_main, fontsize=25)
    fig.text(0.5, 0.9, title_sub, fontsize=25, horizontalalignment="center")
    
    fig.tight_layout()
    # Increase bottom margin to provide extra space for annotations
    fig.subplots_adjust(bottom=0.18)

    plt.savefig(f'plot_{measurement}.pdf')
    plt.show()

if __name__ == "__main__":
    main()
