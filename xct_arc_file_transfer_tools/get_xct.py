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

def batch_fetch(data_dict, out_dir, arc_out_dir, out_txt):
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
        id_dir = os.path.join(out_dir, id[0])

        if not(os.path.exists(id_dir)):
            os.mkdir(id_dir)

        time = 0
        for image in measurements:
            image_dir = os.path.join(id_dir, str(time))
            if not(os.path.exists(image_dir)):
                os.mkdir(image_dir)

            for idx in range(3):
                measurement = image[idx]
                stack = stacks[idx]

                source = r'/DISK6/xtremect2/data/0000{}/000{}/*ISQ*'.format(id[1], measurement)
                target = '{}/{}_{}.isq'.format(image_dir, id[0], stack)
                nii_target = '{}/{}_{}.nii.gz'.format(image_dir, id[0], stack)
                sftp_fetch(source, target, out_txt)

                arc_target = os.path.join(arc_out_dir, id[0])
                arc_target = os.path.join(arc_target, str(time))

                with open(out_txt, 'a') as fp:
                    fp.write('scp {} {}:{}\n'.format(nii_target, arc_host, arc_target))

            time += 1
    

def sftp_fetch(source, target, out_txt):
    with open(out_txt, 'a') as fp:
        fp.write('sftp {}:{} {}\n'.format(xt2_host, source, target))


def main():

    global xt2_host
    global arc_host

    parser = argparse.ArgumentParser()
    parser.add_argument("sftp_path", type=str, help="Text file (path + filename)")
    parser.add_argument("xt2_host", type=str, help="Host address of xt2 server")
    parser.add_argument("out_dir", type=str, help="Output")
    parser.add_argument("arc_host", type=str, help="Host address of arc cluster")
    parser.add_argument("arc_out_dir", type=str, help="Output dir on arc")
    args = parser.parse_args()

    sftp_path = args.sftp_path
    xt2_host = args.xt2_host
    out_dir = args.out_dir
    arc_host = args.arc_host
    arc_out_dir = args.arc_out_dir

    temp_dir = os.path.join(out_dir, 'temp')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)

    file = open(sftp_path, 'r')
    lines = file.readlines()

    out_txt = out_dir+'/sftp_fetch_log.txt'
    with open(out_txt, 'w') as fp:
        pass

    data_dict = parse_txt(lines)

    batch_fetch(data_dict, temp_dir, arc_out_dir, out_txt)

if __name__=='__main__':
    xt2_host = False
    arc_host = False

    main() 