import os
from shutil import SameFileError

input_directory = r'C:\Users\BMLab21\Documents\CrabStreams'
output_directory = r'Y:\users\beng\CrabStreams'

input_files = os.listdir(input_directory)
existing_files_in_loc = os.listdir(output_directory)
for file in input_files:
    if file not in existing_files_in_loc:
        ending_destination = os.join(file, output_directory)
        try:
            # copy file
            shutil.copyfile(src_file, dst_file)
            # destination folder after copying
            print("Destination after copying", ending_destination)
        except SameFileError:
            print("We are trying to copy the same File")
        except IsADirectoryError:
            print("The destination is a directory")