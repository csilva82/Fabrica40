from CR import *
from AMR import irparaposicao
from TornoCNC import *
from CentroUsinagem import *
from Gerenciamento import *
#from Estacao_Buffer import *

Main_client = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True)                   #IP local

def abastecer():
    irparaposicao(5)    #Posicao do Buffer para abastecimento
    CR_atividade(50)    #ABASTECER tODAS
    #CR_atividade(1)     #Abastece peca 1
    #CR_atividade(2)     #Abastece peca 2
    #CR_atividade(3)     #Abastece peca 3
    #CR_atividade(4)     #Abastece peca 4
    #CR_atividade(5)     #Abastece peca 5
    #irparaposicao(13)   #Posicao de Espera de Ordem
    Main_client.write_single_coil(2,True)     #Atualiza status da base do AMR
    Main_client.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return


def reposicao_batentes1(): #Carrega somente as peças das pontas brancas
    irparaposicao(5)     #Posicao do Buffer para abastecimento
    CR_atividade(1)
    #CR_atividade(2)
    #irparaposicao(13)  #Posicao de Espera de Ordem
    #Main_client.write_single_register(11,0)   #Status peca 1
    #Main_client.write_single_register(12,0)   #Status peca 2
    #Main_client.write_single_coil(4,False)
    Main_client.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return

def reposicao_batentes2(): #Carrega somente as peças das pontas brancas
    irparaposicao(5)     #Posicao do Buffer para abastecimento
    CR_atividade(2)
    #irparaposicao(13)  #Posicao de Espera de Ordem
    #Main_client.write_single_register(12,0)   #Status peca 2
    #Main_client.write_single_coil(4,False)
    Main_client.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return

def reposicao_cabeca(): #Carrega somente a peça de aluminio
    irparaposicao(5) #Posicao do Buffer para abastecimento
    CR_atividade(3)
    #irparaposicao(13)  #Posicao de Espera de Ordem
    #Main_client.write_single_register(13,0)   #Status peca 3
    #Main_client.write_single_coil(6,False)
    Main_client.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return

def reposicao_capa1(): #Carrega somente as peças do manipulo preto
    irparaposicao(5) #Posicao do Buffer para abastecimento
    CR_atividade(4)
    #CR_atividade(5)
    #irparaposicao(13)  #Posicao de Espera de Ordem
    #Main_client.write_single_register(14,0)   #Status peca 4
    #Main_client.write_single_register(15,0)   #Status peca 5
    
    #Main_client.write_single_coil(5,False)
    Main_client.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return

def reposicao_capa2(): #Carrega somente as peças do manipulo preto
    irparaposicao(5) #Posicao do Buffer para abastecimento
    #CR_atividade(4)
    CR_atividade(5)
    #irparaposicao(13)  #Posicao de Espera de Ordem
    #Main_client.write_single_register(14,0)   #Status peca 4
    #Main_client.write_single_register(15,0)   #Status peca 5
    
    #Main_client.write_single_coil(5,False)
    Main_client.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return