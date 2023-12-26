# This script was created with the assistance of OpenAI's ChatGPT.
# Special thanks to ChatGPT for providing guidance and support.
# Learn more about ChatGPT at https://openai.com/chatgpt

# Pre-requisites: exiftool (https://exiftool.org/) and ffmpeg (https://ffmpeg.org/) must be installed
# The directories for these applications must be added to the PATH environment variable

from PIL import Image
import subprocess
import json
import os
import sys
import argparse
import cv2
import numpy as np
import traceback
from datetime import datetime

exif_tool_cmd = "exiftool.exe"
ffmpeg_cmd = "ffmpeg.exe"
default_movie_filename = "output.avi"

def get_png_exif_tags(file_path, tags):
    # TODO - add verbose logging for exiftool
    exiftool_cmd = [exif_tool_cmd, "-json"] + tags + [file_path]
    try:
        exif_data = subprocess.check_output(exiftool_cmd)
    except subprocess.CalledProcessError as e:
        print(f"exiftool returned a non-zero exit status: {e.returncode}")

    exif_data_json = exif_data.decode('utf-8')
    return json.loads(exif_data_json)[0]

def extract_parameters(parameters_text):
    extracted_parameters = {}
    key_mapping = {
        "Steps": "Steps",
        "Seed": "Seed",
        "CFG scale": "CFG scale",
        "Denoising strength": "Denoising strength"
    }
    for line in parameters_text.split(','):
        for key in key_mapping:
            if key in line:
                value = line.split(':')[1].strip()
                extracted_parameters[key_mapping[key]] = value
    return extracted_parameters

# Outermost try
try:
    # Create a new ArgumentParser object
    parser = argparse.ArgumentParser(description='Movify: Extract EXIF tag information and save it to an output file.\n \
        PNG files in the current directory or the directory specified by --dir will be renamed based upon modify date if --rename is used. \n \
        This is necessary if the prefix filenames over multiple dates is the same.\n \
        JSON files will be created based upon the EXIF tag: parameter if it exists. Use --skipjson to avoid recreating these files.\n \
        JSON files will be deleted unless --keepjson is used.\n \
        JPEG images will be created from the PNG files using the parameter data in the respective JSON file.\n \
        The JPEG images will be annotated with key parameters.\n \
        A movie will be created with the name output.mp4 or the movie file specified by --moviefile.\n \
        The default frame rate can be changed by using --framerate.\n \
        --overwritemovie will overwrite any existing movie file.\n \
        --skipmovie will skip the creation of the movie. Use this to rename files and/or create JSON files only.\n')

    # Add arguments
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--dir', type=str, help='Directory to convert [Current Directory]')
    parser.add_argument('--rename', action='store_true', help='Rename files based upon EXIF tag')
    parser.add_argument('--skipjson', action='store_true', help='Skip JSON file creation')
    parser.add_argument('--keepjson', action='store_true', help='Do not remove json files after use')
    parser.add_argument('--annotate', action='store_true', help='Annotate top of JPEG files with key parameters')
    parser.add_argument('--moviefile', type=str, help='Output movie file')
    parser.add_argument('--framerate', type=int, help='Output movie file')
    parser.add_argument('--overwritemovie', action='store_true', help='Overwrite movie file without prompting')
    parser.add_argument('--skipmovie', action='store_true', help='Skip Movie file creation')

    # Parse the arguments
    args = parser.parse_args()
    verbose_mode = args.verbose
    conversion_dir = args.dir
    rename_mode = args.rename
    skipjson_mode = args.skipjson
    keepjson_mode = args.keepjson
    annotate_mode = args.annotate
    movie_file = args.moviefile
    framerate_val = args.framerate
    overwritemovie_mode = args.overwritemovie
    skipmovie_mode = args.skipmovie

    if verbose_mode is True:
        print(f"verbose = {verbose_mode}")
        print(f"conversion_directory = {conversion_dir}")
        print(f"rename = {rename_mode}")
        print(f"skip JSON = {skipjson_mode}")
        print(f"keep JSON = {keepjson_mode}")
        print(f"annotate = {annotate_mode}")
        print(f"movie_file = {movie_file}")
        print(f"frame rate = {framerate_val}")
        print(f"overwritemovie_mode = {overwritemovie_mode}")
        print(f"skip Movie = {skipmovie_mode}")

    # Path to the Pictures directory
    if conversion_dir is None:
        # Prompt the user and get input
        response = input("Warning: Using current directory for conversion and/or movie creation.\n Are you sure you want to continue [Y/n]?")
        if not response:
            response = "Y"        
        if response.upper() == 'Y':
            directory_path = os.getcwd()  # Default to the current directory        
        else:
            print("Exiting program")
            sys.exit(1)  # Use a non-zero exit code to indicate an error
    else:  
        directory_path = conversion_dir

    png_present = False
    if skipjson_mode is False:
        if verbose_mode is True:
            print("Skipping creation of JSON files")        
        # Iterate through all files in the directory
        for filename in os.listdir(directory_path):
            if filename.endswith(".png"):
                png_present = True
                file_path = os.path.join(directory_path, filename)
                tags = ["-SourceFile", "-Datemodify", "-FileModifyDate", "-Parameters"]  # Replace with the tags you want to extract
                png_tags = get_png_exif_tags(file_path, tags)
                if verbose_mode:
                    print(f"EXIF tags read from file: {png_tags}")
                source_file = png_tags.get('SourceFile')
                modifydate_str = png_tags.get('Datemodify')  # if the file has been modified by another application            
                modifydate = None
                if modifydate_str is not None:
                    if verbose_mode is True:
                        print("datemodify found - using modify date")                    
                    modifydate = datetime.strptime(modifydate_str, "%Y-%m-%dT%H:%M:%S%z")
                else:
                    if verbose_mode is True:
                        print("datemodify is empty - falling back on File Modify Date")                                      
                    modifydate_str = png_tags.get('FileModifyDate')
                    if modifydate_str is not None:
                        modifydate = datetime.strptime(modifydate_str, "%Y:%m:%d %H:%M:%S%z")
                parameters = png_tags.get('Parameters') 
                
                if verbose_mode is True:
                    print("EXIF extract")
                    print(f"SourceFile = {source_file}")
                    print(f"Modify Date = {modifydate}")
                    print(f"parameters = {parameters}")

                if source_file is None:
                    if verbose_mode is True:
                        print(f"Missing EXIF tag SourceFile using filename {filename}")
                        source_file = filename
                
                # Extract the file extension from source_file
                source_file_name, source_file_extension = os.path.splitext(source_file)

                new_file_name = source_file
                if args.rename:
                    # Rename the file using the formatted timestamp if datemodify exists
                    if modifydate is not None:
                        new_file_name = modifydate.strftime("%y%m%d%H%M%S") + source_file_extension
                                            
                        if os.path.isfile(new_file_name) is True:
                            print(f"Two files have the same modify dates:{modifydate} - do not use rename - exiting")
                            sys.exit(1)  # Use a non-zero exit code to indicate an error                        
                        else:
                            os.rename(source_file, new_file_name)
                        print(f"file {source_file} renamed to {new_file_name}")
                    else:
                        if verbose_mode is True:
                            print(f"File {filename} does not have a date-based EXIF Tag to use - Not renaming")
                
                # Extract the parameters from the text
                if parameters is not None:
                    extracted_parameters = extract_parameters(parameters)
                    if verbose_mode is True:
                        print("The extracted parameters are:")
                        for key, value in extracted_parameters.items():
                            print(f"{key}: {value}")            
                else:
                    if verbose_mode is True:
                        print(f"file {filename} does not have a Parameters EXIF Tag - Using default values")
                    extracted_parameters = 'None'

                # Write Parameters to a text file with the same filename but with .txt extension
                output_json_filename = os.path.splitext(new_file_name)[0] + ".json"        
                with open(output_json_filename, "w") as json_file:
                    json.dump(extracted_parameters, json_file, indent=4)
                    if verbose_mode is True:            
                        print(f"The Parameters have been written to: {output_json_filename}")        
                    else:
                        print("1", end='', flush=True)
            else:
                if verbose_mode is True:
                    print(f"Skipping non-PNG file/directory {filename}")
                else:
                    print(".", end='', flush=True)

    if verbose_mode is True:
        print("Making movie file")
    else:
        print("\n")
        
    json_present = False    
    png_present = False
    # Iterate through the PNG files in the directory
    for png_file in sorted(os.listdir(directory_path)):
        if png_file.endswith(".png"):
            png_present = True
            png_filename = os.path.splitext(png_file)[0]
            json_file = os.path.join(directory_path, f"{png_filename}.json")
            if os.path.exists(json_file):
                json_present = True
                with open(json_file, 'r') as f:
                    text_to_draw =''
                    json_data = json.load(f)
                    if (json_data != 'None'):
                        text_to_draw = f"File: {png_filename} | Steps {json_data['Steps']} | CFG scale {json_data['CFG scale']} | Seed {json_data['Seed']} | Denoising strength {json_data['Denoising strength']} |"
                    else:
                        text_to_draw = ""
                        
                # Use OpenCV to annotate file if necessary
                if verbose_mode is True:
                    print(f"Reading {png_file} for annotate")            
                image = cv2.imread(png_file)
                height, width, channels = image.shape
                top_bar = 30
                text_offset_x = 10
                text_offset_y = 20
                if annotate_mode is True:
                    if verbose_mode is True:
                        print(f"annotating file with {text_to_draw}")
                    image = cv2.rectangle(image, (0,0), (width, top_bar), (0,0,0), -1)
                    image = cv2.putText(image, text_to_draw, (text_offset_x,text_offset_y), fontScale = 0.5, fontFace = cv2.FONT_HERSHEY_PLAIN, \
                        color = (255,255,255), thickness = 1, bottomLeftOrigin=False)               
                jpeg_file =os.path.splitext(png_file)[0] + ".jpg"
                cv2.imwrite(jpeg_file, image)
                
                print("2", end='', flush=True)
                if verbose_mode is True:
                    print(f"\nJPEG file {jpeg_file} saved")
                    
    if png_present is False:
        print("Error no PNG files found (conversion may be required) - exiting program")
        sys.exit(1)  # Use a non-zero exit code to indicate an error
        
    if movie_file is not None:
        output_file = movie_file
    else:
        output_file = default_movie_filename

    # Delete output file
    if os.path.isfile(output_file):
        if overwritemovie_mode is True:
            if verbose_mode is True:
                print (f"deleting {output_file}")
            os.remove(output_file)
        else:
            # Prompt the user and get input
            response = input(f"\nMovie file {output_file} exists. Delete [y/N]?")
            if not response:
                response = "N"
            if response.upper() == 'Y':
                if verbose_mode is True:
                    print (f"deleting {output_file}")
                os.remove(output_file)    
            else:
                print("Exiting program")
                sys.exit(1)  # Use a non-zero exit code to indicate an error        
        
    # Call ffmpeg to create the movie
    # Appropriate level of logging based upon verbose_mode
    # no audio stream
    # frame rate is 1 Hz

    if verbose_mode is True:
        loglevel = 'debug'
    else:
        loglevel = 'panic'    
    
    if framerate_val != None:
        # This suffers from https://trac.ffmpeg.org/ticket/3164 - missing first/last frame
        ffmpeg_cmd_line = f'type *jpg | {ffmpeg_cmd} -loglevel {loglevel} -framerate {framerate_val} -vcodec mjpeg -an -f image2pipe -i - -pix_fmt yuvj420p {output_file}'
    else:
        ffmpeg_cmd_line = f'type *jpg | {ffmpeg_cmd} -loglevel {loglevel} -vcodec mjpeg -an -f image2pipe -i - -pix_fmt yuvj420p {output_file}'
    print(f"about to run {ffmpeg_cmd_line}")
    try:
        completed_process = subprocess.run(ffmpeg_cmd_line, shell=True, check=True)        
        print(f"output file {output_file} ready")
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg returned a non-zero exit status: {e.returncode} - consider using --verbose")

    #tidy up
    if keepjson_mode is False:
        for json_file in sorted(os.listdir(directory_path)):
            if json_file.endswith(".json"):
                json_filename = os.path.splitext(json_file)[0]
                if verbose_mode is True:
                    print(f"deleting file {json_file}")
                    os.remove(json_file)
except Exception as e:
    print(f"Unhandled exception: {traceback.format_exception(*sys.exc_info())}")
    raise