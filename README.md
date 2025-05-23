# Sorting Algorithms Benchmarking Framework

A configurable, parallel benchmarking suite for classic sorting algorithms on large integer arrays. Designed for reproducible, high-precision performance analysis and comparison.

---

## Features

- **Controlled Data Generation**  
  - Generate arrays of arbitrary length (100 → 100 000) or value-range variability (10 → 1 000 000)  
  - Geometric spacing of sample sizes (100 samples)  
  - Deterministic seeding for full reproducibility  

- **Flexible Storage & Chunking**  
  - Compress & store generated arrays on disk with ZPAQ + pickle  
  - Uniform “chunking” of sample sets by total element count  
  - Automatic session-folder creation with timestamp  

- **Robust Multiprocessing Engine**  
  - Configurable pool size (`SAFE_PROCESS_COUNT` vs. `FULL_THROTTLE_PROCESS_COUNT` vs. `CUSTOM`)  
  - “Guard file” mechanism to avoid concurrent runs and support manual abort  
  - High-priority (“real-time”) child processes via `psutil`  
  - Callback & error-callback hooks for per-job handling  

- **Precision Timing & Statistics**  
  - Adaptive `minTime` based on clock resolution + relative error threshold  
  - Per-sample measurement of mean, median, IQR, outliers  
  - Support for asymmetric error bars (e.g. median ± IQR)  

- **Prebuilt Comparisons**  
  - QuickSort (2-way & 3-way), CountingSort, RadixSort  
  - Plug-in any additional `SortingAlgorithm`  

- **Visualization & Export**  
  - Scatter plots with error bars (Matplotlib / Plotly)  
  - Linear & log-log scaling  
  - JSON export of raw & aggregated statistics  

---

## Installation

```bash
git clone https://github.com/londero-lorenzo/SortingAlgorithms.git
cd SortingAlgorithms
python3.11 setup.py