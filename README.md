[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

![Roto1](https://github.com/gopalchand/rotopy/assets/45721890/2934fc37-4e18-48ef-8ca3-7c310de9a484)

# RotoPy

Combine all PNG or JPEG files in a particular directory into a video with frame rates from 1 to 30 Hz. The images must be of the same size.
**Stable Diffusion** annotation (Steps, CFG scale, Seed, Denoising strength) can be overlayed if required for Stable Diffusion generated PNG files.

## Prerequisites

* Windows 10 or higher (not yet tested under Ubuntu)
* exiftool (https://exiftool.org/) and ffmpeg (https://ffmpeg.org/) are required and must be in the PATH environment variable
* Python >= 3.10.6
* OpenCV >= 4.8.0
* numpy >= 1.26.0

## Installation

```
git clone https://github.com/gopalchand/rotopy
pip install opencv-python
cd rotopy
```

### Basic Test
For testing, copy the contents of the source_images subfolder to the input folder

```
python rotopy.py --input_dir input --output_dir output
```

The `--rename` option will rename the files in input folder with the date they were modified. It is only necessary if the filename order does not match the creation date order.
The original files will be copied over to the bak subfolder.
JPEG files derived from the PNG files will be concatenated in the output folder to produce the movie file, output/output.mkv.

### Stable Diffusion Annotation Test
Clear the contents of the output folder and copy over files created in Stable Dffusion image2image to the output folder. The files can be created over multiple days.

```
python rotopy.py  --rename --annotate --input_dir input --output_dir output
```

The `--rename` option will rename the files in input folder with the date they were modified. It is only necessary if the filename order does not match the creation date order.
The original files will be copied over to the bak subfolder.
JPEG files derived from the PNG files will be concatenated in the output folder to produce the movie file, output/output.mkv. The files will be annotated with some Stable Diffusion parameters.

For more detailed information including changing the frame rate, please see the usage below or the ![Wiki](https://github.com/gopalchand/rotopy/wiki)

## Usage

`usage: rotopy.py [-h] [--verbose] [--input_dir DIRECTORY] [--ouput_dir DIRECTORY] [--inputdir [--rename] [--skipjson] [--keepjson] [--annotate]
                 [--moviefile MOVIEFILE] [--framerate FRAMERATE] [--overwritemovie] [--skipmovie]`

Convert a directory of PNG files into a video by converting them into JPEG (.JPG extensioN) with annotation if required.
For Stable Diffusion PNG files, annotation associated with image generation can be saved in the JPEG file if the `--annotate` option is used.
A directory of non Stable Diffusion JPEG files can also be converted into a video if the `--skipjson` option is used.

Create an output.mkv file containing all the PNG images concatenated in filename order.
```
rotopy
```

Create an output.mkv file containing all the PNG images concatenated in filename order in the subdirectory input.
```
rotopy --input_directory input
```

Create an output.mkv in the subdirectory output file containing all the PNG images in the current directory concatenated in filename order.
```
rotopy --output_directory output
```


Create an output.mkv in the subdirectory output containing all the PNG images in the  in the subdirectory input concatenated in filename order.
```
rotopy --input_directory input --output_directory output
```

Create a movie.avi file containing all the PNG images concatenated in filename order using a frame rate of 4 frames per second.
```
rotopy --moviefile movie.avi --framerate 4
```

Create an output.mkv file containing all the PNG images concatenated in filename order with debugging information displayed.
```
rotopy --verbose
```

Create an output.mkv file containing all the PNG images concatenated in filename order by **renaming the PNG files** using the modify date.
Existing PNG files are backed-up in the subdirectory bak.
This is sometimes necessary because each file has the format <counter>-<seed>.png where <counter> is a 5 digit number that resets every day.
```
rotopy --rename
```

Create and output.mkv file containing all the PNG images concatenated in filename order with annotation.
JSON files are created with data for the annotation and deleted unless `--keepjson` is used.
```
rotopy --annotate
```

will create an output.mkv file containing all the PNG images concatenated in filename order and keep the JSON files describing each image.
This will allow the JSON generation part to be skipped to allow experimentation with frame rate settings etc. through a previous `--skipjson`
```
rotopy --keepjson
```

Create an output.mkv file containing all the JPEG images concatenated in filename order.
Used when the JSON files have already been created and saved through a previous `--keepjson`.
If there are no JSON files present then `--annotate` should be avoided it needs JSON files.
```
rotopy --skipjson
```

Skip the movie generation phase. JPEG files will be created from PNG files.
```
rotopy --skipmovie
```

Create an output.mkv file containing all the PNG images concatenated in filename order and overwrite an exisiting output.mkv file.
```
rotopy --overwritemovie
```

Create an output.mkv file with 4 frames per second containing all the PNG images concatenated in filename order and overwrite an exisiting output.mkv file.
```
rotopy --framerate 4
```

## Under the Hood

### JSON file creation

For each PNG file in the chosen directory, key Stable Diffusion parameters in the EXIF tags are extracted and saved in a corresponding JSON file.
e.g. for image `12345-12345.PNG`, the JSON file will be `12345-12345.JSON`.

In the current version, following paramters are saved: Steps, CFG scale, Seed and Denoising strength. Here is an example of such a JSON file:
```
{
    "Steps": "20",
    "CFG scale": "7",
    "Seed": "42",
    "Denoising strength": "0.5"
}
```

### JPEG file creation

A JPEG file will then be generated from the PNG file and if the `--annotate` option is used then the parameter values as text at the top of the image.

If the files need to be renamed because they have been generated over multiple days, the `--rename` option can be used. This will create files of the formaat `YYYYMMddHHMMSS.JPG`.

### Movie file creation

The JPEG files will then be concatenated in filename order using FFMPEG to create an movie file.

The `--framerate` option can be used to change the framerate. There appears to be a bug in FFMPEG that skips the first and/or last frame of the video if the framerate is manually set.

In the current version, the AVI container is used. The FFMPEG command is currently (if `--framerate` is set)
```
type *jpg | ffmpeg.exe -loglevel <loglevel> -vcodec mjpeg -an -framerate <framerate> -f image2pipe -i - -pix_fmt yuvj420p <outputmoviefile>
```

### Tidy up

The JSON files will be deleted unless the `--keepjson` flag option is used.

## Next Steps

1. Fix pylint errors.
2. Code testing.
3. Conversion into a Python Package.

## Contributing

Please use GitHub issue tracking to report bugs and request features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Some code was created with the assistance of OpenAI's ChatGPT.
