import os
import argparse
import shutil

def parse_txt(data):
    '''
    parse_txt 
        Parses through list of liens from txt file to arrage data into dictionary.

    Input: 
    data -> rows of data in following format:
        ("Study_ID Sample_# DST1 MID1 PRX1 ... DSTN MIDN PRXN")

    Output:
    Dictionary of data with [Study_ID, Sample_#] as key.
    '''
    data_dict = {}

    for study_data in data:
        entry = study_data.split()
        key = tuple([entry[0], entry[1]])
        isqs = entry[2:]

        measure_nums = []
        if len(measure_nums)%3:
            # print('Must have three measurement numbers for each image. (DST MID PRX).')
            print('Skipped {}'.format(entry[0]))
            continue

        for idx in range(0, len(isqs), 3):
            measure_nums.append(isqs[idx:idx+3])
        
        data_dict[key] = measure_nums
    
    return data_dict

def batch_check(data_dict, out_dir, out_txt):
    '''
    sftp_fetch
        uses sftp to download isqs in data_dict to out_dir

    data_dict
        dictionary
    out_dir
        path to output directory
    out_txt
        path to txt file to log sftp commands
    '''

    stacks = ['DST', 'MID', 'PRX']

    for id, measurements in data_dict.items():

        time = 0
        for image in measurements:
            
            for idx in range(3):
                measurement = image[idx]
                stack = stacks[idx]

                location = r'/work/manske_lab/images/hrpqct/mcp/actus_raw_stacks/{}/{}/{}_{}.nii.gz'.format(id[0], time, id[0], stack)

                with open(out_txt, 'a') as fp:
                    fp.write('{}_{}: xxxssh -qnx arc "test -f {} && echo 1 || echo 0"\n'.format(id[0], stack, location))
            time += 1
    

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("sftp_path", type=str, help="Text file (path + filename)")
    parser.add_argument("out_dir", type=str, help="Output")
    args = parser.parse_args()

    sftp_path = args.sftp_path
    out_dir = args.out_dir

    temp_dir = os.path.join(out_dir, 'temp')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)

    file = open(sftp_path, 'r')
    lines = file.readlines()

    out_txt = out_dir+'/arc_check_log.txt'
    with open(out_txt, 'w') as fp:
        pass

    data_dict = parse_txt(lines)

    batch_check(data_dict, temp_dir, out_txt)

if __name__=='__main__':

    main() 