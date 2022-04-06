import subprocess
import os

suffix = '_264.avi'
folder = r'C:\Users\BMLab21\Documents\CrabStreams'
contents = os.listdir(folder)
for file_name in contents:
    if '.avi' in file_name:
        output_name = file_name[:-4] + suffix
        if len(output_name) == len('YYYY-MM-DD_265.avi') and output_name not in contents:
            input_path = os.path.join(folder, file_name)
            output_path = os.path.join(folder, output_name)
            command = 'ffmpeg -i {} -c:v libx264 -crf 21 vf- format=yuv420p {}'.format(input_path, output_path)
            print(command)
            result = subprocess.run(command)
            print('compression completed')