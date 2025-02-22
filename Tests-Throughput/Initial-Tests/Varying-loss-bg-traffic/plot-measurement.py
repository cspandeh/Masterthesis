import json
import sys, os
from matplotlib import pyplot as plt

measurement = ""
UNIT = {'factor': 1e3, 'name': "KBytes"}

def main():
    global measurement
    if len(sys.argv) < 2:
        print("[Error] Datei namen angeben!")
        exit(1)
    if not os.path.exists(sys.argv[1]):
        print(f"[Error] Datei {sys.argv[1]} existier nicht!")
        exit(2)

    with open(sys.argv[1]) as f:
        try:
            json_input = json.load(f)
        except ValueError:
            print(f"[Error] Parsing json")
            exit(3)

        # parse file name
        _, algo, date, time = sys.argv[1].split(".")[0].split("_")
        measurement = f'{algo}_{date}_{time}'

        data = parse_data(json_input)
        plot_throughputs_windownsizes(*data)


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

def plot_throughputs_windownsizes(xs, throughputs, windowsizes, summary):
    global measurement, UNIT
    # unit conversion
    throughputs = list(map(lambda x: round(x/UNIT["factor"]), throughputs))
    windowsizes = list(map(lambda x: round(x/UNIT["factor"]), windowsizes))

    fig, ax1 = plt.subplots(figsize=(12,6))

    color="red"
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel(f'throughputs ({UNIT["name"]})', color=color)
    ax1.plot(xs, throughputs, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    offset_xlim = 2
    ax1.set_xlim(xs[1]-offset_xlim, xs[-1]+offset_xlim)

    ax2 = ax1.twinx()  # instantiate a second Axes that shares the same x-axis

    color="blue"
    ax2.set_ylabel(f'windowsizes ({UNIT["name"]})', color=color)
    ax2.plot(xs, windowsizes, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    sum_throughput = round(int(summary["throughput-bytes"])/1e6)
    fig.text(0.5, 0.06, f'Throughput overall: {sum_throughput} MBytes', 
        fontsize=13, 
        horizontalalignment="center",
        color="red"
    )
    sum_retransmits = round(int(summary["retransmits"]))
    fig.text(0.5, 0.02, f'Retransmits overall: {sum_retransmits}', 
        fontsize=13, 
        horizontalalignment="center",
        color="red"
    )
    fig.suptitle(measurement)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    fig.subplots_adjust(bottom=0.2)

    #plt.show()
    plt.savefig(f'plot_{measurement}.pdf')

    


if __name__ == "__main__":
    main()