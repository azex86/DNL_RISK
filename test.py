
from math import *
from random import *
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import time,sys,threading
import subprocess

last_n_win = 0
last_remaining = 0

def get_stat_python(n_defence:int,n_attack:int,n_echantillon:int)->tuple[int,int,float,float]:
    """Return number win  and mean of soldier remaining then rate of them"""
   

    n_win = 0
    n_soldier_remaining = 0

    for n in range(n_echantillon):
        DEF =  n_defence
        ATT = n_attack
        while DEF>0 and ATT>0:
            def_die = [randint(1,6) for i in range(min(3,DEF))]
            def_die.sort(reverse=True)
            att_die = [randint(1,6) for i in range(min(3,ATT))]
            att_die.sort(reverse=True)
            
            if min(DEF,ATT)==1:
                if att_die[0] > def_die[0]:
                    DEF-=1
                else:
                    ATT-=1
            else:
                if att_die[0] > def_die[0]:
                    DEF-=1
                else:
                    ATT-=1
                if att_die[1] > def_die[1]:
                    DEF-=1
                else:
                    ATT-=1
        if ATT>0:n_win+=1
        n_soldier_remaining+=ATT if(ATT>0)else -DEF

    mean_remaining = n_soldier_remaining/n_echantillon

    if  n_win< 0 or n_win>n_echantillon or abs(mean_remaining)>max(n_defence,n_attack):
        print(f"valeur aberrante sur le CPU : win rate : {n_win/n_echantillon} soldier remaining : {n_soldier_remaining} for {n_echantillon} echantillons and {max(n_defence,n_attack)} soldiers !")
        print(f"paramètres causant ce comportement  : --def {str(n_defence)} --att {str(n_attack)} --N {str(n_echantillon)} -q\n output : {process.stdout}")
        return last_n_win,last_remaining,last_n_win/n_echantillon,last_remaining/n_echantillon
    last_n_win = n_win
    las_mean_remaining = mean_remaining
    return n_win,mean_remaining,n_win/n_echantillon,n_soldier_remaining/n_echantillon

def get_stat_cpu(n_defence:int,n_attack:int,n_echantillon:int)->tuple[int,int,float,float]:
    """Return number win  and mean of soldier remaining then rate of them"""
    global last_n_win,last_remaining
    process = subprocess.run([".\\RISK_CPP\\x64\\Release\\RISK_CPP.exe","--def",str(n_defence),"--att",str(n_attack),"--N",str(n_echantillon)],shell=True,capture_output=True)
    if process.returncode!=0:
        print(f"sdtout : {process.stdout} stderr : {process.stderr}")
        raise Exception("Erreur lors du lancement du noyau C++")

    n_win = int.from_bytes(process.stdout[-8:-4],"little",signed=True)
    n_soldier_remaining = int.from_bytes(process.stdout[-4:],"little",signed=True)
    mean_remaining = n_soldier_remaining/n_echantillon

    if  n_win< 0 or n_win>n_echantillon or abs(mean_remaining)>max(n_defence,n_attack):
        print(f"valeur aberrante sur le CPU : win rate : {n_win/n_echantillon} soldier remaining : {n_soldier_remaining} for {n_echantillon} echantillons and {max(n_defence,n_attack)} soldiers !")
        print(f"paramètres causant ce comportement  : --def {str(n_defence)} --att {str(n_attack)} --N {str(n_echantillon)} -q\n output : {process.stdout}")
        return last_n_win,last_remaining,last_n_win/n_echantillon,last_remaining/n_echantillon
    last_n_win = n_win
    las_mean_remaining = mean_remaining
    return n_win,mean_remaining,n_win/n_echantillon,n_soldier_remaining/n_echantillon

def get_stat_gpu(n_defence:int,n_attack:int,n_echantillon:int)->tuple[int,int,float,float]:
    """Return number win  and mean of soldier remaining then rate of them"""
    global last_n_win,last_remaining
    process = subprocess.run([".\\RISK_CUDA\\x64\\Release\\RISK_CUDA.exe","--def",str(n_defence),"--att",str(n_attack),"--N",str(n_echantillon),"--thread 128"],shell=True,capture_output=True)
    if process.returncode!=0:
        print(f"stdout : {process.stdout} stderr : {process.stderr}")
        print([".\\RISK_CUDA\\x64\\Release\\RISK_CUDA.exe","--def",str(n_defence),"--att",str(n_attack),"--N",str(n_echantillon),"-q","--thread 1024"])
        raise Exception("Erreur lors du lancement du noyau C++")
    
    n_win = int.from_bytes(process.stdout[-8:-4],"little",signed=True)
    n_soldier_remaining = int.from_bytes(process.stdout[-4:],"little",signed=True)
    mean_remaining = n_soldier_remaining/n_echantillon

    if n_win< 0 or n_win>n_echantillon or abs(mean_remaining)>max(n_defence,n_attack):
        print(f"valeur aberrante sur le GPU : win rate : {n_win/n_echantillon} soldier remaining : {n_soldier_remaining} for {n_echantillon} echantillons and {max(n_defence,n_attack)} soldiers !")
        print(f"paramètres causant ce comportement  : --def {str(n_defence)} --att {str(n_attack)} --N {str(n_echantillon)} -q\n output : {process.stdout}")
        return last_n_win,last_remaining,last_n_win/n_echantillon,last_remaining/n_echantillon
    last_n_win = n_win
    las_mean_remaining = mean_remaining
    return n_win,mean_remaining,n_win/n_echantillon,n_soldier_remaining/n_echantillon

START_N = 1
END_N = 1500
STEPS = 50
SIZE = (END_N-START_N)//STEPS
TAILLE_ECHANTILLON = 10000


N = []
Wcpu = []
Wgpu = []
Wpy = []
Rpy = []
Rcpu = []
Rgpu = []
Tcpu = []
Tgpu = []
Tpy = []
for n in range(START_N,END_N,STEPS):
    N.append(n)
    start = time.monotonic()
    win,remain,win_rate,remain_mean = get_stat_cpu(n,n,TAILLE_ECHANTILLON)
    end = time.monotonic()
    Tcpu.append(end-start)
    Wcpu.append(win_rate)
    Rcpu.append(remain_mean)
    start = time.monotonic()
    win,remain,win_rate,remain_mean = get_stat_gpu(n,n,TAILLE_ECHANTILLON)
    end = time.monotonic()
    Tgpu.append(end-start)
    Wgpu.append(win_rate)
    Rgpu.append(remain_mean)
    start = time.monotonic()
    win,remain,win_rate,remain_mean = get_stat_gpu(n,n,TAILLE_ECHANTILLON)
    end = time.monotonic()
    Tpy.append(end-start)
    Wpy.append(win_rate)
    Rpy.append(remain_mean)

    print(f"{n}/{END_N} cpu : {round(Tcpu[-1],2)} s gpu : {round(Tgpu[-1],2)} s    python : {round(Tpy[-1],2)} s                                                   ",end='\r')

#plt.plot(N,Wcpu,label="Win rate cpu")
#plt.plot(N,Wgpu,label="Win rate gpu")
#plt.plot(N,Wpy,label="Win rate python")
#plt.plot(N,Rcpu,label="Remaining cpu")
#plt.plot(N,Rgpu,label="Remaining gpu")
#plt.plot(N,Rpy,label="Remaining python")
plt.plot(N,Tcpu,label="Time gpu")
plt.plot(N,Tgpu,label="Time gpu")
plt.plot(N,Tpy,label="Time python")
plt.legend()
plt.show()