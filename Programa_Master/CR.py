from pyModbusTCP.client import ModbusClient
from AMR import *
from Gerenciamento import *
import time

#from Kanban_Inspecao import *

WAIT_DELAY = 0.2
CR_client = ModbusClient(host="192.168.192.6", port=502, unit_id=1, auto_open=True) #IP do CR
Main_clientCR = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True)  #IP local
verifica_retornoCR=0



def CR_AbrirGarra_1():
     CR_client.write_single_register(6,6)
     time.sleep(0.)
     CR_Status =CR_client.read_holding_registers(7,1)[0]
     print("AguardandoMov_CR Abrir Garra1")
     while CR_Status != 0:
                    CR_Status =CR_client.read_holding_registers(7,1)[0]
                    time.sleep(0.5)
     print("Garra Aberta")
     
#CR_AbrirGarra()
def CR_FecharGarra_1():
     CR_client.write_single_register(6,7)
     time.sleep(0.5)
     CR_Status =CR_client.read_holding_registers(7,1)[0]
     print("AguardandoMov_CR fechar Garra1")
     while CR_Status != 0:
                    CR_Status =CR_client.read_holding_registers(7,1)[0]
                    time.sleep(0.5)
     print("Garra Fechar")

def CR_AbrirGarra_2():
     CR_client.write_single_register(6,8)
     time.sleep(0.5)
     CR_Status =CR_client.read_holding_registers(7,1)[0]
     print("AguardandoMov_CR Abrir Garra2")
     while CR_Status != 0:
                    CR_Status =CR_client.read_holding_registers(7,1)[0]
                    time.sleep(0.5)
     print("Garra Abrir")

#CR_AbrirGarra()
def CR_FecharGarra_2():
     CR_client.write_single_register(6,9)
     time.sleep(0.5)
     CR_Status =CR_client.read_holding_registers(7,1)[0]
     print("AguardandoMov_CR fechar Garra2")
     while CR_Status != 0:
                    CR_Status =CR_client.read_holding_registers(7,1)[0]
                    time.sleep(0.5)
     print("Garra Fechar")



def CR_atividade(valor) -> int:
    global verifica_retornoCR
    erroCR=False
    if ((valor==10)):
            Main_clientCR.write_single_register(6,valor)
            CR_Status =CR_client.read_holding_registers(7,1)[0]
            CR_client.write_single_register(6,valor)
            time.sleep(1)
            print("Aguardando_Mov_CR"+str(valor)) #"\n"
            CR_Status =CR_client.read_holding_registers(7,1)[0]
            while CR_Status != 0:
                    CR_Status =CR_client.read_holding_registers(7,1)[0]
                    time.sleep(0.5)
                    CR_STATUS(0)
            print("Finalizado_Mov_CR"+str(valor))#"\n"
            pass
    else:
        while True:  # reinicia em caso de timeout
            verifica_retornoCR = 0
            CR_Modo = CR_client.read_input_registers (1012, 1)[0]
            while CR_Modo !=7:
                time.sleep(1)
                CR_Modo = CR_client.read_input_registers (1012, 1)[0]
                print("Aguardando CR RUN"+str(CR_Modo))

            Main_clientCR.write_single_register(7, 0) 
            CR_Status =CR_client.read_holding_registers(7,1)[0]   
            while CR_Status !=0:        
             Main_clientCR.write_single_register(7, 0)
             CR_Status =CR_client.read_holding_registers(7,1)[0]
             Main_clientCR.write_single_register(7, 0) 
             time.sleep(1)
             print("RESET")
           

            # envia comando inicial
            if ((valor!=10)):
                Main_clientCR.write_single_register(6,valor)


            CR_Status =CR_client.read_holding_registers(7,1)[0]
            CR_client.write_single_register(6,valor)
            time.sleep(1)

            # -----------------------------
            # 1) Verifica se o movimento iniciou
            # -----------------------------
            inicio_tentativas = 0
            while CR_Status == 0:
                Main_clientCR.write_single_register(6, valor)
                time.sleep(1)
                CR_Status = CR_client.read_holding_registers(7, 1)[0]
                PassoCR =  CR_client.read_holding_registers(6, 1)[0] 
                inicio_tentativas += 1
                print("Tentando iniciar movimento CR " + str(valor))
                #if((CR_Status==0 ) and (PassoCR==10)):
                    #print("Posição segura CR " + str(valor))
                    #return 0

                if inicio_tentativas > 10:  # por exemplo, 10 segundos tentando iniciar
                    print("⚠️ Movimento não iniciou, reiniciando...")
                    break  # reinicia o while True

            if CR_Status == 0:
                continue  # reinicia while True se não começou

            print("Movimento iniciado, aguardando finalizar...")

            # -----------------------------
            #
            # 2) Aguarda finalizar movimento  
            # 7 Run|  9 Colisao| 5 Programa Parado| 6 Dreg Ativado |4 DESLIGADO
            # -----------------------------
            while CR_Status != 0:
                Main_clientCR.write_single_register(6, valor)
                time.sleep(1)
                CR_Status = CR_client.read_holding_registers(7, 1)[0]
                
                CR_Modo = CR_client.read_input_registers (1012, 1)[0]
                #print("CR_Modo:" + str(CR_Modo))
                #verifica_retornoCR += 1
                if CR_Modo !=7:
                    verifica_retornoCR += 1
                if verifica_retornoCR > 30:
                    print("⚠️ Timeout - reiniciando processo CR_atividade...")
                    Main_clientCR.write_single_register(7, 0)
                    time.sleep(1)
                    break  # reinicia while True
            else:
                # Finalizou corretamente
                print("Finalizado_Mov_CR " + str(valor)) # "\n"

                # -------------------------
                # AÇÕES ESPECÍFICAS POR VALOR
                # -------------------------

                if valor == 20:
                    Main_clientCR.write_single_register(16, 1)
                    Main_clientGer.write_single_register(17, 1)

                elif valor == 25:
                    Main_clientCR.write_single_register(11, 1)

                elif valor == 26:
                    Main_clientCR.write_single_register(12, 1)

                elif valor == 40:
                    Main_clientCR.write_single_register(13, 1)

                    Prod = Main_clientCR.read_holding_registers(36, 1)[0]
                    Main_clientCR.write_single_register(36, Prod + 1)

                elif valor == 35:
                    Main_clientCR.write_single_register(14, 1)
                    
                    Main_clientCR.write_single_register(25, 1)
                    Prod = Main_clientCR.read_holding_registers(35, 1)[0]
                    Main_clientCR.write_single_register(35, Prod + 1)


                elif valor == 36:
                    Main_clientCR.write_single_register(15, 1)
                    time.sleep(0.2)
                    Main_clientCR.write_single_register(17, 0)
                    time.sleep(0.2)

                elif valor == 12:
                    Main_clientCR.write_single_register(23, 1)
                    time.sleep(0.2)
                    Main_clientCR.write_single_register(17, 0)
                    time.sleep(0.2)
                    Prod = Main_clientCR.read_holding_registers(33, 1)[0]
                    Main_clientCR.write_single_register(33, Prod + 1)

                elif valor == 18:
                    Main_clientCR.write_single_register(22, 1)
                    Prod = Main_clientCR.read_holding_registers(32, 1)[0]
                    Main_clientCR.write_single_register(32, Prod + 1)

                elif valor == 22:
                    Main_clientCR.write_single_register(21, 1)
                    Prod = Main_clientCR.read_holding_registers(31, 1)[0]
                    Main_clientCR.write_single_register(31, Prod + 1)

                elif valor == 30:
                    Main_clientCR.write_single_register(24, 1)
                    Prod = Main_clientCR.read_holding_registers(34, 1)[0]
                    Main_clientCR.write_single_register(34, Prod + 1)

    

                # fim do loop externo → função retorna
                return 0


def CR_Abrir_Porta():
     CR_client.write_single_register(6,32)
     time.sleep(0.5)
     CR_Status =CR_client.read_holding_registers(7,1)[0]
     print("Aguardando Mov_CR Abrir Porta")
     while CR_Status != 0:
                    CR_Status =CR_client.read_holding_registers(7,1)[0]
                    time.sleep(0.5)
                    
     print("Mov_CR Abrir Porta Realizado")

def CR_Fechar_Porta():
     CR_client.write_single_register(6,33)
     time.sleep(0.5)
     CR_Status =CR_client.read_holding_registers(7,1)[0]
     print("Aguardando Mov_CR Fechar Porta")
     while CR_Status != 0:
                    CR_Status =CR_client.read_holding_registers(7,1)[0]
                    time.sleep(0.5)
                    
     print("Mov_CR Fechar Porta Realizado")


def CR_Inicia_Usinagem_Centro():
     CR_client.write_single_register(6,34)
     time.sleep(0.5)
     CR_Status =CR_client.read_holding_registers(7,1)[0]
     print("Aguardando Mov_CR Iniciar Programa")
     while CR_Status != 0:
                    CR_Status =CR_client.read_holding_registers(7,1)[0]
                    time.sleep(0.5)
                    
     print("Mov_CR Fechar Programa Iniciado")
