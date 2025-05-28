import os
import argparse
import plotly.graph_objects as go
from Utils import ArrayStorageCompressor


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Visualize time graph")
    parser.add_argument("-f", "--file", help="Target file path, must be a json.", type=str, required=True)
    parser.add_argument("-o", "--output", help="Folder where the chunks array will be generetad.", type=str, default= None)
    args = parser.parse_args()
    figure = ArrayStorageCompressor.readFromFile(args.file)
    output = args.output
    if output:
        if "." not in output:
            output += ".jpg"
        figure.write_image(output , width=1500, height=900, scale= 4)
    else:
        figure.show()