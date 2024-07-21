import pyarrow.parquet as pq
from collections import defaultdict
from scipy.fft import fft
import numpy as np
import matplotlib.pyplot as plt

# Load the Parquet file
file_path = "C:\\Users\\DEV DAHIYA\\OneDrive\\Desktop\\sampledata.parquet"
table = pq.read_table(file_path)

# Extract relevant columns
source_ip = table['src_ip'].to_pylist()
first_seen = table['first_seen'].to_pylist()
dest_org = table['dst_org'].to_pylist()
dest_port = table['dst_port'].to_pylist()

# Ensure first_seen are sorted by source IP, destination org, destination port, and timestamp
combined = list(zip(source_ip, dest_org, dest_port, first_seen))
combined.sort(key=lambda x: (x[0], x[1], x[2], x[3]))

min_timestamp = min(float(ts) for ts in first_seen if float(ts) >= 0)

# Initialize variables
current_src_ip = None
current_dest_org = None
current_dest_port = None
previous_time = None
time_differences = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

# Iterate over the combined data
for src_ip, dst_org, dst_port, timestamp in combined:
    try:
        timestamp = float(timestamp)  # Ensure timestamp is a float
        if timestamp < 0:
            raise ValueError("Timestamp is negative")
        
        adjusted_timestamp = timestamp - min_timestamp

        # If the source IP, destination org, or destination port changes, reset the current values and previous time
        if src_ip != current_src_ip or dst_org != current_dest_org or dst_port != current_dest_port:
            current_src_ip = src_ip
            current_dest_org = dst_org
            current_dest_port = dst_port
            previous_time = adjusted_timestamp
        else:
            time_diff = adjusted_timestamp - previous_time
            time_differences[src_ip][dst_org][dst_port].append(time_diff)
            previous_time = adjusted_timestamp
    except (ValueError, OSError) as e:
        print(f"Skipping invalid timestamp {adjusted_timestamp} for src_ip {src_ip}, dst_org {dst_org}, dst_port {dst_port}: {e}")

# Bin data into 12 bins of 5 minutes each
bin_size = 10 * 60  # 5 minutes in seconds
num_bins = 6
binned_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0] * num_bins)))

for src_ip, dst_orgs in time_differences.items():
    for dst_org, dst_ports in dst_orgs.items():
        for dst_port, time_diffs in dst_ports.items():
            for time_diff in time_diffs:
                bin_index = int(time_diff // bin_size)
                if bin_index < num_bins:
                    binned_data[src_ip][dst_org][dst_port][bin_index] += 1

# # Print time differences
# for src_ip, dst_orgs in time_differences.items():
#     print(f"Source IP: {src_ip}")
#     for dst_org, dst_ports in dst_orgs.items():
#         print(f"  Destination Org: {dst_org}")
#         for dst_port, time_diffs in dst_ports.items():
#             print(f"    Destination Port: {dst_port}")
#             print(f"      Time Differences: {time_diffs}")
#     print()

# Compute FFT and plot the results
for src_ip, dst_orgs in binned_data.items():
    for dst_org, dst_ports in dst_orgs.items():
        for dst_port, bin_counts in dst_ports.items():
            if dst_org == "N/A":
                continue
            
            # Compute FFT
            f = fft(bin_counts)
            
            # Plot the results
            plt.figure(figsize=(10, 6))
            plt.plot(np.abs(f))
            plt.title(f"FFT for Source IP: {src_ip} visiting {dst_org} on port {dst_port}")
            plt.xlabel("Frequency")
            plt.ylabel("Magnitude")
            plt.grid(True)
            plt.show()
