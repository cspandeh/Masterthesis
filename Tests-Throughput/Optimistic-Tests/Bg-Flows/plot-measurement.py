import json
import sys, os, re, io
from matplotlib import pyplot as plt

measurement = ""
UNIT = {'factor': 1e3, 'name': "KBytes"}

def main():
    global measurement
    if len(sys.argv) < 2:
        print("[Error] Datei namen angeben!")
        exit(1)
    if not os.path.exists(sys.argv[1]):
        print(f"[Error] Datei {sys.argv[1]} existiert nicht!")
        exit(2)

    with open(sys.argv[1]) as f:
        try:
            json_input = json.load(f)
        except ValueError:
            print(f"[Error] Parsing json")
            exit(3)

        # parse file name
        algo, _, time, date = sys.argv[1].split(".")[0].split("_")
        measurement = f'{algo}_{date}_{time}'

        data = parse_data(json_input)
        diags_data = parse_diags(json_input)
        plot_throughputs_windownsizes(*data, diags_data)


#def parse_diags(input):
#    a = json.dumps(input["diags"]).strip().replace('\\n', '\n').replace('\\"', '"')
#    a = re.sub(r"Participant \d\:\n\/usr\/bin\/iperf3.*\n\n", "", a)
#    a = re.sub(r"\}\n\{", "},\n{", a)
#    b = '{"diags" :[' + a[1:-1] + ']}'
#    return json.loads(b)
def parse_diags(input):
    diags_str = input.get("diags", "")
    # Find the first '{' and the last '}'
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
    # Return the parsed JSON object in a list (so downstream code works)
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

def plot_throughputs_windownsizes(xs, throughputs, windowsizes, summary, diags_data):
       # Debug print to inspect the diags data
#    print("Type of diags_data:", type(diags_data))
#    print("Type of diags_data['diags']:", type(diags_data.get("diags")))
#    if diags_data.get("diags"):
#        print("Type of first entry:", type(diags_data["diags"][0]))
#        print("First entry content:", diags_data["diags"][0])
   
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
    fig.text(0.5, 0.1, f'Throughput overall: {sum_throughput} MBytes', 
        fontsize=13, 
        horizontalalignment="center",
        color="red"
    )
    sum_retransmits = round(int(summary["retransmits"]))
    fig.text(0.5, 0.06, f'Retransmits overall: {sum_retransmits}', 
        fontsize=13, 
        horizontalalignment="center",
        color="red"
    )
    sum_receiver = round(int(diags_data["diags"][0]["end"]["streams"][0]["receiver"]["bytes"])/1e6)
    fig.text(0.5, 0.02, f'Receiver throughput: {sum_receiver} MBytes', 
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
