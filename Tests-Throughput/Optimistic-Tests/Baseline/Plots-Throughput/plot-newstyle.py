import json
import sys, os
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

        filename = os.path.basename(sys.argv[1])
        # Expecting filename format: algo_test_YYYYMMDD_HHMM.json
        parts = filename.split(".")[0].split("_")
        if len(parts) < 4:
            print("[Error] Dateiname entspricht nicht dem erwarteten Format!")
            exit(4)
        algo = parts[0]
        date_str = parts[2]
        time_str = parts[3]
        title_main = f"{algo.upper()} Test"  # Main title
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
    # Convert from bytes to KBytes
    throughputs = [round(x / UNIT["factor"]) for x in throughputs]
    windowsizes = [round(x / UNIT["factor"]) for x in windowsizes]
    
    # Filter data to include only values starting from the 10th second
#    #start_index = next(i for i, x in enumerate(xs) if x >= 10)
#    #xs = xs[start_index:]
#    #throughputs = throughputs[start_index:]
#    #windowsizes = windowsizes[start_index:]
    
    # Create figure and primary axis
    fig, ax1 = plt.subplots(figsize=(24,8), dpi=300)
    
    # Customize plot appearance
    plt.rcParams.update({
        "axes.titlesize": 30,
        "axes.labelsize": 28,
        "xtick.labelsize": 23,
        "ytick.labelsize": 23,
        "legend.fontsize": 23,
        "figure.titlesize": 33,
        "lines.linewidth": 1.5,
        "lines.markersize": 8,
        "axes.grid": True,
        "grid.color": "grey",
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
    })
    
    # Plot throughput on the left y-axis
    color1 = "red"
    ax1.set_xlabel('Time (s)', fontsize=28)
    ax1.set_ylabel(f'Throughput ({UNIT["name"]})', fontsize=28, color=color1, labelpad=20)
    ax1.plot(xs, throughputs, color=color1, linestyle='-', linewidth=1.5, label='Throughput')
    ax1.tick_params(axis='x', labelsize=23, pad=10)
    ax1.tick_params(axis='y', labelcolor=color1, labelsize=23, pad=10)
    offset_xlim = 2
    ax1.set_xlim(xs[0]-offset_xlim, xs[-1]+offset_xlim)
   # ax1.xaxis.set_major_locator(AutoLocator())
    
    # Plot CWND on the right y-axis
    ax2 = ax1.twinx()
    color2 = "blue"
    ax2.set_ylabel(f'CWND ({UNIT["name"]})', fontsize=28, color=color2, labelpad=20)
    ax2.plot(xs, windowsizes, color=color2, linestyle='-', linewidth=1.5, label='CWND')
    ax2.tick_params(axis='y', labelcolor=color2, labelsize=23, pad=10)
    #ax2.xaxis.set_major_locator(AutoLocator())
    
    # Add axis lines
#    ax1.axhline(0, color='black', linewidth=1)
#    ax1.axvline(0, color='black', linewidth=1)
#    ax2.axhline(0, color='black', linewidth=1)
#    ax2.axvline(0, color='black', linewidth=1)
    
    # Remove the top spine
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    
    # Add right y-axis line
#    ax2.spines['right'].set_color('black')
#    ax2.spines['right'].set_linewidth(1)
    
    # Place custom legend outside the plot area to avoid overlap
    line1 = mlines.Line2D([], [], color=color1, linestyle='-', linewidth=1.5, label='Throughput')
    line2 = mlines.Line2D([], [], color=color2, linestyle='-', linewidth=1.5, label='CWND')
    legend = ax1.legend(handles=[line1, line2], loc='upper center', bbox_to_anchor=(0.5, 1.2), fontsize=28, ncol=2, frameon=False)
    # Force both axes to start at 0.
    ax1.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)
    
    # Adjust y-axis limits based on data range
    ax1.set_ylim(0, max(throughputs) * 1.1)
    ax2.set_ylim(0, max(windowsizes) * 1.1)
    
    # Adjust overall layout to leave more space at the top for title and subtitle.
    fig.tight_layout(rect=[0, 0.1, 1, 1])
    
    # Position the title and subtitle so they don't overlap.
    # Adjust y positions (normalized coordinates) as needed.
    #fig.suptitle(title_main, fontsize=30, y=0.98)
    #fig.text(0.5, 0.88, title_sub, fontsize=25, horizontalalignment="center")
    
    # Add bottom annotations with extra spacing.
    bottom_gap = 0.05
    sum_throughput = round(int(summary["throughput-bytes"]) / 1e6)
    fig.text(0.18, bottom_gap, f'Throughput overall: {sum_throughput} MBytes', fontsize=28,
             horizontalalignment="center", color="black")
    sum_retransmits = round(int(summary["retransmits"]))
    fig.text(0.82, bottom_gap, f'Retransmissions overall: {sum_retransmits}', fontsize=28,
             horizontalalignment="center", color="black")
    if diags_data.get("diags") and len(diags_data["diags"]) > 0:
        sum_receiver = round(int(diags_data["diags"][0]["end"]["streams"][0]["receiver"]["bytes"]) / 1e6)
        fig.text(0.5, bottom_gap, f'Receiver throughput: {sum_receiver} MBytes', fontsize=28,
                 horizontalalignment="center", color="black")
    
    plt.savefig(f'plot_{measurement}.pdf')
    plt.show()

if __name__ == "__main__":
    main()
