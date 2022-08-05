"""
Interfaces for Jupyter
Wrappers for fit.py and q2.py

"""

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
    
    Example:
    
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


#------------------ Not Used (develop version)-------------

# q_path = str(list(P.glob('*/q.py'))[0])
# q3_path = str(list(P.glob('*/q3.py'))[0])
# q4_path = str(list(P.glob('*/q4.py'))[0])
# q2i_path = str(list(P.glob('*/qi2.py'))[0])
# q2w_path = str(list(P.glob('*/q2_w.py'))[0])


# def q_analysis_2Rw(target_t, target_c, out_file='qw_anal', angle_t=0, angle_c=120, 
#                 q=1, NX=2368, NY=2240, out_tif=True):
#     """q calculation using subprocess for FWHM data
#     FWHM(width) data[arcsec] ['w']

#     Args:
#         target_t (str):  angle_t .npy file name. 
#         target_c (str):  angle_c .npy file name
#         out_file (str, optional): output file name. Defaults to 'qw_anal'.
#         angle_t (int, optional): theta angle . Defaults to 0.
#         angle_c (int, optional): chi angle. Defaults to 120.
#         q (float, optional): lattice value. Defaults to 1.
#         NX (int, optional) : number of x pixels (Width=NX), type=int, default=2240
#         NY (int, optional) : number of y pixels (Height=NY), type=int, default=2368
#         out_tif (bool, optional): output to tif file. Defaults to 'True'
        
#     Returns:
#         folder_dir(str): Output folder name
        
#     Example:
#         target_t = 'hw_210721_105547_w.npy'
#         target_c = 'hw_210721_105858_w.npy'
#         out_file_ = 'qw_0p'
#         angle_t_ = 0
#         angle_c_ = 120
#         q_analysis_2R(target_t=target_t,target_c=target_c, out_file=out_file_, 
#                         angle_t=angle_t_, angle_c=angle_c_)

#     """

#     print(f'outfile name:{out_file}')
#     print(f'Image Size (h(NY),w(NX)):{NY ,NX}')
#     print(f'set Angle t: {angle_t}, c: {angle_c}')
#     print(f'set target t: {str(target_t)}, c: {str(target_c)}')
    
#     command_list = ['python', q2w_path, '-t', str(target_t), '-c', str(target_c), '-p', out_file, 
#                     '-q', str(q), '-s', '--anglet', str(angle_t), '--anglec', str(angle_c),
#                     '--nx', str(NX), '--ny', str(NY) ]

#     proc = subprocess.Popen(command_list, stdout=PIPE, stderr=PIPE)

#     try:
#         outs, errs = proc.communicate(timeout=1800)
#     except subprocess.SubprocessError:
#         proc.kill()
#         outs, errs = proc.communicate()
    
#     output_file_name = f'{out_file}_x.npy'

#     folder_dir= fft.npy2folder(output_file_name,NX,NY,out_tif)

#     # print(f'Output file name: {out_file}')
#     # print(f'Folder name: {str(folder_dir)}')
   
#     outstring=outs.decode('utf-8').split('\n')
#     print(outstring)
#     print('-'*10)  

#     return folder_dir

# def q_analysis(target_t, target_c, out_file='q_anal', angle=120, q=6.258):
#     """q calculation using subprocess

#     Args:
#         target_t (str): theta data file name 
#         target_c (str): chi data file name 
#         out_file (str, optional): out put name. Defaults to 'q_anal'.
#         angle (int, optional): chi angle. Defaults to 120.
#         q (float, optional): q value. Defaults to 6.258.
    
#     Example:
#         target_t = 'hw_210721_105547_c.npy'
#         taeget_c = 'hw_210721_105858_c.npy'
#         out_file = 'n4'
#         q_analysis(target_t=target_t,taeget_c=taeget_c,out_file='n4',angle=120)
        
#     Note:
#         example for shell
#         python .\q.py -t .\hw_210630_134353_c.npy -c .\hw_210630_135306_c.npy -p n002 -q 6.258  -s
        
#     """
#     print(f'outfile name:{out_file}')
#     print(f'set angle: {angle}')
    
#     command_list = ['python', q_path, '-t', target_t, '-c', target_c, '-p', out_file, '-q', str(q), '-s', '--angle', str(angle) ]
#     proc = subprocess.Popen(command_list, stdout=PIPE, stderr=PIPE)

#     try:
#         outs, errs = proc.communicate(timeout=1800)
#     except subprocess.SubprocessError:
#         proc.kill()
#         outs, errs = proc.communicate()
#     outstring=outs.decode('utf-8').split('\n')
#     print(outstring)
#     print('-'*10)

# def q_analysis_3R(target_t, target_c, target_n, out_file='q_anal', angle_t=0, angle_c=120, angle_n=0, fct=1, q=6.258):
#     """
#     q calculation using subprocess
#     3 R vectors calculation

#     # special case t=0 c=120, c2=-120
#     angle=1212
    
#     # python .\q3.py -t .\hw_210630_134353_c.npy -c .\hw_210630_135306_c.npy -a .\hw_210630_135306_c.npy -p n002 -q 6.258  -s
    
#     example
#     target_t = 'hw_210721_105547_c.npy'
#     target_c = 'hw_210721_105858_c.npy'

    
#     """
#     print(f'outfile name:{out_file}')
#     print(f'set Angle t: {angle_t}, c: {angle_c}, n: {angle_n}')
#     print(f'facter: {fct}')
#     # print(f'{q3_path}')
    
#     command_list = ['python', q3_path, '-t', target_t, '-c', target_c, '-n', target_n, '-p', out_file, '-q', str(q), 
#                     '-f', str(fct), '-s', '--anglet', str(angle_t), '--anglec', str(angle_c),'--anglen', str(angle_n) ]
#     proc = subprocess.Popen(command_list, stdout=PIPE, stderr=PIPE)

#     try:
#         outs, errs = proc.communicate(timeout=1800)
#     except subprocess.SubprocessError:
#         proc.kill()
#         outs, errs = proc.communicate()
#     outstring=outs.decode('utf-8').split('\n')
#     print(outstring)
#     print('-'*10)  

    
# def q_analysis_4R(target_t, target_c, target_a='None', out_file='q4_anal', angle=1212, q=6.258):
#     """
#     q calculation using subprocess
#     4 R vectors calculation

#     # special case t=0 c=120, c2=-120
#     angle=1212
    
#     """

#     command_list = ['python', q4_path, '-t', target_t, '-c', target_c, '-a',target_a, '-p', out_file, '-q', str(q), '-s', '--angle', str(angle) ]
#     proc = subprocess.Popen(command_list, stdout=PIPE, stderr=PIPE)

#     try:
#         outs, errs = proc.communicate(timeout=1800)
#     except subprocess.SubprocessError:
#         proc.kill()
#         outs, errs = proc.communicate()
#     outstring=outs.decode('utf-8').split('\n')
#     print(outstring)
#     print('-'*10)
    
# def q_analysis_2RI(target_t, target_c, target_it, target_ic, out_file='q_anal', angle_t=0, angle_c=120, q=6.258, NX=2368, NY=2240):
#     """q calculation using subprocess

#     Args:
#         target_t (str):  angle_t .npy file name
#         target_c (str):  angle_c .npy file name
#         target_it (str):  hight_t .npy file name
#         target_ic (str):  hight_c .npy file name
#         out_file (str, optional): output file name. Defaults to 'q_anal'.
#         angle_t (int, optional): theta angle . Defaults to 0.
#         angle_c (int, optional): chi angle. Defaults to 120.
#         q (float, optional): lattice value. Defaults to 6.258.
    
#     Example:
#         target_t = 'hw_210721_105547_c.npy'
#         target_c = 'hw_210721_105858_c.npy'
#         target_it = 'hw_210721_105547_h.npy'
#         target_ic = 'hw_210721_105858_h.npy'
        
#         out_file_ = 'q_0p'
#         angle_t_ = 0
#         angle_c_ = 120
#         q_analysis_2R(target_t=target_t,target_c=target_c, out_file=out_file_, 
#                         angle_t=angle_t_, angle_c=angle_c_)

#     """

#     print(f'outfile name:{out_file}')
#     print(f'set Angle t: {angle_t}, c: {angle_c}')
    
#     command_list = ['python', q2i_path, '-t', target_t, '-c', target_c,  '-i', target_it, '-j', target_ic,'-p', 
#                     out_file, '-q', str(q), '-s', '--anglet', str(angle_t), '--anglec', str(angle_c),
#                     '--nx', str(NX), '--ny', str(NY) ]
#     proc = subprocess.Popen(command_list, stdout=PIPE, stderr=PIPE)

#     try:
#         outs, errs = proc.communicate(timeout=1800)
#     except subprocess.SubprocessError:
#         proc.kill()
#         outs, errs = proc.communicate()
#     outstring=outs.decode('utf-8').split('\n')
#     print(outstring)
#     print('-'*10)  

    
if __name__ == '__main__':
    pass