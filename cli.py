import argparse
import geopandas as gpd
import fiona
import shapely
from rich.progress import track

# General Parameters
version = "0.1"

# Establish the parser
parser = argparse.ArgumentParser(prog="GeoConverter", description="A conversion tool for geo files such as .shp, .gdb, .geojson, etc.")

# General Options
general = parser.add_argument_group("general options")
general.add_argument("--version", "-v", required=False, action="store_true", help="Print the version of the program")

# Layer Options
layer = parser.add_argument_group("layer options")
layer.add_argument("--layer", "-l", required=False, type=str, help="The layer to convert")
layer.add_argument("--layers", "-ls", required=False, action="store_true", help="List the layers in the file. If this is set, the program will not convert the file")

# File Options
file_ops = parser.add_argument_group("file options")
file_ops.add_argument("--file", "-f", required=False, type=str, help="The file to convert")
file_ops.add_argument("--output", "-o", required=False, type=str, help="The output file name", default="output.geojson")
file_ops.add_argument("--format", "-fmt", required=False, type=str, help="The output format. Default is .geojson", default=".geojson")

# Coordinate Options
coords = parser.add_argument_group("coordinate options")
coords.add_argument("--crs", "-c", required=False, type=str, help="The coordinate reference system to convert to. Default is epsg:4326", default="epsg:4326")
coords.add_argument("--round", "-r", required=False, type=int, help="The number of decimal places to round the coordinates to (i.e. 7 for 0.0000001). Default is 7", default=7)

# Read File
def read_file(args, gdf=None):
    try:
        if args.layer is None:
            gdf = gpd.read_file(args.file)
        else:
            gdf = gpd.read_file(args.file, layer=args.layer)
    except Exception as e:
        print(f"Error: {e}", end="\n\n")
        exit(1)
    return gdf

# Set CRS
def set_crs(args, gdf=None):
    try:
        gdf = gdf.set_geometry("geometry")
        if args.crs:
            gdf = gdf.to_crs(args.crs)
    except Exception as e:
        print(f"Error: {e}", end="\n\n")
        exit(1)
    return gdf

# Round Geometry
def round_geometry(args, gdf=None):
    try:
        gdf["geometry"]= shapely.set_precision(gdf.geometry.array, grid_size=10**(-args.round))
    except Exception as e:
        print(f"Error: {e}", end="\n\n")
        exit(1)
    return gdf

# Write to File
def write_file(args, gdf=None):
    try:
        # Get the driver
        if args.format == ".shp":
            # No driver needed for .shp
            driver = None
        elif args.format == ".geojson":
            driver = "GeoJSON"
        elif args.format == ".gpkg":
            driver = "GPKG"
        else:
            print(f"Error: The format {args.format} is not supported", end="\n\n")
            exit(1)
        gdf.to_file(args.output, driver=driver)
    except Exception as e:
        print(f"Error: {e}", end="\n\n")
        exit(1)

    return gdf

# Main Function
def main(args):
    functions = [read_file, set_crs, round_geometry, write_file]

    # Run the functions
    gdf = None
    for f in track(functions, description="Processing..."):
        gdf = f(args, gdf)

    print(f"Output file created successfully at {args.output}{args.format}", end="\n\n")


if __name__ == "__main__":
    args = parser.parse_args()

    if args.version:
        print(f"GeoConverter v{version}", end="\n\n")
        exit(0)

    if args.layers:
        # Make sure the file is set
        if not args.file:
            print("You must set the file to list the layers", end="\n\n")
            exit(1)
        
        try:
            layers = fiona.listlayers(args.file)
            print("Layers in the file:")
            for layer in layers:
                print(f"  - {layer}")
            print("\n")
        except Exception as e:
            print(f"Error: {e}", end="\n\n")
            exit(1)

        exit(0)
    
    if not args.file:
        print("You must set the file to convert", end="\n\n")
        exit(1)

    # Run the main function
    main(args)