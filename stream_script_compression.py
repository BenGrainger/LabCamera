import subprocess
import os

suffix = '_265.avi'
folder = r'C:\Users\BMLab21\Documents\CrabStreams
contents = os.listdir(folder)
for file_name in contents:
    if '.avi' in file_name and suffix not in file_name:
        input_name = file_name
        output_name = os.join(folder, file_name[:-4] + suffix)
        command = 'ffmpeg -i {} -c:v libx264 -crf 21 vf- format=yuv420p {}'.format(input_name, output_name)
        result = subprocess.run(command)
        pathlib.Path(json_server_file_path).write_text(json.dumps(metaData))
        print('compression completed')