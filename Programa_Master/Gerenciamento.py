from pyModbusTCP.client import ModbusClient
import time
from AMR import *
from CR import *
from TornoCNC import *
from CentroUsinagem import *
import subprocess
import time
#from Kanban_Inspecao import *

Main_clientGer = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True)                   #IP local
CentroUsinagem_clientGer = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True)    #IP do Centro de Usinagem
TornoCNC_clientGer = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True)          #IP do torno CNC
CR_client = ModbusClient(host="192.168.192.6", port=502, unit_id=1, auto_open=True)                     #IP do CR
amr_client = ModbusClient(host="192.168.192.5", port=502, unit_id=1, auto_open=True)                    #IP do AMR


def servidor_local():
    command = "sudo pgrep -u fab40 -a python"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    #print ("Aqui" + result)
    if result.returncode == 0:
        teste=result.stdout.splitlines()
        pids = [line.split()[2] for line in result.stdout.splitlines() if len(line.split()) > 2]
        quant = len(pids)
        for i in range (quant):
            try:
                if (teste[i].index("ServerModbus.py")):
                    pid=str(teste[i]).split()
                    #command = "sudo kill -9 " + str(pid[0])
                    print ("registro" + pid[0])
                    result = subprocess.run(command, shell=True)
                    sleep(50)
                    result = subprocess.run(command, shell=True)
            except:
                    pass
                    
    subprocess.Popen(['gnome-terminal', '--', 'python', 'ServerModbus.py'], start_new_session=True)
    time.sleep(1)
    #print("ServidorMdb_OK3")
    #return    

def inicio_programa():
    Main_clientGer.write_single_register(1,3)   #iniciar operando torno da peca  1 - P1
    Main_clientGer.write_single_register(2,3)   #iniciar operando centro da peca 1 -P1
    Main_clientGer.write_single_register(111,0) #Passo Inical Centro de Usinagemorno
    Main_clientGer.write_single_register(112,0) #Passo Inical torno

    Main_clientGer.write_single_register(113,0) #Programa atual sendo executado no Torno
    Main_clientGer.write_single_register(114,0) #Programa atual sendo executado Centro de Usinagem

    Main_clientGer.write_single_register(6,0)   #Passo CR armazenado
    Main_clientGer.write_single_register(5,0)   #Carga de bateria do AMR



    #Main_clientGer.write_single_register(100,0)  #Modo0 Pause

    
    Main_clientGer.write_single_coil(2,False)   # Estagio_Abastecer base AMR
    Main_clientGer.write_single_coil(3,False)   # EM_Atividade 
    Main_clientGer.write_single_coil(4,False)   # Kanban Peças do Torno
    Main_clientGer.write_single_coil(5,False)   # Kanban Peças do Centro de Usinagem Manipulo
    Main_clientGer.write_single_coil(6,False)   # Kanban Peças do Centro de Usinagem Cabeça do Martelo


    Main_clientGer.write_single_register(11,0)   #Status peca 1
    Main_clientGer.write_single_register(12,0)   #Status peca 2
    Main_clientGer.write_single_register(13,0)   #Status peca 3
    Main_clientGer.write_single_register(14,0)   #Status peca 4
    Main_clientGer.write_single_register(15,0)   #Status peca 5
    Main_clientGer.write_single_register(16,0)   #Status peca 3 PRIMEIRA ETAPA
    
    Main_clientGer.write_single_register(17,0)   #Status peca P3 PRIMEIRA ETAPA E ESTA NA BASE DO AMR

    Main_clientGer.write_single_register(21,0)   #Status pega peça 1
    Main_clientGer.write_single_register(22,0)   #Status pega peça 2
    Main_clientGer.write_single_register(23,0)   #Status pega peça 3
    Main_clientGer.write_single_register(24,0)   #Status pega peça 4
    Main_clientGer.write_single_register(25,0)   #Status pega peça 5

    
    Main_clientGer.write_single_register(30,0)   #Contagem de Produção Geral
    
    Main_clientGer.write_single_register(31,0)   #Contagem de Produção P1
    Main_clientGer.write_single_register(32,0)   #Contagem de Produção P2
    Main_clientGer.write_single_register(33,0)   #Contagem de Produção P3
    Main_clientGer.write_single_register(34,0)   #Contagem de Produção P4
    Main_clientGer.write_single_register(35,0)   #Contagem de Produção P5
    Main_clientGer.write_single_register(36,0)   #Contagem de Produção P3 Centro Usinagem


    Main_clientGer.write_single_register(37,0)   #Toogle_ProducaoBatentes
    Main_clientGer.write_single_register(38,0)   #Toogle_ProducaoManipulo
    Main_clientGer.write_single_register(39,0)   #Toogle_ProducaoPrimeiroEstagioCabeca
    Main_clientGer.write_single_register(40,0)   #Toogle_ProducaoCabecaCentroUsinagemFIm

    Main_clientGer.write_single_register(41,0)   #Toogle_ReinicioTorno
    Main_clientGer.write_single_register(42,0)   #Toogle_ReinicioCentroUsinagem
    
    Main_clientGer.write_single_register(43,0)   #Toogle_Espera

    Main_clientGer.write_single_register(50,0)   #ESTADO DA PLACA TORNO



    
    iniciar_Torno()
    iniciar_CentroUsinagem()


def CR_STATUS(valor)->int:
    Main_clientGer.write_single_register(101,valor) #registrado de status Movendo/parado CR
    ##print(valor)

