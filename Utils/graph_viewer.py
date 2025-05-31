import os
import argparse
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from Utils import ArrayStorageCompressor
from Utils.ArraySettings import Variability
import fnmatch
from copy import deepcopy
import sys

def copy_layout_settings(source_layout, target_keys):
    return source_layout.to_plotly_json()

def combine(figures):
    assert len(figures) % 2 == 0, f"Unpair figures detected. Found:\n{figures}"
    assert len(figures) <= 4, f"Expected maximum 4 images, got {len(figures)}"
    
    default_layout = figures[0]["layout"]
    fig_combined = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.10,
        subplot_titles=("Array Length", "Number Variability"),
    )
    
    positions = {
        Variability.onLength.value["nice_name"]: {
            "linear":       (1, 1),
            "logaritmic":   (1, 1)
            },
        Variability.onNumbers.value["nice_name"]:{
            "linear":       (1, 2),
            "logaritmic":   (1, 2)
            }
    }
    
    visible_by_default = [True, False, True, False]
    


    for idx, single_fig in enumerate(figures):
        meta = single_fig["layout"]["meta"]
        row, col = positions[meta["variability"]][meta["scale"]]
        show_flag = visible_by_default[idx]
        for trace in single_fig.data:
            trace.visible = show_flag
            fig_combined.add_trace(trace, row=row, col=col)
            
            
    fig_combined.update_layout(
        **copy_layout_settings(figures[0]["layout"], ["font"])
    )

    for col in range(2):
        fig_combined.update_yaxes(
            title_text="Time (s)",
            row=1,
            col=col+1,
        )
        

    fig_combined.update_xaxes(
        title_text="Array length",
        type="linear",
        row=1,
        col=1,
    )
    fig_combined.update_xaxes(
        title_text="Variance",
        type="linear",
        row=1,
        col=2,
    )
    
    n_traces_per_fig = [(f["layout"]["meta"]["scale"], len(f.data)) for f in figures]
    
    vis_linear = []
    vis_log = []
    for scale, count in n_traces_per_fig:
        if scale == "linear":
            vis_linear += [True]  * count
            vis_log    += [False] * count
        else:
            vis_linear += [False] * count
            vis_log    += [True]  * count


    button_linear = dict(
        label="Linear scale",
        method="update",
        args=[
            {"visible": vis_linear},
            {
                "xaxis":  {"type": "linear", "title": "Array length"},
                "xaxis2": {"type": "linear", "title": "Number variance"},
            },
        ],
    )

    button_log = dict(
        label="Logaritmic scale",
        method="update",
        args=[
            {"visible": vis_log},
            {
                "xaxis":  {"type": "log", "title": "Array length (log)"},
                "xaxis2": {"type": "log", "title": "Number variance (log)"},
            },
        ],
    )
    
    
    fig_combined.update_xaxes(
        hoverformat = ".5s"
    )
    
    fig_combined.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.55,
                y=-0.1,
                showactive=True,
                buttons=[button_linear, button_log],
            )
        ],
        title = dict(
            subtitle=dict(
                text = "Run times grouped by sorting algorithm.",
            ),
        ),
        legend = dict(
            orientation="h",
            yanchor="bottom",
            xanchor="center",
            y=-0.2,
            x=0.5,
        ),
        margin = dict(l=80, r=30, t=100, b=80),
        height = 1920/2,
        width = 1080*2,
    )
    
    return fig_combined





def find_file(filename, search_root):
    matches = []

    for root, dirs, files in os.walk(search_root):
        for file in files:
            if fnmatch.fnmatch(file, filename):
                full_path = os.path.join(root, file)
                matches.append(full_path)
    return matches
    


def show_figures(figures):
    fig = combine(figures)
    fig.show()
    
def write_figures(figures, output, width = 1500, height = 900, scale = 4):
    fig = combine(figures)
    if ".html" in output:
        fig.write_html(output, width = width, height = height, scale = scale)
    else:
        fig.write_image(output , width = width, height = height, scale = scale)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Visualize time graph")
    parser.add_argument("-f", "--file", help="Target file path, must be a plotly.graph_objects.Figure object.", type=str, required=True)
    parser.add_argument("-o", "--output", help="Folder where the chunks array will be generetad.", type=str, default= None)
    parser.add_argument("-a", "--auto", help="Automatically generate the arrays by searching for the target file.", action='store_true')
    parser.add_argument("-s", "--searchFolder", help="Folder from which to search the target file (used with --auto).", type=str, default=".")
    
    args = parser.parse_args()
    figures = []
    
    if args.auto:
        if '*.' in args.file and args.file.count('.') > 1:
            raise ValueError("Pattern name not recognized.")
        figure_paths = find_file(args.file, args.searchFolder)
        if len(figure_paths) == 0:
            print(f"Error: no file named '{args.file}' found in '{args.searchFolder}'")
            sys.exit(1)
        for figure_path in figure_paths:
            figure = ArrayStorageCompressor.readFromFile(figure_path)
            assert isinstance(figure, go.Figure), f"Imported file must be a plotly.graph_objects.Figure object"
            figures.append(figure)
            
    else:
        figure = ArrayStorageCompressor.readFromFile(figure_path)
        assert isinstance(figure, go.Figure), f"Imported file must be a plotly.graph_objects.Figure object"
        figures.append(figure)
        
   
    if args.output is None:
        show_figures(figures)
    else:
        write_figures(figures, output, width = 1500, height = 900, scale = 4)