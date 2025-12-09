from AMR import *
from CR import *
from TornoCNC import *
from CentroUsinagem import *
from Gerenciamento import *
from Estacao_Buffer import *
import time
import logging
logging.root.handlers = []

# Configura o logger com formato e nível de log desejados
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', 
    level=logging.INFO, 
    filename='log_Fab40.log'
)

Main_clientCOp = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True)                   #IP local
TornoCNC_clientCOp = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC
CentroUsinagem_clientOp = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True) #IP do Centro de Usinagem

tempo_inicialTornoCNC = time.time()
#print("Início do programa:", time.strftime("%H:%M:%S", time.localtime(tempo_inicial)))
toogle_viraPeca = 0

def Torno_ViraPeca():
    global toogle_viraPeca
    TORNO_Abre_Placa()                           #Torno CNC abre Placa
    TORNO_AlterarSentidodePlaca()                #Altera moode de operação da placa do torno para opera de maneira INVERTIDA fechando para fora
    TORNO_IniciaUsinagem()                       #Torno CNC Inicia Usinagem(Mover para posição de virar peça)
    time.sleep(0.2)
    #TORNO_Abrir_Porta()                         #Torno CNC abre Porta
    TORNO_Abrir_Porta()               #Torno CNC abre Porta sem verificar sensores
    #irparaposicao(4)                             #Ir para posição do torno CNC
    time.sleep(0.1)                              #Tempo de Espera após porta abrir
    toogle_viraPeca = 1


def ler_Torno_ViraPeca():
    global toogle_viraPeca
    retorno = toogle_viraPeca
    return retorno

def set_Torno_ViraPeca():
    global toogle_viraPeca
    toogle_viraPeca = 1

pos_incorretaCentroUsinagem = 0
pos_incorretaTorno=0

def Usinar_TORNO():
    loopTorno = True
    #print("Usinar_TORNO")
    while(loopTorno == True ):
        pos_incorretaTorno=0
        PosicaoAtual_AMR= amr_client.read_input_registers(33,1)[0] #Posicao Atual do AMR
        global toogle_viraPeca
        if (PosicaoAtual_AMR==4):
                passo_torno =  Main_clientCOp.read_holding_registers(112,1)[0]                     #Armazena o numero da Operação atual de usinagem no Torno CNC
                print("Usinar_TORNO:" +str(passo_torno)) 
                if passo_torno==0: 
                            Peca_03 = Main_client.read_holding_registers(13,1)[0] 
                            #if(Peca_03==False):
                            TORNO_AlterarPlacNORMAL()                    #Altera moode de operação da placa do torno para opera normalmente fechando para dentroMain_clientCOp.write_single_register(112,1
                            Main_clientCOp.write_single_register(112,1)  #Passo seguinte
                            #else:
                            #print("Aguradando Reposição Peça P3")
                elif passo_torno==1:   
                            TORNO_Abrir_Porta()                          #Torno CNC abre Porta
                            TORNO_Abre_Placa()                           #Torno CNC abre Placa
                            Main_clientCOp.write_single_register(112,2)  #Passo seguinte
                
                elif passo_torno==2:                                      #ROBO PEGA PEÇA P3 NA BASE DO AMR E COLOCA NA PLACA       
                            #tempo_inicialTornoCNC = time.time()
                            #print("P3 inicio TornoCNC:", time.strftime("%H:%M:%S", time.localtime(tempo_inicialTornoCNC)))
                            CR_atividade(12)                              #ROBO PEGA PEÇA P3 NA BASE DO AMR E COLOCA NA PLACA
                            TORNO_Fechar_Placa()                          #Torno CNC fecha Placa
                            CR_AbrirGarra_1()                             #CR ABRE garra
                            CR_atividade(13)                              #CR Sai da maquina para posição segura
                            Main_clientCOp.write_single_register(112,3)   #Passo seguinte
                
                elif passo_torno==3:
                            #irparaposicaoDireto(9)
                            PecaAtual_TORNO=Main_client.read_holding_registers(1,1)[0]  #Verifica qual peça esta fazendo no TORNO
                            time.sleep(0.1)
                            TORNO_Fechar_Porta()                                        #Torno CNC fecha Porta
                            TORNOCNC_SelecionarPrograma(PecaAtual_TORNO)                #Torno CNC seleciona Progra para operar
                            time.sleep(0.1)
                            TORNO_IniciaUsinagem()                                      #Torno CNC Inicia Usinagem(Prineira Parte) P3
                            time.sleep(0.1)
                            Main_clientCOp.write_single_register(112,4)                 #Passo seguinte
                            Main_clientCOp.write_single_coil(3,False)                   #Libera robô para realizar operações em outras maquinas
                            time.sleep(0.1)
                            print("Robô LiberadoTorno")
                            loopTorno = False
                            irparaposicaoDireto(9)

    ###########################  ROBÔ LIBERADO
                elif passo_torno==4: 
                            TornoCNC_clientCOp = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC
                            time.sleep(0.1)
                            try:   # Aguardando Usinagem
                                Status_Pause =TornoCNC_clientCOp.read_coils(23,1)[0]   #Verifica se a maquina esta em pause
                                time.sleep(0.2)
                                Status_IniciFIM =TornoCNC_clientCOp.read_coils(22,1)[0] #Verifica se o programa foi finalizado
                                time.sleep(0.2)
                                print("AGUARDANDO USINAGEM")
                                
                                if(Status_Pause==True or Status_IniciFIM==False):
                                    #TORNO_Abre_Placa()                           #Torno CNC abre Placa
                                    #TORNO_AlterarSentidodePlaca()                #Altera moode de operação da placa do torno para opera de maneira INVERTIDA fechando para fora
                                    #TORNO_IniciaUsinagem()                       #Torno CNC Inicia Usinagem(Mover para posição de virar peça)
                                    Main_clientCOp.write_single_register(112,5)  #Passo seguinte 
                                else:Main_clientCOp.write_single_coil(3,False)
                            except:
                                print("erro modbus Torno")
                                logging.error("erro modbus Torno")
                            
                
                elif passo_torno==5: #SAIDA PARA VIRAR PEÇA 
                            #TORNO_Abre_Placa()                           #Torno CNC abre Placa
                            #TORNO_AlterarSentidodePlaca()                #Altera moode de operação da placa do torno para opera de maneira INVERTIDA fechando para fora
                            #TORNO_IniciaUsinagem()                       #Torno CNC Inicia Usinagem(Mover para posição de virar peça)
                        
                            #Torno_ViraPeca = 0

                            TORNO_Abrir_Porta()                          #Torno CNC abre Porta
                            time.sleep(0.2)                              #Tempo de Espera após porta abrir
                            ####4TORNO_AlterarPlacNORMAL()                    #Altera moode de operação da placa do torno para opera normalmente fechando para dentro
                            CR_atividade(14)                             #CR realiza a virada da peça e coloca na placa P3
                            TORNO_Fechar_Placa() 
                            #fim do Acerto
                            CR_AbrirGarra_1()                            #CR ABRE garra
                            CR_atividade(13)                             #CR Sai da maquina para posição segura
                            #irparaposicaoDireto(9)
                            TORNO_Fechar_Porta()                         #Torno CNC fecha Porta
                            TORNO_IniciaUsinagem()                       #Torno CNC Inicia Usinagem(Segunda Parte)
                            time.sleep(0.2)
                            Main_clientCOp.write_single_register(112,6)  #Passo seguinte 
                            Main_clientCOp.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
                            time.sleep(0.2)
                            toogle_viraPeca = 0
                            print("Robô Liberado")                       #Robô Liberado
                            irparaposicaoDireto(9)
                            loopTorno = False
    ###########################  ROBÔ LIBERADO
                elif passo_torno==6:
                            TornoCNC_clientCOp = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC
                            time.sleep(0.1)
                            try:  # Aguardando Ausinagem
                                Status_Pause =TornoCNC_clientCOp.read_coils(23,1)[0]    #Verifica se a maquina esta em pause
                                time.sleep(0.2)
                                Status_IniciFIM =TornoCNC_clientCOp.read_coils(22,1)[0] #Verifica se o programa foi finalizado
                                time.sleep(0.2)
                                print("AGUARDANDO USINAGEM" +str(passo_torno))
                                if(Status_Pause==True or Status_IniciFIM==False):
                                    Peca_03 = Main_clientCOp.read_holding_registers(16,1)[0] 
                                    if(Peca_03==False):
                                        Main_clientCOp.write_single_register(112,7)         #Passo seguinte
                                    else: 
                                        irparaposicao(9)
                                        Main_clientCOp.write_single_coil(3,False)
                                        print("Aguardando Finalizacao de P3")
                                        loopTorno = False

                                else:Main_clientCOp.write_single_coil(3,False)
                            except:
                                print("erro modbus Torno")
                                logging.error("erro modbus Torno")
                            
    ###########################  ROBÔ LIBERADO
                elif passo_torno==7:
                        Peca_02 = Main_client.read_holding_registers(12,1)[0]   #Status peca 2
                        #if(Peca_02==False):
                        TORNO_Abrir_Porta()                          #Torno CNC Abre Porta
                        CR_atividade(18)                             #CR pega peça 2 P2 na base do AMR e pega da peça pronta P3
                        TORNO_Fechar_Placa()                         #Torno CNC fecha Placa
                        CR_atividade(13)                              #CR sai da  placa
                        #CR_atividade(20)                              #CR guarda P3
                        Main_clientCOp.write_single_register(112,8)  #Passo seguinte 
                        #Main_clientCOp.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
                        time.sleep(0.2)
                        #print("Robô Liberado")                        #Robô Liberado
                        #else:
                            #print("Aguradando Reposição Peça P2")
                        
                elif passo_torno==8:
                        PecaAtual_TORNO=Main_client.read_holding_registers(1,1)[0]  #Verifica qual peça esta fazendo no TORNO
                        time.sleep(0.2)     
                        PecaAtual_TORNO=PecaAtual_TORNO-1                           #Subrai uma da peça que esta fazendo em um total de 3
                        Main_clientCOp.write_single_register(1,PecaAtual_TORNO)     #Escreve peça esta fazendo no TORNO atual
                        time.sleep(0.2)
                        PecaAtual_TORNO=Main_clientCOp.read_holding_registers(1,1)[0]  #Verifica qual peça esta fazendo no TORNO
                        time.sleep(0.2)
                        TORNOCNC_SelecionarPrograma(PecaAtual_TORNO)                #Torno CNC seleciona Progra para operar
                        time.sleep(0.2)
                        Main_clientCOp.write_single_register(112,9)                 #Passo seguinte 

                elif passo_torno==9:
                        TORNO_Fechar_Porta()                         #Torno CNC fecha Porta
                        TORNO_IniciaUsinagem()                       #Torno CNC Inicia Usinagem(Segunda Parte)
                        time.sleep(0.2)
                        PecaAtual_TORNO=Main_clientCOp.read_holding_registers(1,1)[0]  #Verifica qual peça esta fazendo no TORNO
                        if(PecaAtual_TORNO==2):
                            CR_atividade(20)                              #CR guarda P3
                        
                        Main_clientCOp.write_single_register(112,10) #Passo seguinte 
                        Main_clientCOp.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
                        time.sleep(0.2)
                        PecaAtual_TORNO=Main_client.read_holding_registers(1,1)[0]  #Verifica qual peça esta fazendo no TORNO
                        
                        if(PecaAtual_TORNO==1):
                            CR_atividade(25)                             #CR coloca P2 usinada na base
                        
                        print("Robô Liberado")                        #Robô Liberado
                        irparaposicaoDireto(9)
                        loopTorno = False
                        # Tempo de Usinagem P3
                        #tempo_parcial_1 = time.time()
                        #print("Usinagem P3 Torno:", tempo_inicialTornoCNC - tempo_inicial, "segundos")
    ###########################  ROBÔ LIBERADO
    #######################################################################################PEÇAS DOS BATENTES 
                elif passo_torno==10:
                        TornoCNC_clientCOp = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC
                        time.sleep(0.1)
                        try:   # Aguardando Ausinagem
                                Status_Pause =TornoCNC_clientCOp.read_coils(23,1)[0]     #Verifica se a maquina esta em pause
                                time.sleep(0.2)
                                Status_IniciFIM =TornoCNC_clientCOp.read_coils(22,1)[0]  #Verifica se o programa foi finalizado
                                time.sleep(0.2)
                                print("AGUARDANDO USINAGEM")
                                
                                if(Status_Pause==True or Status_IniciFIM==False):
                                    #TORNO_Abre_Placa()                           #Torno CNC abre Placa
                                    #TORNO_AlterarSentidodePlaca()                #Altera moode de operação da placa do torno para opera de maneira INVERTIDA fechando para fora
                                    #TORNO_IniciaUsinagem()                       #Torno CNC Inicia Usinagem(Mover para posição de virar peça)
                                    Main_clientCOp.write_single_register(112,11)         #Passo seguinte
                                else:Main_clientCOp.write_single_coil(3,False) 
                        except:
                                print("erro modbus Torno")
                                logging.error("erro modbus Torno")
                
                elif passo_torno== 11:
                            #TORNO_Abre_Placa()                           #Torno CNC abre Placa
                            #TORNO_AlterarSentidodePlaca()                #Altera moode de operação da placa do torno para opera de maneira INVERTIDA fechando para fora
                            #TORNO_IniciaUsinagem()                       #Torno CNC Inicia Usinagem(Mover para posição de virar peça)
    
                            #Torno_ViraPeca = 0
                            
                            TORNO_Abrir_Porta()                          #Torno CNC abre Porta
                            time.sleep(0.1)                                #Tempo de Espera após porta abrir
                            ####4TORNO_AlterarPlacNORMAL()                    #Altera moode de operação da placa do torno para opera normalmente fechando para dentro
                            CR_atividade(21)                             #CR realiza a virada da peça e coloca na placa
                            TORNO_Fechar_Placa()                         #Torno CNC fecha Placa
                            CR_atividade(13)                             #CR realiza a virada da peça e coloca na placa
                            TORNO_Fechar_Porta()                         #Torno CNC fecha Porta
                            TORNO_IniciaUsinagem()                       #Torno CNC Inicia Usinagem(Segunda Parte)
                            time.sleep(0.2)
                            Main_clientCOp.write_single_register(112,12)
                            Main_clientCOp.write_single_coil(3,False)
                            time.sleep(0.5)
                            #global toogle_viraPeca
                            toogle_viraPeca = 0
                            print("Robô Liberado")                        
                            irparaposicaoDireto(9)
                            loopTorno = False
            ###########################  ROBÔ LIBERADO
                        
                elif passo_torno==12:
                        TornoCNC_clientCOp = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC
                        time.sleep(0.1)
                        try: # Aguardando Ausinagem
                                Status_Pause =TornoCNC_clientCOp.read_coils(23,1)[0]     #Verifica se a maquina esta em pause
                                time.sleep(0.2)
                                Status_IniciFIM =TornoCNC_clientCOp.read_coils(22,1)[0]  #Verifica se o programa foi finalizado
                                time.sleep(0.2)
                                print("AGUARDANDO USINAGEM")

                                if(Status_Pause==True or Status_IniciFIM==False):
                                    Peca_02 = Main_client.read_holding_registers(12,1)[0]   #Status peca 2
                                    if(Peca_02==False):
                                        Main_clientCOp.write_single_register(112,13)         #Passo seguinte
                                    else: Main_clientCOp.write_single_coil(3,False)
                                else:Main_clientCOp.write_single_coil(3,False) 
                        except:
                                print("erro modbus Torno")
                                logging.error("erro modbus Torno")
                elif passo_torno==13:
                        TORNO_Abrir_Porta()                                          #Torno CNC Abre Porta
                        PecaAtual_TORNO=Main_client.read_holding_registers(1,1)[0]   #Verifica qual peça esta fazendo no TORNO
                        if (PecaAtual_TORNO==2):
                                CR_atividade(22)                             #CR pega P1 na Base
                                CR_atividade(23)                             #CR pega P2 ronta NA Placa
                                CR_atividade(24)                             #CR coloca P1 Na Placa
                                CR_atividade(13)                             #CR sai com segurança
                                CR_atividade(25)                             #CR coloca P2 usinada na base
                        else:
                                CR_atividade(23)                             #CR pega P1 ronta NA Placa
                                CR_atividade(10)                             #CR vai para posicao Segura
                                CR_atividade(26)                             #CR coloca P1 usinada na base
                        
                        Main_clientCOp.write_single_register(112,14)      #Passo seguinte 
                        

    ###########################  ROBÔ LIBERADO
                elif passo_torno==14: #Se a peça atual for P2 refaz o loop com dados da peça 1. Se não ciclo no torno concluido.
                        PecaAtual_TORNO=Main_client.read_holding_registers(1,1)[0]
                        time.sleep(0.2)
                        PecaAtual_TORNO=Main_client.read_holding_registers(1,1)[0]
                        if (PecaAtual_TORNO==2):
                                Main_clientCOp.write_single_register(112,8)  
                                Main_clientCOp.write_single_coil(3,False)         #Libera robô para realizar operações em outras maquinas
                                time.sleep(0.2)
                                print("Robô Liberado")                            #Robô Liberado
                        else:
                                Main_clientCOp.write_single_register(112,15)  

                elif passo_torno==15:
                        print("Ciclo Torno Finalizado")
                        Main_clientCOp.write_single_register(112,16) 
                        time.sleep(0.1)
    
                elif passo_torno==16:
                        Main_clientCOp.write_single_coil(3,False)
                        loopTorno = False
                        print("Robô Liberado")                        #Torno CNC abre Porta
                        
        else:
            print("Posição Incorreta")
            pos_incorretaTorno=pos_incorretaTorno+1
            time.sleep(1)
            if(pos_incorretaTorno>5):
                Main_clientCOp.write_single_coil(3,False)
                print("Robô Liberado Torno")
                loopCentro = False
                pos_incorretaTorno=0

    
                
###########################  ROBÔ LIBERADO


 
def Usinar_CENTRO():
    loopCentro = True 
    #print("Usinar_CENTRO")
    while(loopCentro == True ): 
        PosicaoAtual_AMR= amr_client.read_input_registers(33,1)[0] #Posicao Atual do AMR
        if (PosicaoAtual_AMR==9):
                pos_incorretaCentroUsinagem=0
                passo_CentroUsinagem =  Main_clientCOp.read_holding_registers(111,1)[0]                     #Armazena o numero da Operação atual de usinagem no Centro de Usinagem
                print("Usinar Centro:" +str(passo_CentroUsinagem))     
                if passo_CentroUsinagem==0: 
                            Peca_04 = Main_client.read_holding_registers(14,1)[0]
                            Peca_05 = Main_client.read_holding_registers(15,1)[0]   #Status peca 5
                            #if((Peca_04==False) and (Peca_05==False)):
                            #print("CentroUsinagem")
                            if (EstadoDaPorta() ==False):
                                CR_Abrir_Porta()                          #CENTRO CNC abre Porta
                            VerificarPorta_Aberta()
                            Centro_Abre_Morsa()                             #Centro de Usinagem abre Morça
                            Main_clientCOp.write_single_register(111,1)     #Passo seguinte
                            #else:
                                #print("Aguradando Reposição Peça P4 e P5" )
                                            
                elif passo_CentroUsinagem==1: #pega peça na base e coloca na morsa
                            CR_atividade(30)                                #CR coloca peça na morça
                            CR_AbrirGarra_2()                               #CR ABRE garra 
                            Centro_Fecha_Morsa()
                            #CR_AbrirGarra_2()                               #CR ABRE garra 
                            CR_atividade(31)                                #sai da posição da morça peça primeiro Lado garra 2
                            PecaAtual_CENTRO=Main_clientCOp.read_holding_registers(2,1)[0]  #Verifica qual peça esta fazendo no CENTRO
                            CENTROUSINAGEMCNC_SelecionarPrograma(PecaAtual_CENTRO)        #Torno CNC seleciona Progra para operar
                            time.sleep(0.2)
                            CR_Fechar_Porta()  #Fechar porta ja esta com a movimentação de dar o start
                            #CENTROUSINAGEMCNC_IniciaUsinagem()
                            Main_clientCOp.write_single_register(111,2)  #Passo seguinte
                            Main_clientCOp.write_single_coil(3,False)
                            time.sleep(0.2)
                            print("Robô Liberado")
                            irparaposicaoDireto(4)
                            loopCentro = False 

                elif passo_CentroUsinagem==2:
                            CentroUsinagem_clientOp = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True) #IP do torno CNC
                            time.sleep(0.1)
                            try: # Aguardando Ausinagem
                                Centro_Status_Pause =CentroUsinagem_clientOp.read_coils(23,1)[0]     #Verifica se a maquina esta em pause
                                time.sleep(0.2)
                                Centro_Status_IniciFIM =CentroUsinagem_clientOp.read_coils(22,1)[0]  #Verifica se o programa foi finalizado
                                time.sleep(0.2)
                                print("AGUARDANDO USINAGEM CENTRO")
                                if(Centro_Status_Pause==True or Centro_Status_IniciFIM==False):
                                    Main_clientCOp.write_single_register(111,3)         #Passo seguinte 
                                else:Main_clientCOp.write_single_coil(3,False)
                                
                            except:
                                print("erro modbus Centro Usinagem")
                                logging.error("erro modbus Centro Usinagem")   
                        

                elif passo_CentroUsinagem==3:
                            CR_Abrir_Porta()                                #CENTRO CNC abre Porta
                            CR_atividade(34)                                #ROBO PEGA PEÇA PARA VIRAR
                            CR_Fechar_Porta()
                            #CENTROUSINAGEMCNC_IniciaUsinagem()
                            Main_clientCOp.write_single_register(111,4)  #Passo seguinte
                            Main_clientCOp.write_single_coil(3,False)
                            time.sleep(0.2)
                            print("Robô Liberado")
                            irparaposicaoDireto(4)
                            loopCentro = False

                elif passo_CentroUsinagem==4:
                            CentroUsinagem_clientOp = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True) #IP do torno CNC
                            time.sleep(0.1)
                            try: # Aguardando Ausinagem
                                Centro_Status_Pause =CentroUsinagem_clientOp.read_coils(23,1)[0]     #Verifica se a maquina esta em pause
                                time.sleep(0.2)
                                Centro_Status_IniciFIM =CentroUsinagem_clientOp.read_coils(22,1)[0]  #Verifica se o programa foi finalizado
                                time.sleep(0.2)
                                print("AGUARDANDO USINAGEM CENTRO")
                                if(Centro_Status_Pause==True or Centro_Status_IniciFIM==False):
                                    Peca_04 = Main_client.read_holding_registers(14,1)[0]
                                    Peca_05 = Main_client.read_holding_registers(15,1)[0]   #Status peca 5

                                    if((Peca_04==False) and (Peca_05==False)) or ((Peca_04==True) and (Peca_05==False)) :
                                        Main_clientCOp.write_single_register(111,5)         #Passo seguinte
                                    else: 
                                        irparaposicao(4)
                                        Main_clientCOp.write_single_coil(3,False)
                                        print("Aguardando Finalizacao de P4")
                                        loopCentro = False
                                else:Main_clientCOp.write_single_coil(3,False)

                            except:
                                print("erro modbus Centro")
                                logging.error("erro modbus Centro Usinagem")
                            

                elif passo_CentroUsinagem==5:  
                            PecaAtual_CENTRO=Main_clientCOp.read_holding_registers(2,1)[0]  #Verifica qual peça esta fazendo no CENTRO
                            #CR_Abrir_Porta()                              #CENTRO CNC abre Porta
                            if (PecaAtual_CENTRO==2):
                                
                                PecaAtual_CENTRO=Main_clientCOp.read_holding_registers(2,1)[0]  #Verifica qual peça esta fazendo no CENTRO
                                time.sleep(0.2)
                                PecaAtual_CENTRO=PecaAtual_CENTRO-1
                                Main_clientCOp.write_single_register(2,PecaAtual_CENTRO)     #Escreve peça esta fazendo no TORNO atual
                                time.sleep(0.2)
                                PecaAtual_CENTRO=Main_clientCOp.read_holding_registers(2,1)[0]  #Verifica qual peça esta fazendo no CENTRO
                                time.sleep(0.2)
                                CENTROUSINAGEMCNC_SelecionarPrograma(PecaAtual_CENTRO)        #Torno CNC seleciona Progra para operar
                                time.sleep(1)
                                print("Aqui3:"+ str(PecaAtual_CENTRO))
                                CR_atividade(36) #Modificado Realizar operacao de conjunta pegar aluminoo e tirar P5
                            else:  
                                PecaAtual_CENTRO=Main_clientCOp.read_holding_registers(2,1)[0]  #Verifica qual peça esta fazendo no CENTRO
                                time.sleep(0.2)
                                PecaAtual_CENTRO=PecaAtual_CENTRO-1
                                Main_clientCOp.write_single_register(2,PecaAtual_CENTRO)     #Escreve peça esta fazendo no TORNO atual
                                time.sleep(0.2)
                                PecaAtual_CENTRO=Main_clientCOp.read_holding_registers(2,1)[0]  #Verifica qual peça esta fazendo no CENTRO
                                time.sleep(0.2)
                                CENTROUSINAGEMCNC_SelecionarPrograma(PecaAtual_CENTRO)        #Torno CNC seleciona Progra para operar
                                time.sleep(0.2)
                                CR_atividade(35)                           #ROBO PEGA NA BASE DO AMR A  P5  E  PEGA P4 PRONTA
                                

                            PecaAtual_CENTRO=Main_clientCOp.read_holding_registers(2,1)[0]  #Verifica qual peça esta fazendo no CENTRO
                            if (PecaAtual_CENTRO==2):
                                #CENTROUSINAGEMCNC_SelecionarPrograma(PecaAtual_CENTRO)        #Torno CNC seleciona Progra para operar
                                #CR_Fechar_Porta()
                                #CENTROUSINAGEMCNC_IniciaUsinagem()
                                Main_clientCOp.write_single_register(111,2)
                                Main_clientCOp.write_single_coil(3,False)
                                time.sleep(0.5)
                                print("Robô Liberado")
                                time.sleep(0.5)
                                irparaposicaoDireto(4)
                                time.sleep(0.5)
                                loopCentro = False
                            else:
                                Peca_03 = Main_client.read_holding_registers(13,1)[0] 
                                if(Peca_03==False):
                                    #Main_clientCOp.write_single_register(111,6)
                                    Main_clientCOp.write_single_register(111,7)  #Modificado Realizar operacao de conjunta pegar aluminoo e tirar P5
                                    Main_clientCOp.write_single_coil(3,False)
                                    time.sleep(0.5)
                                    irparaposicaoDireto(4)
                                    loopCentro = False
       
                
                elif passo_CentroUsinagem==6:
                        PecaAtual_CENTRO=Main_clientCOp.read_holding_registers(2,1)[0]  #Verifica qual peça esta fazendo no CENTRO
                        CENTROUSINAGEMCNC_SelecionarPrograma(PecaAtual_CENTRO)        #Torno CNC seleciona Progra para operar
                        CR_atividade(37)                               #PEGA PEÇA DE ALUMINIO
                        CR_AbrirGarra_2()                              #CR ABRE garra 
                        Centro_Fecha_Morsa()                           #Centro CNC Fecha Morça
                        CR_atividade(38)                               #ROBO sai da morsa após colocar peça de aluminio 
                        CR_Fechar_Porta()
                        #CENTROUSINAGEMCNC_IniciaUsinagem()
                        Main_clientCOp.write_single_coil(3,False)
                        time.sleep(0.1)
                        print("Robô Liberado") 
                        Main_clientCOp.write_single_register(111,7)
                        irparaposicaoDireto(4)
                        loopCentro = False
                
                elif passo_CentroUsinagem==7:
                            CentroUsinagem_clientOp = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True) #IP do torno CNC
                            time.sleep(0.1)
                            try: # Aguardando Ausinagem
                                Centro_Status_Pause =CentroUsinagem_clientOp.read_coils(23,1)[0]     #Verifica se a maquina esta em pause
                                time.sleep(0.2)
                                Centro_Status_IniciFIM =CentroUsinagem_clientOp.read_coils(22,1)[0]  #Verifica se o programa foi finalizado
                                time.sleep(0.2)
                                print("AGUARDANDO USINAGEM CENTRO")

                                if(Centro_Status_Pause==True or Centro_Status_IniciFIM==False):
                                    Main_clientCOp.write_single_register(111,8)         #Passo seguinte 
                                else:Main_clientCOp.write_single_coil(3,False)
                            except:
                                print("erro modbus Centro")
                                logging.error("erro modbus Centro Usinagem")

                
                elif passo_CentroUsinagem==8:
                        CR_Abrir_Porta() 
                        CR_atividade(39)                                    #ROBO  peGa de alumino pronta e coloca para realizar rosca
                        Main_clientCOp.write_single_register(111,9)         #Passo seguinte                   
                        CR_Fechar_Porta()
                        Main_clientCOp.write_single_coil(3,False)
                        time.sleep(0.2)
                        print("Robô Liberado") 
                        #irparaposicao(4)
                        loopCentro = False

                elif passo_CentroUsinagem==9:
                            CentroUsinagem_clientOp = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True) #IP do torno CNC
                            time.sleep(0.1)
                            try: # Aguardando Ausinagem
                                Centro_Status_Pause =CentroUsinagem_clientOp.read_coils(23,1)[0]     #Verifica se a maquina esta em pause
                                time.sleep(0.2)
                                Centro_Status_IniciFIM =CentroUsinagem_clientOp.read_coils(22,1)[0]  #Verifica se o programa foi finalizado
                                time.sleep(0.2)
                                print("AGUARDANDO USINAGEM CENTRO")
                                
                                if(Centro_Status_Pause==True or Centro_Status_IniciFIM==False):
                                    Main_clientCOp.write_single_register(111,10)         #Passo seguinte 
                                else:Main_clientCOp.write_single_coil(3,False)

                            except:
                                print("erro modbus Centro")
                                logging.error("erro modbus Centro Usinagem")

                
                elif passo_CentroUsinagem==10:
                        CR_Abrir_Porta() 
                        CR_atividade(40)                               #ROBO  peGa de alumino pronta
                        Main_clientCOp.write_single_register(111,11)         #Passo seguinte                   
                    
                elif passo_CentroUsinagem==11:
                        print("Ciclo Centro Finalizado")
                        Main_clientCOp.write_single_register(111,12) 
                        time.sleep(0.1)
    
                elif passo_CentroUsinagem==12: 
                        #Main_clientCOp.write_single_coil(3,False)
                        time.sleep(0.5)
                        Main_clientCOp.write_single_register(111,20) 
                        print("Robô Centro Liberado") 

                elif passo_CentroUsinagem==20: 
                        Main_clientCOp.write_single_coil(3,False)
                        print("Robô Liberado CentroUsinagem_ Passo20")
                        loopCentro = False     
        else:
            print("Posição Incorreta")
            pos_incorretaCentroUsinagem=pos_incorretaCentroUsinagem+1
            time.sleep(1)
            if(pos_incorretaCentroUsinagem>5):
                Main_clientCOp.write_single_coil(3,False)
                print("Robô Liberado CentroUsinagem_ Passo20")
                loopCentro = False
                pos_incorretaCentroUsinagem=0

            

