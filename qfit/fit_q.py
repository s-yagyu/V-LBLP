"""
Interfaces for Jupyter
Wrappers for fit.py and q2.py

"""

__author__ = "Shinjiro Yagyu"
__license__ = "BSD-3-Clause"
__copyright__ = "National Institute for Materials Science, Japan"
__date__ = "2022/09/02"
__version__= "1.0.0"
__revised__ = "2022/09/02"


from pathlib import Path
import subprocess
from subprocess import PIPE
import time

from qfit import file_folder_trans as fft

P = Path().resolve()
# print(Path().resolve())
# print(list(p.iterdir()))

#./qfit/fit.py
# FIT_path = str(list(P.glob('*/fit.py'))[0])
FIT_path = str(list(P.glob('**/fit.py'))[0])

#./qfit/q2.py
# q2_path = str(list(P.glob('*/q2.py'))[0])
q2_path = str(list(P.glob('**/q2.py'))[0])


# print(FIT_path)
# print(q_path)


def fit_analysis(target_file, method='hw', comment='', filter=30, pmax=30, 
                NX=2368, NY=2240, core=4, timeout=20000, out_tif=True):
    """Rocing curve fitting using subprocess

    Args:
        target_file (str): target file path
        method (str, optional):'hw' or 'gaussian'. Defaults to 'hw'.
                hw: full width half maximum
                gaussian : gauss distribution. 
        comment (str, optional): [description]. Defaults to ''.
        filter (int, optional): except low intensty. Defaults to 30.
            Do not fit signals if difference between min and max is less than chosen threshold
	        If the difference of the intensity of (max-min) is less than options["filter"], then the fitting value is nan.
        pmax (int, optional): using Gauss fitting only. Defaults to 30.
            If peak hight < peak hight average +pmax, then fitting values nan.
        NX (int, optional) : number of x pixels (Width=NX), type=int, default=2240
        NY (int, optional) : number of y pixels (Height=NY), type=int, default=2368
	        allows to set other image sizes than the default
        core (int, optional): Number of cores. Defaults to 4.
        timeout (int, optional): fitting timeout. Defaults to 20000.-> about 5.5h
        out_tif (bool, optional): output to tif file. Defaults to 'True'

    Returns:
        folder_dir(str): Output folder name
        outstring([list(str)]):output from subprocess
    
    Examples:
        t_file =fm0
        t_folder, t_out = fit_analysis(target_file=t_file, method='gaussian', pmax=30, comment='GaN 4',filter=20, core=12)
        print(t_out[-3])
        
        c_file= fm120
        c_folder, c_out = fit_analysis(target_file=c_file, method='gaussian', pmax=30, comment='GaN 4',filter=20, core=12)
        print(c_out[-3])
    """
    
    start_time = time.time()
    # print('S'*10)
    print(comment)
    # print('start')
    print(f'target file:{target_file}')
    
    
    command_list = ['python',FIT_path, str(target_file), method, '-f', 'tif', 
                    '--filter', str(filter), '-n', str(core),'-s','--pmax', 
                    str(pmax),'-b','--nx', str(NX), '--ny', str(NY) ]
    proc = subprocess.Popen(command_list, stdout=PIPE, stderr=PIPE)


    try:
        outs, errs = proc.communicate(timeout=timeout)
    except subprocess.SubprocessError:
        proc.kill()
        outs, errs = proc.communicate()
        
    elasp_time =time.time()-start_time
    print(f'Elasped time: {elasp_time :.1f}[s] @ {core} cores')
    outstring = outs.decode('utf-8').split('\n')
    
    
    try:
        out_file = outstring[-3].strip()

    except:
        out_file = "error, check the angle file"
        print(f'Output file name: {out_file}')
        return 
        
    folder_dir= fft.npy2folder(out_file,NX,NY,out_tif)

    print(f'Comment: {comment}')
    print(f'Output file name: {out_file}')
    print(f'Folder name: {str(folder_dir)}')
    # print(f'all output {outstring}')

    print('-'*10)
    return folder_dir, outstring
    

def q_analysis_2R(target_t, target_c, out_file='q_anal', angle_t=0, angle_c=120, 
                q=6.258, NX=2368, NY=2240, out_tif=True):
    """q calculation using subprocess

    Args:
        target_t (str):  angle_t .npy file path and name. data unit [arcsec].
        target_c (str):  angle_c .npy file path and name. data unit [arcsec].
        out_file (str, optional): output file name. Defaults to 'q_anal'.
        angle_t (int, optional): theta angle . Defaults to 0.
        angle_c (int, optional): chi angle. Defaults to 120.
        q (float, optional): lattice value. Defaults to 6.258.
        NX (int, optional) : number of x pixels (Width=NX), type=int, default=2240
        NY (int, optional) : number of y pixels (Height=NY), type=int, default=2368
        out_tif (bool, optional): output to tif file. Defaults to 'True'
        
    Returns:
        folder_dir(str): Output folder name
    
    Example:
        target_t = 'hw_210721_105547_c.npy'
        target_c = 'hw_210721_105858_c.npy'
        out_file_ = 'q_0p'
        angle_t_ = 0
        angle_c_ = 120
        q_analysis_2R(target_t=target_t,target_c=target_c, out_file=out_file_, 
                        angle_t=angle_t_, angle_c=angle_c_)

    """

    print(f'outfile name:{out_file}')
    print(f'Image Size (h(NY),w(NX)):{NY ,NX}')
    print(f'set Angle t: {angle_t}, c: {angle_c}')
    print(f'set target t: {str(target_t)}, c: {str(target_c)}')
    
    command_list = ['python', q2_path, '-t', str(target_t), '-c', str(target_c), '-p', out_file, 
                    '-q', str(q), '-s', '--anglet', str(angle_t), '--anglec', str(angle_c),
                    '--nx', str(NX), '--ny', str(NY) ]

    proc = subprocess.Popen(command_list, stdout=PIPE, stderr=PIPE)

    try:
        outs, errs = proc.communicate(timeout=1800)
    except subprocess.SubprocessError:
        proc.kill()
        outs, errs = proc.communicate()
    
    output_file_name = f'{out_file}_x.npy'

    folder_dir= fft.npy2folder(output_file_name,NX,NY,out_tif)

    # print(f'Output file name: {out_file}')
    # print(f'Folder name: {str(folder_dir)}')
   
    outstring=outs.decode('utf-8').split('\n')
    print(outstring)
    print('-'*10)  

    return folder_dir
    
if __name__ == '__main__':
    pass
