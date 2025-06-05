# Sorting Algorithms Benchmarking Framework

A configurable benchmarking suite for classic sorting algorithms on large integer arrays. Designed for reproducible, high-precision performance analysis and comparison.

---

## Features

- **Controlled Data Generation**  
  - Generate arrays of arbitrary length (100 → 100 000) or value-range variability (10 → 1 000 000)  
  - Geometric spacing of sample sizes (100 samples)  
  - Deterministic seeding for full reproducibility  

- **Flexible Storage**  
  - Compress & store generated arrays on disk with ZPAQ + pickle  
  - Single-output file per sample set (`ArrayStorage.pick`)  
  - Automatic folder creation with timestamp  

- **Precision Timing & Statistics**  
  - Adaptive `minTime` based on clock resolution + relative error threshold  
  - Per-sample measurement of mean, median, IQR, outliers  
  - Support for asymmetric error bars (e.g. median ± IQR)  

- **Prebuilt Comparisons**  
  - QuickSort (2-way & 3-way), CountingSort, RadixSort  
  - Plug-in any additional `SortingAlgorithm`  

- **Visualization & Export**  
  - Interactive Plotly plots (linear & log-log scaling) that estimate the mean execution time with a 95 % confidence interval  
  - JSON export of raw & aggregated statistics  

---

## Final Report

The final report — including methodology, data analysis, and conclusions — is available at this page:

[https://londero-lorenzo.github.io/SortingAlgorithms/](https://londero-lorenzo.github.io/SortingAlgorithms/)

This page includes:

- A readable version of the report as PDF (Word-based)
- Interactive performance plots
- Access to source code and benchmarks

---

## Configuration

### Variability Settings (`Utils/ArraySettings.py`)
- `Variability.onLength` → arrays vary by length (constant value range)
- `Variability.onNumbers` → arrays vary by number of distinct elements (constant length)

### Timing Parameters
- `minTime` and relative error thresholds are defined in `Utils/TimingSettings.py`

---

## Notes

- All benchmarks now run **sequentially**; there is no multiprocessing support.
- Only one `.pick` file is generated per sample set (no chunking).
- Visualization is handled exclusively via **Plotly** (no Matplotlib).
- Interactive graphs are saved as standalone HTML files, suitable for GitHub Pages.
- Final plots estimate the mean execution time for each data point and include a **95 % confidence interval**.
- The interactive benchmark visualization is available at:  
  [https://londero-lorenzo.github.io/SortingAlgorithms/benchmarks.html](https://londero-lorenzo.github.io/SortingAlgorithms/assets/benchmarks.html)

---


## Installation

```bash
git clone https://github.com/londero-lorenzo/SortingAlgorithms.git
cd SortingAlgorithms
python3.11 setup.py
```

---

## Usage

1. **Generate Data**
    ```bash
    python create_sample_arrays.py
    ```
    - Generates compressed `.pick` files for each variability configuration.

2. **Run Benchmarks**
    ```bash
    (venv) python -m Benchmark.benchmark_runner --input <path_to_arrays> --output <output_folder> --algorithms <algorithm_names>
    ```
    - Executes all selected sorting algorithms on the generated arrays.
    - Results are saved as `.time` files under `Benchmark/ExecutionTimes/X_Variability`.

3. **Visualize Results**
    ```bash
    python view_benchmarks.py
    ```
    or more specifically:
    ```bash
    (venv) python -m Utils.graph_viewer --file <path_to_time_files> --auto --searchFolder <search_path> --output <output_html>
    ```
    - Generates interactive Plotly graphs (HTML) or opens them in a browser.
    - Supports both *length variability* and *number variability* modes.

4. **View Interactive Graph (on GitHub Pages)**
    - Open [https://londero-lorenzo.github.io/SortingAlgorithms/benchmarks.html](https://londero-lorenzo.github.io/SortingAlgorithms/benchmarks.html) to explore the interactive benchmark visualizations.

---

## Directory Structure
- Only relevant files and folders are shown below for clarity.
```
SortingAlgorithms/
├─ Array/
│  ├─ ArrayStorage/
│  │  ├─ N_variability/         # Length-based sample sets
│  │  └─ M_variability/         # Number-based sample sets
│  └─ ArraySettings.py          # Variability & storage config
│                               
├─ Benchmark/                   
│  ├─ ExecutionTimes/           
│  │  ├─ N_variability/         # .time files for length variability
│  │  └─ M_variability/         # .time files for number variability
│  ├─ Benchmark.ipynb	        # Notebook for interactive benchmark
│  ├─ benchmark_runner.py       # Sequential benchmark executor  **(TODO)**
│  └─ BenchmarkViewer.ipynb     # Notebook for result analysis
│                               
├─ Report/                      
│  └─ Charts/                   
│     ├─ N_variability/         # Plotly figures for length variability
│     └─ M_variability/         # Plotly figures for number variability
│                               
├─ Utils/                       
│  ├─ ArrayGenerator.py         # Data generation logic
│  ├─ ArraySettings.py          # Variability & file naming
│  ├─ ArrayStorageCompressor.py # Saving file using ZPAQ + pickle
│  ├─ SortingSettings.py        # minTime & error thresholds
│  └─ graph_viewer.py           # Interactive plot generator
│                               
├─ docs/                        
│  └─ benchmarks.html           # Interactive HTML visualization
│                               
├─ create_sample_arrays.py      # CLI for data generation
├─ setup.py                     # Installation & dependency setup
├─ start_jupyter.py				# Launching jupyter lab
├─ start_venv.py				# Launching virtual environment
├─ view_benchmarks.py	        # Launching graphical interaction
└─ README.md
```