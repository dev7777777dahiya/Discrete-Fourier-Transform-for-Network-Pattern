### Project Title: Network Data Pattern Detection

#### Description
This project, created by Dev Dahiya during an internship at a cyber-security company, aims to detect patterns in network data, primarily focusing on data received by a Wi-Fi router from local systems. The primary goal is to differentiate between real human activity and automated data pulls by the company or other systems. By analyzing these patterns, the project helps in identifying non-human inputs and miscellaneous sources of data traffic.

#### Features
- **Data Input:** Accepts Parquet files containing network data.
- **Data Processing:** Utilizes `pyarrow` for reading and processing the Parquet files.
- **Pattern Detection:** Computes time differences between network events and bins the data to identify recurring patterns.
- **FFT Analysis:** Uses `scipy.fft` to perform frequency analysis on the binned data.
- **Visualization:** Generates graphs using `matplotlib` to visualize the frequency components and help infer the nature of the network patterns.

#### How It Works
1. **Load Network Data:** The project reads a Parquet file containing network data, including source IP, destination organization, destination port, and timestamps of events.
2. **Process Timestamps:** Calculates the time differences between consecutive events for the same source IP, destination organization, and destination port.
3. **Bin Data:** Aggregates these time differences into bins of a specified size to identify patterns over time.
4. **FFT Analysis:** Performs Fast Fourier Transform (FFT) on the binned data to analyze the frequency components of the network traffic.
5. **Plot Results:** Visualizes the FFT results in a graph, highlighting the magnitude of different frequency components to help identify recurring patterns.

#### Installation
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/your-username/network-data-pattern-detection.git
   cd network-data-pattern-detection
   ```
2. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

#### Usage
1. **Prepare Your Data:**
   - Ensure your network data is in a Parquet file format.
   - Place the Parquet file in the project directory or provide the correct path.

2. **Run the Script:**
   ```sh
   python detect_patterns.py
   ```

3. **View the Results:**
   - The script will print the calculated time differences and display graphs of the FFT results.

#### Example
```python
import pyarrow.parquet as pq
from collections import defaultdict
from scipy.fft import fft
import numpy as np
import matplotlib.pyplot as plt

# Load the Parquet file
file_path = r"path_to_your_parquet_file.parquet"
table = pq.read_table(file_path)

# Extract relevant columns
source_ip = table['src_ip'].to_pylist()
first_seen = table['first_seen'].to_pylist()
dest_org = table['dst_org'].to_pylist()
dest_port = table['dst_port'].to_pylist()

# Process and sort data
combined = list(zip(source_ip, dest_org, dest_port, first_seen))
combined.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
min_timestamp = min(float(ts) for ts in first_seen if float(ts) >= 0)

# Initialize time differences
time_differences = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
current_src_ip, current_dest_org, current_dest_port, previous_time = None, None, None, None

# Calculate time differences
for src_ip, dst_org, dst_port, timestamp in combined:
    timestamp = float(timestamp)
    adjusted_timestamp = timestamp - min_timestamp
    if src_ip != current_src_ip or dst_org != current_dest_org or dst_port != current_dest_port:
        current_src_ip, current_dest_org, current_dest_port, previous_time = src_ip, dst_org, dst_port, adjusted_timestamp
    else:
        time_diff = adjusted_timestamp - previous_time
        time_differences[src_ip][dst_org][dst_port].append(time_diff)
        previous_time = adjusted_timestamp

# Print time differences
for src_ip, dst_orgs in time_differences.items():
    print(f"Source IP: {src_ip}")
    for dst_org, dst_ports in dst_orgs.items():
        print(f"  Destination Org: {dst_org}")
        for dst_port, time_diffs in dst_ports.items():
            print(f"    Destination Port: {dst_port}")
            print(f"      Time Differences: {time_diffs}")
    print()

# FFT and plot results
for src_ip, dst_orgs in time_differences.items():
    for dst_org, dst_ports in dst_orgs.items():
        for dst_port, time_diffs in dst_ports.items():
            if dst_org == "N/A":
                continue
            bin_size, num_bins = 10 * 60, 6
            bin_counts = [0] * num_bins
            for time_diff in time_diffs:
                bin_index = int(time_diff // bin_size)
                if bin_index < num_bins:
                    bin_counts[bin_index] += 1
            f = fft(bin_counts)
            plt.figure(figsize=(10, 6))
            plt.plot(np.abs(f))
            plt.title(f"FFT for Source IP: {src_ip} visiting {dst_org} on port {dst_port}")
            plt.xlabel("Frequency")
            plt.ylabel("Magnitude")
            plt.grid(True)
            plt.show()
```

#### Future Enhancements
- **Automated Pattern Recognition:** Implement machine learning algorithms to automatically classify human vs. non-human activity.
- **Real-Time Analysis:** Extend the project to support real-time data processing and pattern detection.
- **Advanced Visualization:** Add more sophisticated visualizations and dashboards for better insights.

#### Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

#### License
This project is licensed under the MIT License. See the LICENSE file for details.

#### Acknowledgments
Special thanks to the cyber-security company for the opportunity to work on this project and for providing the necessary resources and data.
