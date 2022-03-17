import csv
import re

with open('PUV203-test.csv', newline='') as f:
    reader = csv.DictReader(f)

    # Set new dictionary
    proj_dict = {}
    episode_dict={}
    shot_list=[]

    for row in reader:
        for k, v in row.items():
            if k.lower() == 'shot':
                results = re.match(r"(\w{3})_(\d{3})_(\d{3})_(\d{3})", v)
                shot_list.append(results.group(4))
                episode_dict[results.group(3)] = shot_list
                proj_dict[results.group(2)] = episode_dict
                short_project_name = results.group(1)
                
    print(proj_dict)


