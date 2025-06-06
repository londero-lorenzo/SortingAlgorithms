import os, fnmatch
import sys
import argparse
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from Utils.ArraySettings import Variability
from Utils import ArrayStorageCompressor
import glob


def combine(figures):
    from collections import defaultdict

    assert len(figures) in [2, 4], f"Expected 2 or 4 images, got {len(figures)}"

    default_variability_order = [Variability.onLength.value["nice_name"], Variability.onNumbers.value["nice_name"]]
    default_scales_order = ["linear", "logaritmic"]
    plotly_scale_names = {"linear": "linear", "logaritmic": "log"}
    scale_unit = {
        "linear": lambda x: f"({x})" if x else '',
        "logaritmic": lambda x: f"(log({x}))" if x else '(log)'
    }

    # Metadata extraction
    variabilities, scales = set(), set()
    for fig in figures:
        v = fig["layout"]["meta"]["variability"]
        s = fig["layout"]["meta"]["scale"]
        assert v in default_variability_order, f"Unknown variability {v}"
        assert s in default_scales_order, f"Unknown scale {s}"
        variabilities.add(v)
        scales.add(s)

    variabilities = [v for v in default_variability_order if v in variabilities]
    scales = [s for s in default_scales_order if s in scales]
    assert variabilities, f"No valid variabilities. Expected: {default_variability_order}"
    assert len(variabilities) <= 2, (
        f"combine() supports up to 2 variabilities. Got {len(variabilities)}: {variabilities}"
    )

    assert scales, f"No valid scales. Expected: {default_scales_order}"

    # Subplot creation
    fig = make_subplots(
        rows=1, cols=len(variabilities),
        shared_yaxes=False,
        shared_xaxes=False,
        horizontal_spacing=0.10
    )
    default_layout = figures[0]["layout"]

    # figure position
    positions = {v: {s: (1, i + 1) for s in scales} for i, v in enumerate(variabilities)}

    # subplot axies 
    axes_ids = {
        v: {
            s: (
                f"x{col if col > 1 else ''}",
                f"y{col if col > 1 else ''}"
            )
            for s, (row, col) in s_pos.items()
        }
        for v, s_pos in positions.items()
    }

    # set each trace to the rigth axies
    visible_by_default = {s: s == default_scales_order[0] for s in default_scales_order}
    for fig_in in figures:
        var = fig_in["layout"]["meta"]["variability"]
        scale = fig_in["layout"]["meta"]["scale"]
        row, col = positions[var][scale]
        x_id, y_id = axes_ids[var][scale]
        for t in fig_in.data:
            t.update(xaxis=x_id, yaxis=y_id, visible=visible_by_default[scale])
            fig.add_trace(t, row=row, col=col)

    # Import default layout
    fig.update_layout(**default_layout.to_plotly_json())
    fig.update_xaxes(hoverformat=".5s", title=dict(font=dict(size=20)))
    for i, var in enumerate(variabilities):
        fig.update_yaxes(title=dict(text="Time (s)", font=dict(size=20)), row=1, col=i + 1)
        fig.update_xaxes(title=dict(text=var), row=1, col=i + 1)

    # Button action creation
    def get_scale_args(scale):
        args = {}
        for var, scale_map in axes_ids.items():
            x_id, y_id = scale_map[scale]
            x_num = x_id[1:]
            y_num = y_id[1:]
            args.update({
                f"xaxis{x_num}.type": plotly_scale_names[scale],
                f"yaxis{y_num}.type": plotly_scale_names[scale],
                f"xaxis{x_num}.title": f"{var} {scale_unit[scale]('')}",
                f"yaxis{y_num}.title": f"Time {scale_unit[scale]('s')}"
            })
        return args

    def get_scale_button(scale):
        return {
            "label": f"{scale.capitalize()} scale",
            "method": "relayout",
            "args": [get_scale_args(scale)]
        }
    
    
    # Update final update with buttons
    fig.update_layout(
        width=2280, height=1075,
        margin=dict(l=80, r=80, t=150, b=205),
        xaxis=dict(title=dict(standoff=10)),
        hovermode="x unified",
        title=dict(
            subtitle=dict(
                text="Run times grouped by sorting algorithm according to <a href= 'https://londero-lorenzo.github.io/SortingAlgorithms/' target='_self'>Performance and Analysis of Sorting Algorithms</a> report.", font=dict(size=24),
            )
        ),
        legend=dict(
            title=dict(text="Algorithms", side="top"),
            yanchor="bottom", y=-0.18,
            xanchor="center", x=0.5,
            font=dict(size=20), entrywidth=140, orientation='h',
            groupclick='togglegroup'
        ),
        updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0.55, y=-0.2,
            showactive=True,
            buttons=[
                get_scale_button("linear"),
                get_scale_button("logaritmic")
            ]
        )]
    )

    # Hide traces for non-active scales
    all_traces = list(fig.data)
    seen = set()
    for trace in all_traces:
        name = trace.name
        trace.legendgroup = name
        if name in seen:
            trace.showlegend = False
        else:
            seen.add(name)
            trace.showlegend = True

    # copy and paste trace color 
    palette = px.colors.qualitative.Plotly
    algorithms = sorted({t.name for f in figures for t in f.data})
    alg_colors = {alg: palette[i % len(palette)] for i, alg in enumerate(algorithms)}
    for trace in all_traces:
        c = alg_colors.get(trace.name, "#000")
        if hasattr(trace, 'marker') and hasattr(trace.marker, 'color'):
            trace.marker.color = c
        if hasattr(trace, 'line') and hasattr(trace.line, 'color'):
            trace.line.color = c

    # add visible separator
    if len(variabilities) > 1:
        fig.add_shape(
            type="line", x0=0.5, x1=0.5, y0=0, y1=1,
            xref="paper", yref="paper",
            line=dict(color="LightGray", width=2, dash="dash"),
        )

    return fig


def show_figures(figures):
    if len(figures) > 1:
        combine(figures).show()
    else:
        figures.pop().show()

def write_figures(figures, output, width=1500, height=900, scale=4):
    if len(figures) > 1:
        fig = combine(figures)
    else:
        fig = figures.pop()
    if '.' not in output:
        output += ".html"
    if output.endswith(".html"):
        html_str = fig.to_html(include_plotlyjs='cdn', full_html=True, config={"responsive": True})
        #if figures:
        
        html_str = html_str.replace(
        "<head>",
        """
        <head>
        <meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
		<meta name="description" content="Performance analysis of sorting algorithms under different data distributions." />
		<meta property="og:title" content="Sorting Algorithms Benchmark" />
		<link rel="icon" type="image/x-icon" href="https://londero-lorenzo.github.io/SortingAlgorithms/images/preview.png">
		<meta property="og:description" content="Interactive plots and report on QuickSort, RadixSort, CountingSort and more." />
		<meta property="og:image" content="https://londero-lorenzo.github.io/SortingAlgorithms/images/preview.png" />
		<meta property="og:type" content="website" />
		<meta property="og:url" content="https://londero-lorenzo.github.io/SortingAlgorithms/" />
		<meta name="twitter:card" content="summary_large_image" />
        """
        )
        
        html_str = html_str.replace(
            "<body>",
            """
            <body>
            <style>
                body {
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

                    buttons.forEach((btn) => {
                        const w = btn.getBBox().width;
                        totalWidth += w;
                    });
                    totalWidth += spacing * (buttons.length - 1);

                    const startX = tx + bound_x / 2 - totalWidth / 2;
                    const y = ty + bound_y + bound_y / 2;

                    let currentX = startX;
                    buttons.forEach((btn) => {
                        const btnWidth = btn.getBBox().width;
                        btn.setAttribute('transform', `translate(${currentX}, ${y})`);
                        currentX += btnWidth + spacing;
                    });
                }

                window.addEventListener("load", function () {
                    repositionButtons();

                    const plotContainer = document.querySelector('.main-svg');
                    if (plotContainer) {
                        const observer = new MutationObserver(() => {
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
        
    print(f"Interactive graph saved at:\n{os.path.abspath(output)}")
        
        
def batch_process(pattern: str, output: str):
    files = [f for f in glob.glob(pattern, recursive=True)]
    if not files:
        location = f"at {pattern}" if '*' not in pattern else f"with pattern {pattern}"
        print(f"Error: no figure files found {location}.")
        sys.exit(1)
    
    for f in files[:]:
        if os.path.isdir(f):
            batch_process(f"{f}\**\*.fig", output)
            files.remove(f)
    
    if not files:
        sys.exit(0)
    
    figures = []
    
    for figure_path in files:
        fig = ArrayStorageCompressor.readFromFile(figure_path)
        if isinstance(fig, go.Figure):
            figures.append(fig)

    print(f"Found {len(files)} figure file(s):")
    for f in files:
        print(f"  • {f}")
        
    if output is None:
        show_figures(figures)
    else:
        write_figures(figures, output, width = 1500, height = 900, scale = 4)
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Visualize time graph")
    parser.add_argument("-f", "--file", help="Target file path, must be a plotly.graph_objects.Figure object.", type=str, required=True)
    parser.add_argument("-o", "--output", help="Folder where the figures will be generetad.", type=str, default= None)

    args = parser.parse_args()
    
    
    batch_process(args.file, args.output)