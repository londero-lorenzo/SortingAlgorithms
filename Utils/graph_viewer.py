import os, fnmatch
import argparse
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from Utils.ArraySettings import Variability
from Utils import ArrayStorageCompressor

def copy_layout_settings(layout, keys): return layout.to_plotly_json()

def combine(figures):
    assert len(figures) == 4, f"Expected 4 images, got {len(figures)}"
    
    default_layout = figures[0]["layout"]
    fig = make_subplots(rows=1, cols=2, shared_yaxes=False, shared_xaxes=False, horizontal_spacing=0.10)
    
    positions = {
        Variability.onLength.value["nice_name"]: {"linear": (1, 1), "logaritmic": (1, 1)},
        Variability.onNumbers.value["nice_name"]: {"linear": (1, 2), "logaritmic": (1, 2)}
    }
    
    axes_ids = {
        Variability.onLength.value["nice_name"]: {"linear": ('x', 'y'), "logaritmic": ('x2', 'y')},
        Variability.onNumbers.value["nice_name"]: {"linear": ('x', 'y2'), "logaritmic": ('x2', 'y2')}
    }

    visible_by_default = {"linear": True, "logaritmic": False}
    vis_linear = []

    for single_fig in figures:
        meta = single_fig["layout"]["meta"]
        v, scale = meta["variability"], meta["scale"]
        (row, col), (xid, yid), vis = positions[v][scale], axes_ids[v][scale], visible_by_default[scale]
        for t in single_fig.data:
            t.update(xaxis=xid, yaxis=yid, visible=vis)
            fig.add_trace(t, row=row, col=col)
            vis_linear.append(vis)

    fig.update_layout(**copy_layout_settings(default_layout, ["font"]))
    for col in range(2):
        fig.update_yaxes(title=dict(text="Time (s)", font=dict(size=20)), row=1, col=col + 1)

    fig.update_xaxes(type="linear", title=dict(font=dict(size=20)))
    fig.update_xaxes(title=dict(text="Array length"), row=1, col=1)
    fig.update_xaxes(title=dict(text="Variance"), row=1, col=2)

    fig.update_xaxes(hoverformat=".5s")

    fig.update_layout(
        margin=dict(l=80, r=80, t=150, b=200),
        height=960,
        width=2280,
        hovermode="x unified",
        title=dict(subtitle=dict(text="Run times grouped by sorting algorithm.", font=dict(size=24))),
        legend=dict(orientation="h", yanchor="bottom", xanchor="center", y=-0.2, x=0.5, groupclick='togglegroup'),
        updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0.55, y=-0.2,
            showactive=True,
            buttons=[
                dict(label="Linear scale", method="relayout", args=[{
                    "xaxis.type": "linear", "xaxis2.type": "linear",
                    "xaxis.title": "Array length", "xaxis2.title": "Number variance",
                    "yaxis.type": "linear", "yaxis2.type": "linear",
                    "yaxis.title": "Time (s)", "yaxis2.title": "Time (s)"
                }]),
                dict(label="Logaritmic scale", method="relayout", args=[{
                    "xaxis.type": "log", "xaxis2.type": "log",
                    "xaxis.title": "Array length (log)", "xaxis2.title": "Number variance (log)",
                    "yaxis.type": "log", "yaxis2.type": "log",
                    "yaxis.title": "Time (log(s))", "yaxis2.title": "Time (log(s))"
                }])
            ]
        )]
    )

    # Legend grouping
    for trace in fig.data:
        trace.legendgroup = trace.name

    for alg in set(t.name for t in fig.data):
        traces = [t for t in fig.data if t.name == alg]
        for i, t in enumerate(traces):
            t.showlegend = (i == 0)

    # Coloring
    palette = px.colors.qualitative.Plotly
    alg_colors = {alg: palette[i % len(palette)] for i, alg in enumerate(sorted(set(t.name for f in figures for t in f.data)))}

    for t in fig.data:
        c = alg_colors.get(t.name, "#000")
        if hasattr(t, 'marker') and hasattr(t.marker, 'color'):
            t.marker.color = c
        if hasattr(t, 'line') and hasattr(t.line, 'color'):
            t.line.color = c

    # Vertical separator
    fig.add_shape(
        type="line", x0=0.5, x1=0.5, y0=0, y1=1,
        xref="paper", yref="paper",
        line=dict(color="LightGray", width=2, dash="dash"),
    )
    
    return fig

def find_file(filename, search_root):
    return [os.path.join(r, f) for r, _, fs in os.walk(search_root) for f in fs if fnmatch.fnmatch(f, filename)]

def show_figures(figures):
    combine(figures).show()

def write_figures(figures, output, width=1500, height=900, scale=4):
    fig = combine(figures)
    if output.endswith(".html"):
        fig.update_layout(
            width=2280, height=1100,
            margin=dict(l=80, r=80, t=150, b=200),
            xaxis=dict(title=dict(standoff=10)),
            legend=dict(
                title=dict(text="Algorithms", side="top"),
                yanchor="bottom", y=-0.18,
                xanchor="center", x=0.5,
                font=dict(size=20), entrywidth=140, orientation='h'
            ),
            updatemenus=[dict(pad=dict(r=20, l=20, t=20, b=20))]
        )

        html_str = fig.to_html(include_plotlyjs='cdn', full_html=True, config={"responsive": True})
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