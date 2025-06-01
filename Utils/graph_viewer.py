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
    assert len(figures) == 4, f"Expected 4 images, got {len(figures)}"
    
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
        title = dict(
            text = "Array length",
            font=dict(size = 16)
            ),
        type="linear",
        row=1,
        col=1,
    )
    fig_combined.update_xaxes(
        title = dict(
                    text="Variance",
                    font=dict(size = 16)
            ),
        type="linear",
        row=1,
        col=2
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
    
        margin = dict(l=80, r=80, t=150, b=200),
        height = 1920/2,
        width = 1140*2,
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.55,
                y=-0.2,
                showactive=True,
                buttons=[button_linear, button_log],
            )
        ],
        title = dict(
            subtitle=dict(
                text = "Run times grouped by sorting algorithm.",
                font = dict(size=24)
            ),
        ),
        legend = dict(
            orientation="h",
            yanchor="bottom",
            xanchor="center",
            y=-0.2,
            x=0.5,
        ),
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
        fig.update_layout(
            width =  1140*2 ,
            height = 1100,
            xaxis = dict(
                title= dict(
                standoff= 10
                )
            ),
            margin = dict(l=80, r=80, t=150, b=200),
            legend = dict(
               title=dict(
                    text="Algorithms",
                    side="top"
                ),
                yanchor="bottom",
                y=-0.18,
                xanchor="center",
                x=0.5,
                font=dict(size=20), 
                entrywidth = 140,
                orientation = 'h'
            ),
            updatemenus = [
                dict(
                    pad=dict(r=20, l=20, t=20, b= 20)
                )
            ]
        )
        
        html_str = fig.to_html(include_plotlyjs='cdn', full_html=True,  config={"responsive": True})
        html_str = html_str.replace(
                    "<body>",
                    """
                    <body>
                    <style>
                        body{
                            margin: 0;
                            padding: 0;
                            width: 100% !important;
                            height: 90% !important;
                        }
                        .updatemenu-header-group > g .updatemenu-item-rect {
                            height: 36px !important;   
                        }

                        .updatemenu-item-text {
                            font-size: 20px !important;
                            dominant-baseline: middle;
                        }
                        
                    </style>
                    <script>
                        function repositionButtons() {
                            const buttons = document.querySelectorAll('.updatemenu-header-group .updatemenu-button');
                            if (buttons.length === 0) {
                                return;
                            }

                            const legend = document.querySelector('.infolayer .legend');
                            if (!legend) {
                                return;
                            }

                            const rect = legend.getBoundingClientRect();
                            const bound_x = rect.width;
                            const bound_y = rect.height;

                            const raw_transform = legend.getAttribute("transform");
                            if (!raw_transform) {
                                return;
                            }

                            const coords = raw_transform
                                .substring(raw_transform.indexOf("(") + 1, raw_transform.indexOf(")"))
                                .split(',')
                                .map(val => parseFloat(val.trim()));

                            const [tx, ty] = coords;

                            const spacing = 20;
                            let totalWidth = 0;

                            buttons.forEach((btn, i) => {
                                const w = btn.getBBox().width;
                                totalWidth += w;
                            });
                            totalWidth += spacing * (buttons.length - 1);

                            const startX = tx + bound_x / 2 - totalWidth / 2;
                            const y = ty + bound_y + bound_y / 2;

                            let currentX = startX;
                            buttons.forEach((btn, i) => {
                                const btnWidth = btn.getBBox().width;
                                const centerX = currentX;
                                btn.setAttribute('transform', `translate(${centerX}, ${y})`);
                                currentX += btnWidth + spacing;
                            });
                        }


                        
                        
                        window.addEventListener("load", function () {
                            repositionButtons();
                            
                            const plotContainer = document.querySelector('.main-svg');

                            if (plotContainer) {
                                const observer = new MutationObserver((mutationsList, observer) => {
                                    repositionButtons();
                                });

                                observer.observe(plotContainer, {
                                    childList: true,
                                    subtree: true,
                                });
                            }
                        
                    
                            
                        });
                    </script>
                    """
                )



        with open(output, "w", encoding="utf-8") as f:
            f.write(html_str)
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
        write_figures(figures, args.output, width = 1500, height = 900, scale = 4)