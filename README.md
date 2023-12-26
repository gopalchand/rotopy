Extract EXIF tag information and save it to an output file.

PNG files in the current directory or the directory specified by --dir will be renamed based upon modify date if --rename is used.
This is necessary if the prefix filenames over multiple dates is the same.
JSON files will be created based upon the EXIF tag: parameter if it exists. Use --skipjson to avoid recreating these files.
JSON files will be deleted unless --keepjson is used.
JPEG images will be created from the PNG files using the parameter data in the respective JSON file.
The JPEG images will be annotated with key parameters
A movie will be created with the name output.mp4 or the movie file specified by --moviefile.
The default frame rate can be changed by using --framerate.
--overwritemovie will overwrite any existing movie file.
--skipmovie will skip the creation of the movie. Use this to rename files and/or create JSON files only.
