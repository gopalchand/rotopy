[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

![Roto1](https://github.com/gopalchand/Rotofy/assets/45721890/2934fc37-4e18-48ef-8ca3-7c310de9a484)

# Rotofy

Combines all PNG or JPG  files in a particular directory into a video. The images must be of the same size.
**Stable Diffusion** annotation (Steps, CFG scale, Seed, Denoising strength) can be overlayed if required for Stable Diffusion generated PNG files.

## Installation

Tested in Microsoft Widows 10
exiftool (https://exiftool.org/) and ffmpeg (https://ffmpeg.org/) are required must be in the PATH environment variable
Python 3.10.6 or higher required.

## Usage

`usage: rotofy.py [-h] [--verbose] [--dir DIR] [--rename] [--skipjson] [--keepjson] [--annotate]
                 [--moviefile MOVIEFILE] [--framerate FRAMERATE] [--overwritemovie] [--skipmovie]`

Convert a directory of PNG files into a video by converting them into JPEG (.JPG extensioN) with annotation if required. 
For Stable Diffusion PNG files, annotation associated with image generation can be saved in the JPEG file if the `--annotate` option is used.
A directory of non Stable Diffusion JPEG files can also be converted into a video if the `--skipjson` option is used.

```
rotofy
```
will create an output.avi file containing all the PNG images concatenated in filename order.

```
rotofy --directory .
```
will create an output.avi file containing all the PNG images concatenated in filename order in the directory specified.


```
rotofy --moviefile movie.avi --framerate 4
```
will create a movie.avi file containing all the PNG images concatenated in filename order using a frame rate of 4 frames per second.

```
rotofy --verbose
```
will create an output.avi file containing all the PNG images in the current directory concatenated in filename order and provide debugging information.

```
rotofy --rename
```
will create an output.avi file containing all the PNG images concatenated in modify date order by **renaming the PNG files** using the modify date.
This is sometimes necessary because each file has the format <counter>-<seed>.png where <counter> is a 5 digit number that resets every day.

```
rotofy --annotate
```
will create an output.avi file containing all the PNG images concatenated in filename order with annotation.

```
rotofy --keepjson
```
will create an output.avi file containing all the PNG images concatenated in filename order and keep the JSON files describing each image.
This will allow the JSON generation part to be skipped.

```
rotofy --skipjson
```
Skip the JSON file generation phase and create the movie.

```
rotofy --skipmovie
```
Skip the movie generation phase.

```
rotofy --overwritemovie
```
will create an output.avi file containing all the PNG images concatenated in filename order and not prompt before overwriting an existing output.avi file

```
rotofy --framerate 4
```
will create an output.avi file containing all the PNG images concatenated in filename order using a framerate of 4 per second.

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

Conversion into a Python Package.

## Contributing

Please use GitHub issue tracking to report bugs and request features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Some code was created with the assistance of OpenAI's ChatGPT.
