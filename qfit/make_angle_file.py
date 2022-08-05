
"""
Create angle file

file info
check existance of angle.txt file
make angle list
make angle file

"""

import pandas as pd
from pathlib import Path
import csv

def check_holder(data_path):
    """Check files info
         file extention: .tif
    
    args:
        data_path (str): data path
    
    returns:
        sort_p_name(list): file name list
    """
    
    def _is_num(s):
        """check the possibility for str to float
            s: str
        Returns: bool

        example: 
            print(is_num('-1.23')) #>>> True 
        """
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True

    print(f'Data path:{data_path}')
    p_ = Path(data_path)
    # print(str(p_))
    p_list = list(p_.glob("*.tif"))
    p_name = [i.name for i in p_list]

    print(f"Dark file exist  T/F: {'dark.tif' in p_name}")
    # remove dark file from list
    p_name_wo_dark =  [s for s in p_list if 'dark' not in s.stem]

    # file name is treated to theata value. So file list have to be sorted.
    # Todo sorted order. check the data file name 
    if _is_num(p_name_wo_dark[0].stem):
        if int(p_name_wo_dark[0].stem) < 0 :
            reverse_ = True
        else:
            reverse_ = False
        sort_p_list =sorted(p_name_wo_dark, key = lambda x: int(x.stem), reverse=reverse_)
    else:
        sort_p_list =sorted(p_name_wo_dark)

    sort_p_name = [i.name for i in sort_p_list]

    print(f'Number of all tif files : {len(p_list)}')
    print(f'Number of tif data files without dark file: {len(sort_p_name)}')
    print(f"tif data name: {sort_p_name[:5]}...{sort_p_name[-5:]}")
 
    angle_list = list(p_.glob("angle.txt"))
    angle_name = [i.name for i in angle_list]
    print(f"angle file exist T/F: {'angle.txt' in angle_name}")
    print('-'*5)
    
    return sort_p_name
    
def make_angle_list(start, step, length):
    """ make angle list
    
    unit: arcsec
    Args:
        start (int): start incident angle 
        step (int): step
        length (int): number of data files except dark file

    Returns:
        angle_list (list): angle list
    """

    angle_list = [i*step + start for i in range(length)] 

    print(f'data length created :{len(angle_list)}')
    print(f"angle list: {angle_list[:5]}....{angle_list[-5:]}")

    return angle_list


def make_anglefile(data_path, angle_list):
    """make angle file

    Args:
        data_path (str): data path
        angle_list (list): angle list
        
    """

    p_name_list = check_holder(data_path)
 
    file_path = f'{data_path}/angle.txt'
    print(f'Angle file path: {file_path}')
    
    angle_f = pd.DataFrame({"angle":angle_list, "filename":p_name_list})
    angle_f.to_csv(file_path,index=False)
    
    # header = ['angle', 'filename']
    # with open(file_path, 'w', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(header)
    #     for an, fi  in zip(angle_list,p_name_list):
    #         writer.writerow([an,fi])

    p_ = Path(data_path)
    angle_list = list(p_.glob("angle.txt"))
    angle_name = [i.name for i in angle_list]
    print(f"Check angle file exist T/F: {'angle.txt' in angle_name}")

def anglefile_info(data_path, sigChange=False):
    """Read and display Angle file. 
    If you change the angle sig(+,-), sigChange is True.

    Args:
        data_path (string): 
        sigChange (bool):
   
    """
    p_ = Path(data_path)
    angle_file = list(p_.glob("angle.txt"))
    angle_name = [i.name for i in angle_file]
    print(f"Check angle file exist T/F: {'angle.txt' in angle_name}")

    if 'angle.txt' in angle_name :
        
        angle_df = pd.read_csv(str(angle_file[0]))
        print(f'Read angle file: {angle_df.head()}')
        print(f'Read angle file: {angle_df.tail()}')

        if sigChange:
            angle_df['angle'] = angle_df['angle']*(-1)

            file_path = f'{p_}/angle.txt'
            # print(file_path)
            angle_df.to_csv(file_path,index=False)
            print('-'*10)
            print(f'Change: {angle_df.head()}')
            
    print('-'*10)

if __name__ == '__main__':
    pass


