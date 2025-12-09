from pyModbusTCP.client import ModbusClient
import time
TornoCNC_client_Op = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC
Main_clientTor = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True)  


def iniciar_Torno():
     TornoCNC_client_Op.write_single_coil(0,1)  #SELEÇÃO DO RESET
     time.sleep(1)
     TornoCNC_client_Op.write_single_coil(0,0)  #SELEÇÃO DO RESET
     time.sleep(1)
#iniciar_Torno()


#TORNO_Fechar_Porta()
def TORNO_Fechar_Porta():
    TornoCNC_client_Op.write_single_coil(12,False)
    time.sleep(0.2)
    TornoCNC_client_Op.write_single_coil(13,True)
    time.sleep(0.2)
    TornoCNC_client_Op.write_single_coil(13,False)
    time.sleep(0.2)
    Status_Porta_S1 =TornoCNC_client_Op.read_coils(27,1)[0]
    print("AGUARDANDO FECHAR PORTA")
    while(Status_Porta_S1==False):
        TornoCNC_client_Op.write_single_coil(12,False)
        time.sleep(0.2)
        TornoCNC_client_Op.write_single_coil(13,True)
        time.sleep(0.3)
        TornoCNC_client_Op.write_single_coil(13,False)
        time.sleep(0.2)
        Status_Porta_S1 =TornoCNC_client_Op.read_coils(27,1)[0]
        time.sleep(0.2)

    TornoCNC_client_Op.write_single_coil(13,False)
    time.sleep(0.1)
    print("PORTA FECHADA")

#TORNO_Abre_Porta()
def TORNO_Abrir_Porta():
    Verificacao=True
    while(Verificacao):
        try:
            TornoCNC_client_Op.write_single_coil(13,False)
            time.sleep(0.2)
            TornoCNC_client_Op.write_single_coil(12,True)
            time.sleep(0.3)
            TornoCNC_client_Op.write_single_coil(12,False)
            time.sleep(0.2)
            Status_Porta_S1 =TornoCNC_client_Op.read_coils(26,1)[0]
            print("AGUARDANDO ABRIR PORTA")
            while(Status_Porta_S1==False):
                TornoCNC_client_Op.write_single_coil(13,False)
                time.sleep(0.2)
                TornoCNC_client_Op.write_single_coil(12,True)
                time.sleep(0.3)
                TornoCNC_client_Op.write_single_coil(12,False)
                time.sleep(0.2)
                Status_Porta_S1 =TornoCNC_client_Op.read_coils(26,1)[0]
                time.sleep(0.2)

            TornoCNC_client_Op.write_single_coil(12,False)
            time.sleep(0.1)
            Verificacao=False
            print("PORTA ABERTA")
        except:
            print("Erro ABRIR PORTA")

#TORNO_Abre_Porta()
def TORNO_Abrir_Porta_sem_checar():
    TornoCNC_client_Op.write_single_coil(13,False)
    TornoCNC_client_Op.write_single_coil(12,True)
    time.sleep(0.2)
    TornoCNC_client_Op.write_single_coil(12,False)
    #Status_Porta_S1 =TornoCNC_client_Op.read_coils(26,1)[0]
    TornoCNC_client_Op.write_single_coil(12,False)

def AjustesPecaNa_Placa():
    TornoCNC_client_Op.write_single_coil(6,True)
    TornoCNC_client_Op.write_single_coil(5,False)
    time.sleep(2)
    TornoCNC_client_Op.write_single_coil(5,True)
    TornoCNC_client_Op.write_single_coil(6,False)

    time.sleep(1)
    TornoCNC_client_Op.write_single_coil(6,True)
    TornoCNC_client_Op.write_single_coil(5,False)
    time.sleep(1)
    TornoCNC_client_Op.write_single_coil(5,True)
    TornoCNC_client_Op.write_single_coil(6,False)
    time.sleep(1)
    TornoCNC_client_Op.write_single_coil(6,True)
    TornoCNC_client_Op.write_single_coil(5,False)



#TORNO_Abrir_Placa()
def TORNO_Fechar_Placa():
    time.sleep(0.2)
    TornoCNC_client_Op.write_single_coil(6,True)
    TornoCNC_client_Op.write_single_coil(5,False)
    time.sleep(0.2)
    Status_Placa_S1 =TornoCNC_client_Op.read_coils(25,1)[0]
    Status_Placa_S2 =TornoCNC_client_Op.read_coils(25,1)[0]
    print("AGUARDANDO FECHAR PLACA")
    while(Status_Placa_S1==False or Status_Placa_S2==False):
        Status_Placa_S1 =TornoCNC_client_Op.read_coils(25,1)[0]
        Status_Placa_S2 =TornoCNC_client_Op.read_coils(25,1)[0]
        time.sleep(0.2)
        TornoCNC_client_Op.write_single_coil(6,True)
        TornoCNC_client_Op.write_single_coil(5,False)

    TornoCNC_client_Op.write_single_coil(6,False)
    time.sleep(0.2)
    print("PLACA FECHADA")
#TORNO_Fechar_Placa()

def TORNO_Abre_Placa_sem_checar():
    TornoCNC_client_Op.write_single_coil(5,True)
    TornoCNC_client_Op.write_single_coil(6,False)
    time.sleep(0.5)


def TORNO_Abre_Placa():
    time.sleep(0.2)
    TornoCNC_client_Op.write_single_coil(5,True)
    TornoCNC_client_Op.write_single_coil(6,False)
    time.sleep(0.2)
    Status_Placa_S1 =TornoCNC_client_Op.read_coils(25,1)[0]
    Status_Placa_S2 =TornoCNC_client_Op.read_coils(25,1)[0]
    print("AGUARDANDO ABRIR PLACA")
    while(Status_Placa_S1==True or Status_Placa_S2==True ):
        Status_Placa_S1 =TornoCNC_client_Op.read_coils(25,1)[0]
        Status_Placa_S2 =TornoCNC_client_Op.read_coils(25,1)[0]
        time.sleep(0.2)
        TornoCNC_client_Op.write_single_coil(5,True)
        TornoCNC_client_Op.write_single_coil(6,False)
    TornoCNC_client_Op.write_single_coil(5,False)
    time.sleep(0.2)
    print("PLACA ABERTA")
#TORNO_Abre_Placa()
#SELECIONAR QUAL PROGRAMA VAI RODAR
def TORNOCNC_SelecionarPrograma(valor)-> int:
     Main_clientTor.write_single_register(113,valor) #Programa atual sendo executado no Torno
     try:
       TornoCNC_client_Op = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC
       time.sleep(0.5)
     except:
       print("erro modbus Torno selecao do programa")
     Main_clientTor.write_single_register(113,valor) #Programa atual sendo executado no Torno
     TornoCNC_client_Op.write_single_coil(9,False) #SELEÇÃO DO PROGRAMA 1
     time.sleep(0.1)
     TornoCNC_client_Op.write_single_coil(10,False) #SELEÇÃO DO PROGRAMA 2
     time.sleep(0.1)
     TornoCNC_client_Op.write_single_coil(11,False) #SELEÇÃO DO PROGRAMA 3

     if valor==1:
        TornoCNC_client_Op.write_single_coil(9,True) #SELEÇÃO DO PROGRAMA 1 
        time.sleep(0.1)
        print("Programa Torno CNC Selecionado: " + str (valor))
     if valor==2:
        TornoCNC_client_Op.write_single_coil(10,True) #SELEÇÃO DO PROGRAMA 2
        time.sleep(0.1)
        print("Programa Torno CNC Selecionado: " + str (valor))
     if valor==3:
        TornoCNC_client_Op.write_single_coil(11,True) #SELEÇÃO DO PROGRAMA 3
        time.sleep(0.1)
        print("Programa Torno CNC Selecionado: " + str (valor))
        
     Programa = [9,10,11]
     while TornoCNC_client_Op.read_coils(Programa[valor-1], 1)[0] == False:
         time.sleep(0.2)
         print("Aguardando Set de Programa" +str(TornoCNC_client_Op.read_coils(Programa[valor], 1)[0])+str(Programa[valor-1]))


     TornoCNC_client_Op.write_single_coil(2,True) #SELEÇAO DO MODO AUTO
     TornoCNC_client_Op.write_single_coil(9,False) #SELEÇÃO DO PROGRAMA 1
     TornoCNC_client_Op.write_single_coil(10,False) #SELEÇÃO DO PROGRAMA 2
     TornoCNC_client_Op.write_single_coil(11,False) #SELEÇÃO DO PROGRAMA 3
     TornoCNC_client_Op.write_single_coil(2,False) #SELEÇAO DO MODO AUTO
     #time.sleep(0.5)


#TORNO_IniciaUsinagem()
def TORNO_IniciaUsinagem():
     #TornoCNC_client_Op.write_single_coil(9,True) #SELEÇÃO DO PROGRAMA 1
     TornoCNC_client_Op.write_single_coil(2,True) #SELEÇAO DO MODO AUTO
     time.sleep(0.2)
     #TornoCNC_client_Op.write_single_coil(9,False) #SELEÇÃO DO PROGRAMA 1
     TornoCNC_client_Op.write_single_coil(2,False) #SELEÇAO DO MODO AUTO
     time.sleep(0.2)
     TornoCNC_client_Op.write_single_coil(3,True) #START DE PROGRAMA
     time.sleep(0.2)
     TornoCNC_client_Op.write_single_coil(3,False) #START DE PROGRAMA
     



#ALTERAR SENTIDO DE APERTURA DE PLACA INVERTIDA
def TORNO_AlterarSentidodePlaca():
    TornoCNC_client_Op = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC
    time.sleep(0.1)
    Status_Sentido_Placa =TornoCNC_client_Op.read_coils(20,1)[0]
    time.sleep(0.1)
    #print(Status_Sentido_Placa)
    confirmacao=0
    if (Status_Sentido_Placa==False):
        print("AGUARDANDO MUDAR SENTIDO DE PLACA") #+str(Status_Sentido_Placa)+str(confirmacao))
        while(Status_Sentido_Placa==False or confirmacao <2 ):
            Status_Sentido_Placa =TornoCNC_client_Op.read_coils(20,1)[0]
            if(Status_Sentido_Placa==True):
                confirmacao=confirmacao+1
                time.sleep(0.5)
            else:
                confirmacao=0
                TornoCNC_client_Op.write_single_coil(4,True) #START DE PROGRAMA
                time.sleep(0.2)
                TornoCNC_client_Op.write_single_coil(4,False) #START DE PROGRAMA
                time.sleep(2)
  

#ALTERAR SENTIDO DE APERTURA DE PLACA NORMAL
def TORNO_AlterarPlacNORMAL():
    TornoCNC_client_Op = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC
    time.sleep(0.1)
    Status_Sentido_Placa =TornoCNC_client_Op.read_coils(20,1)[0]
    time.sleep(0.1)
    #print(Status_Sentido_Placa)
    confirmacao=0
    if (Status_Sentido_Placa==True):
        print("AGUARDANDO MUDAR SENTIDO DE PLACA") #+str(Status_Sentido_Placa)+str(confirmacao))
        while(Status_Sentido_Placa==True or confirmacao <2 ):
            Status_Sentido_Placa =TornoCNC_client_Op.read_coils(20,1)[0]
            if(Status_Sentido_Placa==False):
                confirmacao=confirmacao+1
                time.sleep(0.5)
            else:
                confirmacao=0
                TornoCNC_client_Op.write_single_coil(4,True) #Mudança de operacçao de modo de Placa 
                time.sleep(0.2)
                TornoCNC_client_Op.write_single_coil(4,False) #Mudança de operacçao de modo de Placa 
                time.sleep(1)
    

