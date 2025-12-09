'''
Status_TORNO_Pause == False           --> Torno Pausado Esperando AMR
Status_CentroUsinagem_Pause == False  --> Centro Pausado Esperando AMR
Status_CentroUsinagem_Parado == True  --> Torno parado sem programa em execucao
Status_TORNO_Parado == True           --> Centro parado sem programa em execucao
EM_Atividade == False                 --> AMR livre

################################################################################  JSON  ####################################################
################################################################################        ####################################################

NivelBateriaAMR: "ValorNivelBateria"

PosicaoAMR: "ValorPosiçãoDoAMR"
 
PassoCR: "ValorPassoReealizadoPeloCR"

AMR_Abastecido: "SeABaseDoAMRfoiAbastecidoComPeças"

St_Producao: [P1, P2, P31Stagio, P4, P5, P3]
    P1 = "false" -> Não Produzida, "true" -> Produzida
    P2 = "false" -> Não Produzida, "true" -> Produzida
    P31Stagio3 = "false" -> Não Produzida, "true" -> Produzida
    P4 = "false" -> Não Produzida, "true" -> Produzida
    P5 = "false" -> Não Produzida, "true" -> Produzida

Inspecao: ["PassoParaRealizarInspeçãoTorno", "SeJáFoiRealizadoTorno", "PassoParaRealizarInspeçãoTorno", "SeJáFoiRealizadoCentro"],
    PassoParaRealizarInspeçãoTorno -> passo do torno em quevai parar para realizar verificação na Tridimensional
    SeJáFoiRealizadoTorno   -> "false" -> Não Realizado, "true" -> Realizado
    PassoParaRealizarInspeçãoCentro  -> passo do centro em quevai parar para realizar verificação na Tridimensional
    SeJáFoiRealizadoCentro ->  "false" -> Não Realizado, "true" -> Realizado

StatusDeMaquina: ["TornoPause", "TornoOperando", "CentroPause", "CentroOperando"]
    TornoPause = "false" -> Esta em Pause esperando ação do CR, "true" -> Em modo de funcionamento
    TornoOperando= "false" -> Esta parado, "true" -> Em modo de funcionamento
    CentroPause = "false" -> Esta em Pause esperando ação do CR, "true" -> Em modo de funcionamento
    CentroOperando = "false" -> Esta parado, "true" -> Em modo de funcionamento

Kanban: ["RealizouKanbanP1/P2", "RealizouKanbanP3", "RealizouKanbanP4/P5"]
    RealizouKanbanP1/P2 = "false" -> Não realizou KanbanP1, "true" -> realizou KanbanP1
    RealizouKanbanP3 = "false" -> Não realizou KanbanP1, "true" -> realizou KanbanP1
    RealizouKanbanP4/P5 = "false" -> Não realizou KanbanP1, "true" -> realizou KanbanP1

PassoMaquinas: ["Estagio do ciclo de Operações do Torno", "Estagio do ciclo de Operações do Centro"]

ProgramaEmExecucaoCNC: [Programa em Execução no Torno, Programa em Execução no Centro]

Reposicao: [ReposiçãodeP1, ReposiçãodeP2, ReposiçãodeP3, ReposiçãodeP4, ReposiçãodeP5]
    ReposiçãodeP1 = "false" -> Não precisa de Reposição, "true" -> Precisa de Reposição
    ReposiçãodeP2 = "false" -> Não precisa de Reposição, "true" -> Precisa de Reposição
    ReposiçãodeP3 = "false" -> Não precisa de Reposição, "true" -> Precisa de Reposição
    ReposiçãodeP4 = "false" -> Não precisa de Reposição, "true" -> Precisa de Reposição
    ReposiçãodeP5 = "false" -> Não precisa de Reposição, "true" -> Precisa de Reposição

ContagemPedidoPecas": ["ContagemProgressiva","QuantidadeDoPedido,"P1", "P2", "P3_TORNO1Stagio", "P4", "P5", "P3Pronta"]

Timestamp: Timestamp

################################################################################  JSON  ####################################################

continue  # Volta para o início do while
break     # Sai do while completamente
'''


from AMR import *
from CR import *
from TornoCNC import *
from CentroUsinagem import *
from Gerenciamento import *
from Estacao_Buffer import *
from CicloDeOpecaracoes import *
from Kanban_Inspecao import *
import sys
import time
import requests
import json
import random
import logging
import signal
import atexit 
from datetime import datetime
from pyModbusTCP.client import ModbusClient
logging.root.handlers = []

import psycopg2
import os

#DEBUGADOR

#Banco de Dados
# Informações de conexão
host = "192.168.192.175"
port = "5432"
dbname = "postgres"
user = "postgres"
password = "postgres123"
try:
    # Conexão com o banco de dados
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    print("Conexão bem-sucedida!")
except Exception as e:
    print("Erro ao conectar ao banco de dados:", e)

#VARIAVEIS
Medicao_Tridimensiona_Torno = [10] #Torno e Centro Usinagem Medicao_Tridimensional = [21, 24, 26, 31]
Passo_Medicao_Tridimensional_Torno = random.choice(Medicao_Tridimensiona_Torno)

Medicao_Tridimensiona_CentroUsinagem = [7] #Torno e Centro Usinagem
Passo_Medicao_Tridimensional_CentroUsinagem = random.choice(Medicao_Tridimensiona_CentroUsinagem)


Bateria_AMR_bit1 = 0
Bateria_AMR_bit2 = 0
Peca_01 = 0                         #Status peca 1
Peca_02 = 0                         #Status peca 2
Peca_03 = 0                         #Status peca 5
Peca_04 = 0                         #Status peca 6
Peca_05 = 0                         #Status peca 3
Peca_03PRIMEIROEstagio  = 0         #Status peca 3 primeiro estagio
Passo_CR =0                         #passo do CR
PosicaoAtual_AMR =0                 #Posição do AMR
Status_TORNO_Pause=0
Status_TORNO_Parado=0
Status_CentroUsinagem_Pause=False
Status_CentroUsinagem_Parado=False
passo_torno=0
passo_CentroUsinagem=0
Status_KanbanTORNO=False
Status_KanbanCentroUsinagemManipulo=False
Status_KanbanCentroUsinagemCabeca =False

#reinicio de operaçao
Toogle_ProducaoBatentes=0
Toogle_ProducaoBatentes = Main_client.read_holding_registers(37,1)[0]

Toogle_ProducaoManipulo=0
Toogle_ProducaoManipulo = Main_client.read_holding_registers(38,1)[0]

Toogle_ProducaoPrimeiroEstagioCabeca=0
Toogle_ProducaoPrimeiroEstagioCabeca = Main_client.read_holding_registers(39,1)[0]

Toogle_ProducaoCabecaCentroUsinagemFIm=0
Toogle_ProducaoCabecaCentroUsinagemFIm = Main_client.read_holding_registers(40,1)[0]

Reset_Kanban = 0
Espera=False


# Configura o logger com formato e nível de log desejados
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', 
    level=logging.INFO, 
    filename='log_Fab40.log'
)


Main_client = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True)                  #IP local
CentroUsinagem_client = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True)   #IP do Centro de Usinagem
TornoCNC_client = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True)         #IP do torno CNC
CR_client = ModbusClient(host="192.168.192.6", port=502, unit_id=1, auto_open=True)                 #IP do CR
amr_client = ModbusClient(host="192.168.192.5", port=502, unit_id=1, auto_open=True)                #IP do AMR                                                                                    # Disconnect device



ArmazenaQnatPedida = 0
#Status Pedido
PedidoAtivoFila = True
Start_Pedido=False
Start_Pedido= bool(Main_client.read_coils(101,1)[0])  #Ordem para Iniciar Pedido
print("Start Pedido: " + str(Main_client.read_coils(101,1)[0]))
time.sleep(0.2)
#Pause Pedido
Pause_Pedido = False
Pause_Pedido=bool(Main_client.read_coils(102,1)[0])  #Ordem para Pausar Pedido  
print("Pause Pedido: " + str(Main_client.read_coils(102,1)[0]))
time.sleep(0.2)

#Ao encerar Tratar Equipamentos
# Executado ao sair normalmente
def ao_sair():
    #enviar_sinal_modbus(False)  # ou True, dependendo do significado
    print("Finalizando com segurança.")

# Executado em exceções
def tratamento_erro(exc_type, exc_value, traceback):
    print("Erro capturado:", exc_value)
    #enviar_sinal_modbus(False)
    sys.__excepthook__(exc_type, exc_value, traceback)

# Sinais do sistema (Ctrl+C, kill, etc.)
def sinal_encerramento(sig, frame):
    print(f"Sinal recebido: {sig}")
    #enviar_sinal_modbus(False)
    sys.exit(0)


# Registro
atexit.register(ao_sair)
sys.excepthook = tratamento_erro
signal.signal(signal.SIGINT, sinal_encerramento)   # Ctrl+C
signal.signal(signal.SIGTERM, sinal_encerramento)  # kill



def inicioJornada():
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password)
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE dados_gerais.pedidos SET quantidade_produzida = quantidade::INTEGER WHERE data_pedido::DATE < CURRENT_DATE;")
        conn.commit()
        time.sleep(0.2)
        print("Atualizado Registros Anteriores.")
    except:
        print("Sem registros Anteriores")

inicioJornada()

def finalizaUltimoPedido():
    try:
        conn2 = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password)
        serial = datetime.now().strftime("%Y%m%d%H%M%S")
        time.sleep(0.1)
        cursor2= conn2.cursor()
        time.sleep(0.1)
        cursor2.execute("SELECT MAX(id) FROM dados_gerais.pedidos WHERE quantidade_produzida::INTEGER = quantidade::INTEGER AND status <> '5';")
        resultado = cursor2.fetchone()
        time.sleep(0.1)
        cursor2.execute("UPDATE dados_gerais.pedidos SET cod_ratreamento = '" + str(serial) +"', status = 3  WHERE id =" + str(resultado[0])+";")
        conn2.commit()
    except:
        print("ERRO ATUALIZAR ULTIMO")    
#finalizaUltimoPedido()
#sys.exit() 

def finalizarOrdem(ID: int):
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dados_gerais.pedidos WHERE status = '1' AND status <> '5' AND id <"+ str(ID) +" ORDER BY id DESC OFFSET 0 LIMIT 1")
    resultado = cursor.fetchone()
    serial = datetime.now().strftime("%Y%m%d%H%M%S")
    cursor = conn.cursor()
    cursor.execute("UPDATE dados_gerais.pedidos SET  cod_ratreamento="+str(serial)+",status = 3  WHERE  id =" + str(resultado[0]))
    conn.commit()
    time.sleep(0.2)


def ObterQuantidadeAnterior():
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password)
    Antriror_Producao =0 
    try:
        conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password)

        cursor = conn.cursor()
        cursor.execute ("SELECT SUM(quantidade_produzida::INTEGER) AS total_pedidos FROM dados_gerais.pedidos WHERE data_pedido::DATE = CURRENT_DATE and quantidade_produzida::INTEGER <= quantidade::INTEGER AND status <> '5';")
        resultado = cursor.fetchone()
        time.sleep(0.1)
        Valor=resultado[0]
        if Valor==None:
            Antriror_Producao = 0
        else:
            Antriror_Producao = resultado[0]
    except:
        Antriror_Producao =0
        finalizaUltimoPedido()
        print("Erro Iniciar BD")
        
    return Antriror_Producao


print("Aterior: " +str(ObterQuantidadeAnterior()))
if(int(Main_client.read_holding_registers(30,1)[0])>0):
    valorArmazenado = Main_client.read_holding_registers(30,1)[0]
    valorProducao =int(int(ObterQuantidadeAnterior()) + (int(valorArmazenado))-(int(int(ObterQuantidadeAnterior()))))
    if (int(valorArmazenado)==int(ObterQuantidadeAnterior())):
        finalizaUltimoPedido()
else: 
    valorProducao =int(int(ObterQuantidadeAnterior()))
    

Main_client.write_single_register(30,valorProducao)

Main_client.write_single_register(31,valorProducao)
Main_client.write_single_register(32,valorProducao)
Main_client.write_single_register(33,valorProducao)
Main_client.write_single_register(34,valorProducao)
Main_client.write_single_register(35,valorProducao)
Main_client.write_single_register(36,valorProducao)
print("VerificaInicio36: " + str(Main_client.read_holding_registers(36,1)[0]))

time.sleep(0.2)
print("Produzido: " + str(Main_client.read_holding_registers(30,1)[0]))

def ObterDadosPedido():
    conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password)
    try:
        cursor = conn.cursor()
        cursor.execute ("SELECT MIN(id) FROM dados_gerais.pedidos WHERE quantidade_produzida::INTEGER < quantidade::INTEGER and status <> '5';") #Minimo valor de id com status 0 ou 1
        resultado = cursor.fetchone()
        cursor.execute ("SELECT * FROM dados_gerais.pedidos WHERE id =" + str(resultado[0])+";")
        resultado = cursor.fetchone()
        colunas = [desc[0] for desc in cursor.description]
        data = dict(zip(colunas, resultado))
    except:
        print ("sem Pedido em Sequencia")
        irparaposicao(13)
        finalizaUltimoPedido()
    return data  


def verificar_totalPedidos():
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password)
    global ArmazenaQnatPedida
    try:
        cursor = conn.cursor()
        # Corrigida com CAST para INTEGER
        cursor.execute("SELECT SUM(quantidade::INTEGER) AS total_pedidos FROM dados_gerais.pedidos WHERE data_pedido::DATE = CURRENT_DATE AND status <> '5';")
        resultado = cursor.fetchone()
        # Cria dicionário com o resultado
        data = {
            "total_pedidos": resultado[0] if resultado[0] is not None else 0
        }
        # Converte para JSON
        json_result = json.dumps(data, indent=4)
        Qnt_Pedido = resultado[0]
        
        if (Qnt_Pedido==None):
            Qnt_Pedido=0
        ArmazenaQnatPedida = Qnt_Pedido
    except:
        ArmazenaQnatPedida = ArmazenaQnatPedida
    return ArmazenaQnatPedida

Qnt_Pedido = verificar_totalPedidos()
print ("Quantidade do Pedido: " + str(Qnt_Pedido))
Main_client.write_single_register(100,Qnt_Pedido)             #Quantidade de Peças Pedidas Para testes  <<<<<<<

def check_PedidoEmFila():
    global PedidoAtivoFila
    totalProduzido = ObterQuantidadeAnterior()
    ValorProducaoDia = verificar_totalPedidos()
    time.sleep(0.2)
    Total = int(int(ValorProducaoDia) - int(totalProduzido))
    if(Total>0):
        PedidoAtivoFila = True
    else:
        PedidoAtivoFila = False
    return PedidoAtivoFila
    

check_PedidoEmFila()

Status_Base_Carregada=Main_client.read_coils(2,1)[0]  
if (Status_Base_Carregada==False):
    inicio_programa()

    valorProducao = int(ObterQuantidadeAnterior())
    print ("Valor:" +str(valorProducao))
    #PRODUÇAO ANTERIOR
    Main_client.write_single_register(30,valorProducao)
    Main_client.write_single_register(31,valorProducao)
    Main_client.write_single_register(32,valorProducao)
    Main_client.write_single_register(33,valorProducao)
    Main_client.write_single_register(34,valorProducao)
    Main_client.write_single_register(35,valorProducao)
    Main_client.write_single_register(36,valorProducao)
    time.sleep(0.2)


def confere(endereco: int, valor: int) -> None:
    # Lê apenas 1 registro
    Leitura = Main_client.read_holding_registers(endereco, 1)
    
    if Leitura:  # verifica se a leitura retornou dados
        if Leitura[0] != valor:
            Main_client.write_single_register(endereco, valor)
            nova_leitura = Main_client.read_holding_registers(endereco, 1)
            print(f"Verificando Escrita: {endereco}, {valor} -> {nova_leitura[0]}")
        else:
            print(f"Escrita OK: {endereco}, {valor} -> {Leitura[0]}")
    else:
        print(f"Falha ao ler o endereço {endereco}")


def reinicioOperaçoes():
    try:

        global Toogle_ProducaoBatentes
        global Toogle_ProducaoManipulo
        global Toogle_ProducaoPrimeiroEstagioCabeca
        global Toogle_ProducaoCabecaCentroUsinagemFIm
        global Espera
        
        CentroUsinagem_client = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True)   #IP do Centro de Usinagem
        time.sleep(0.1)  
        TornoCNC_client = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True)         #IP do torno CNC   
        time.sleep(0.1) 
        
        Status_TORNO_Parado=TornoCNC_client.read_coils(22,1)[0]                                             #Verifica status MaqParada do torno 
        time.sleep(0.1) 
        


        Status_CentroUsinagem_Parado=CentroUsinagem_client.read_coils(22,1)[0]                              #Verifica status MaqParada do CENTRO 
        time.sleep(0.1)  
        
        Main_passo_CentroUsinagem =  Main_client.read_holding_registers(111,1)[0]
        time.sleep(0.1)  
        Main_passo_torno =  Main_client.read_holding_registers(112,1)[0]  
        time.sleep(0.1)
       
        Pega_P1 = bool(Main_client.read_holding_registers(21,1)[0])     #Status pega peça 1
        Pega_P2 = bool(Main_client.read_holding_registers(22,1)[0])     #Status pega peça 2
        Pega_P3 = bool(Main_client.read_holding_registers(23,1)[0])     #Status pega peça 3
        Pega_P4 = bool(Main_client.read_holding_registers(24,1)[0])     #Status pega peça 4
        Pega_P5 = bool(Main_client.read_holding_registers(25,1)[0])     #Status pega peça 5

        P3_NabaseParaUsinarCentro = Main_client.read_holding_registers(17,1)[0] #Status peca P3 PRIMEIRA ETAPA E ESTA NA BASE DO AMR

        pedido =  Main_client.read_holding_registers(100,1)[0]
        Producao = Main_client.read_holding_registers(30,1)[0]

        Contg_P1 = Main_client.read_holding_registers(31,1)[0]
        Contg_P2 = Main_client.read_holding_registers(32,1)[0]
        Contg_P3 = Main_client.read_holding_registers(33,1)[0]
        Contg_P4 = Main_client.read_holding_registers(34,1)[0]
        Contg_P5 = Main_client.read_holding_registers(35,1)[0] 
        Contg_P3_Centro= Main_client.read_holding_registers(36,1)[0]
        
        Fianlizar_Torno=0

        if((Contg_P1 < pedido) and (Contg_P2< pedido) and (Contg_P3< pedido)):
            Fianlizar_Torno = 1
            Espera=False
          
        Fianlizar_Centro =0
        if((Contg_P4< pedido) and (Contg_P3_Centro< pedido) and (Contg_P5< pedido)):
            Fianlizar_Centro = 1
            Espera=False
        
        if (Main_passo_CentroUsinagem==20)and (Fianlizar_Centro==1):
            if((Toogle_ProducaoManipulo==1)and(Status_CentroUsinagem_Parado==False)and(Pega_P4==False)and(Pega_P5==False)):
                Main_client.write_single_register(111,0)    #Inicia novamente com  Manipulo
                Main_client.write_single_register(2,3)      #iniciar operando centro da peca 1 -P5
                print("\033[31mFIM REINICIO  Inicia novamente com  Manipulo CentroUsinagem!\033[0m")
                Main_clientGer.write_single_register(42,1)  #Toogle_ReinicioCentroUsinagem
                #reinicio de operaçao
                Main_client.write_single_register(38,0)
                time.sleep(0.2)
                confere(38,0)
                Main_client.write_single_register(40,0)
                time.sleep(0.2)
                confere(40,0)
                Toogle_ProducaoCabecaCentroUsinagemFIm=0
                Toogle_ProducaoManipulo=0
                
                return

            if((Toogle_ProducaoCabecaCentroUsinagemFIm==1)and(Status_CentroUsinagem_Parado==False))and(P3_NabaseParaUsinarCentro==1):
                Main_client.write_single_register(111,6)    #Inicia novamente com  Cabeça Martelo
                Main_client.write_single_register(2,1)      #iniciar operando centro da peca 1 -P3
                print("\033[31mFIM REINICIO  Inicia novamente com  Cabeca Martelo CentroUsinagem!\033[0m")
                Main_clientGer.write_single_register(42,1)  #Toogle_ReinicioCentroUsinagem
                #reinicio de operaçao
                Main_client.write_single_register(38,0)
                time.sleep(0.2)
                confere(38,0)
                Main_client.write_single_register(40,0)
                time.sleep(0.2)
                confere(40,0)
                Toogle_ProducaoManipulo=0
                Toogle_ProducaoCabecaCentroUsinagemFIm=0
                return
        
        if (Main_passo_torno==16) and (Fianlizar_Torno==1):
            if((Toogle_ProducaoPrimeiroEstagioCabeca==1)and(Status_TORNO_Parado==False)and(Pega_P3==False)):
                Main_client.write_single_register(112,0)   #Inicia novamente Cabeca Martelo
                Main_client.write_single_register(1,3)     #iniciar operando torno da peca  1 - P1
                print("\033[31mFIM REINICIO  Inicia novamente com  Cabeca Martelo Torno!\033[0m")
                Main_clientGer.write_single_register(41,1) #Toogle_ReinicioTorno
                #reinicio de operaçao
                Main_client.write_single_register(37,0)
                time.sleep(0.2)
                confere(37,0)
                Main_client.write_single_register(39,0)
                time.sleep(0.2)
                confere(39,0)
                Toogle_ProducaoBatentes=0
                Toogle_ProducaoPrimeiroEstagioCabeca=0 
                return

            if((Toogle_ProducaoBatentes==1)and(Status_TORNO_Parado==False)and(Pega_P1==False)and(Pega_P2==False)):
                Main_client.write_single_register(112,7)    #Inicia novamente com  Batentes
                Main_client.write_single_register(1,3)      #iniciar operando torno da peca  1 - P1 --ajuste para iniciar para depois subtrarir 1
                print("\033[31mFIM REINICIO  Inicia novamente com  Batentes Torno!\033[0m")
                #reinicio de operaçao
                Main_clientGer.write_single_register(41,1)   #Toogle_ReinicioTorno
                Main_client.write_single_register(37,0)
                sleep(0.2)
                confere(37,0)
                Main_client.write_single_register(39,0)
                sleep(0.2)
                confere(39,0)

                Toogle_ProducaoPrimeiroEstagioCabeca=0
                Toogle_ProducaoBatentes=0
                return
    except:
        print("erro final Modbus")


def agilizar_Virada_Torno():
    try:
        global St_ViraPeca
        global Status_TORNO_Pause
        global Main_passo_torno
        St_ViraPeca = ler_Torno_ViraPeca()
        if ((St_ViraPeca==0) and (((Status_TORNO_Pause==True) and (Main_passo_torno==4))or((Status_TORNO_Pause==True) and (Main_passo_torno==10)))):
            Torno_ViraPeca()
            set_Torno_ViraPeca()
    except:
        pass 

#########################
def logistica():
                    
                    global Status_KanbanTORNO
                    global Status_KanbanCentroUsinagemManipulo
                    global Status_KanbanCentroUsinagemCabeca
                    global Passo_Medicao_Tridimensional_Torno
                    global Passo_Medicao_Tridimensional_CentroUsinagem

                    CentroUsinagem_client = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True)   #IP do Centro de Usinagem
                    TornoCNC_client = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True)         #IP do torno CNC       
                    time.sleep(0.1)
                    Status_TORNO_Parado=TornoCNC_client.read_coils(22,1)[0] 
                    time.sleep(0.1)
                    
                    Status_CentroUsinagem_Parado=CentroUsinagem_client.read_coils(22,1)[0]
                    time.sleep(0.1)

                    Status_CentroUsinagem_Pause=CentroUsinagem_client.read_coils(23,1)[0]   #Verifica status pause do CENTRO
                    time.sleep(0.1) 
                    Status_TORNO_Pause=TornoCNC_client.read_coils(23,1)[0]                  #Verifica status pause do torno
                    time.sleep(0.1)                                                         #Delay

                    EM_Atividade=Main_client.read_coils(3,1)[0]
                    Main_passo_CentroUsinagem =  Main_client.read_holding_registers(111,1)[0]
                    Main_passo_Torno =  Main_client.read_holding_registers(112,1)[0]

                    Peca_01 = Main_client.read_holding_registers(11,1)[0]   #Status peca 1
                    Peca_02 = Main_client.read_holding_registers(12,1)[0]   #Status peca 2
                    Peca_03 = Main_client.read_holding_registers(13,1)[0]   #Status peca 3
                    Peca_04 = Main_client.read_holding_registers(14,1)[0]   #Status peca 4
                    Peca_05 = Main_client.read_holding_registers(15,1)[0]   #Status peca 5

                    St_Pega_P1 = Main_client.read_holding_registers(21,1)[0]   #Status pega peça 1
                    St_Pega_P2 = Main_client.read_holding_registers(22,1)[0]   #Status pega peça 2
                    St_Pega_P3 = Main_client.read_holding_registers(23,1)[0]   #Status pega peça 3
                    St_Pega_P4 = Main_client.read_holding_registers(24,1)[0]   #Status pega peça 4
                    St_Pega_P5 = Main_client.read_holding_registers(25,1)[0]   #Status pega peça 5

########################## REALIZAR MEDIDAS           
                    if ((Status_TORNO_Pause == False) and (Status_CentroUsinagem_Pause == False)
                        or (Status_TORNO_Parado == False) and (Status_CentroUsinagem_Parado == False)
                        and (EM_Atividade == False)):
                        Main_passo_CentroUsinagem =  Main_client.read_holding_registers(111,1)[0]
                        Main_passo_Torno =  Main_client.read_holding_registers(112,1)[0]
                        pecaEmProducaoCentroUsinagem = Main_client.read_holding_registers(114,1)[0]

                        Status_TORNO_Parado=TornoCNC_client.read_coils(22,1)[0] 
                        Status_CentroUsinagem_Parado=CentroUsinagem_client.read_coils(22,1)[0]
                        
                        passa=0
                        if((Status_TORNO_Parado==False) or (Status_CentroUsinagem_Parado==False)):
                            passa=1

                        if ((Main_passo_Torno == Passo_Medicao_Tridimensional_Torno)or((Main_passo_CentroUsinagem == Passo_Medicao_Tridimensional_CentroUsinagem)and(pecaEmProducaoCentroUsinagem==2))and (EM_Atividade==False)and(passa==0)):
                                print("Medir _ TRIDIMENSIONAL")
                                Medir_Tridimensional()
                                Passo_Medicao_Tridimensional_Torno=1000 #Valor  Qualquer para sair do Loop
                                Passo_Medicao_Tridimensional_CentroUsinagem = 1000
                                return  
                                

########################## KAMBAM
                    liberado=0
                    pss_Centro = Main_client.read_holding_registers(111,1)[0] #Passo Inical centro 
                    pss_Torno  = Main_client.read_holding_registers(112,1)[0] #Passo Inical torno   
                    if((pss_Torno!=0)and(pss_Centro!=0)):
                        liberado=1

                    if (((Peca_01 == True) and (Peca_02 == True)and (Peca_03 == True)and (Peca_04 == True)and (Peca_05== True))
                        and ( liberado==1)and (EM_Atividade == False)):
                        print(f'Valores reinicio : {pss_Torno} -- {pss_Centro}')
                        
                        Status_KanbanCentroUsinagemCabeca=Main_client.read_coils(6,1)[0] 
                        Status_KanbanCentroUsinagemManipulo=Main_client.read_coils(5,1)[0] 
                        Status_KanbanTORNO=Main_client.read_coils(4,1)[0] 
                        
                        EM_Atividade=Main_client.read_coils(3,1)[0]

                        Main_passo_CentroUsinagem =  Main_client.read_holding_registers(111,1)[0]  #passo atual  CentroUsinagem
                        Main_passo_torno =  Main_client.read_holding_registers(112,1)[0]           #passo atual Torno
                        
                        Main_client.write_single_coil(3,True) 
                        #Kanban_Pecas_Torno()
                        #Kanban_Pecas_Centro_Manipulo()
                        #Kanban_Pecas_Centro_CabecaMartelo()
                        Kanban_TODAS_Montagem()

                        Main_client.write_single_register(11,0)   #Status pega peça 1
                        Main_client.write_single_register(12,0)   #Status pega peça 2
                        Main_client.write_single_register(13,0)   #Status pega peça 3
                        Main_client.write_single_register(14,0)   #Status pega peça 4
                        Main_client.write_single_register(15,0)   #Status pega peça 5
                        Main_client.write_single_register(16,0)   #Status peca 3 PRIMEIRA ETAPA
                        
                        while(Main_client.read_holding_registers(11,1)[0]==1):
                            print("Erro zerar producao P1")
                            Main_client.write_single_register(11,0)
                            time.sleep(0.1)
                        while(Main_client.read_holding_registers(12,1)[0]==1):
                            print("Erro zerar producao P2")
                            Main_client.write_single_register(12,0)
                            time.sleep(0.1)
                        while(Main_client.read_holding_registers(13,1)[0]==1):
                            print("Erro zerar producao P3")
                            Main_client.write_single_register(13,0)
                            time.sleep(0.1)
                        while(Main_client.read_holding_registers(14,1)[0]==1):
                            print("Erro zerar producao P4")
                            Main_client.write_single_register(14,0)
                            time.sleep(0.1)
                        while(Main_client.read_holding_registers(15,1)[0]==1):
                            print("Erro zerar producao P5")
                            Main_client.write_single_register(15,0)
                            time.sleep(0.1)
                        while(Main_client.read_holding_registers(16,1)[0]==1):
                            print("Erro zerar producao Etapa")
                            Main_client.write_single_register(16,0)
                            time.sleep(0.1)
                        

                        Contagem_Producao =  Main_client.read_holding_registers(30,1)[0] #Contagem De Produção
                        Contagem_Producao=Contagem_Producao+1
                        Main_client.write_single_register(30,Contagem_Producao)

                        pedido =  Main_client.read_holding_registers(100,1)[0]
                        Producao = Main_client.read_holding_registers(30,1)[0]

                        Contg_P1 = Main_clientCR.read_holding_registers(31,1)[0]
                        Contg_P2 = Main_clientCR.read_holding_registers(32,1)[0]
                        Contg_P3 = Main_clientCR.read_holding_registers(33,1)[0]
                        Contg_P4 = Main_clientCR.read_holding_registers(34,1)[0]
                        Contg_P5 = Main_clientCR.read_holding_registers(35,1)[0] 

                        #Reabastecer caso tenha alguma peça Faltando na Base do AMR
                        if (St_Pega_P1==1)and (Contg_P1 < (pedido +1) ):
                            reposicao_batentes1() 
                            Main_client.write_single_register(21,0)   #Status pega peça 1
                            print("Reposição manipulo preto P1")
                        if (St_Pega_P2==1)and (Contg_P2 < (pedido +1)):
                            reposicao_batentes2()
                            Main_client.write_single_register(22,0)   #Status pega peça 2
                            print("Reposição manipulo preto P2")
                        if (St_Pega_P3==1)and (Contg_P3 < (pedido +1)):
                            reposicao_cabeca()
                            Main_client.write_single_register(23,0)   #Status pega peça 3
                            print("Reposição cabeça de Alumínio")
                        if (St_Pega_P4==1)and (Contg_P4 < (pedido +1)):
                            reposicao_capa1()
                            Main_client.write_single_register(24,0)   #Status pega peça 4
                            print("Reposição manipulo preto P4")
                        if (St_Pega_P5==1)and (Contg_P5 < (pedido +1)):
                            reposicao_capa2()
                            Main_client.write_single_register(25,0)   #Status pega peça 5
                            print("Reposição manipulo preto P5")

                        Main_client.write_single_coil(3,False)
                        return

########################## REPOSIÇÃO
                    Contagem = Main_client.read_holding_registers(30,1)[0]
                    pedido =  Main_client.read_holding_registers(100,1)[0]

                    Contg_P1 = Main_clientCR.read_holding_registers(31,1)[0]
                    Contg_P2 = Main_clientCR.read_holding_registers(32,1)[0]
                    Contg_P3 = Main_clientCR.read_holding_registers(33,1)[0]
                    Contg_P4 = Main_clientCR.read_holding_registers(34,1)[0]
                    Contg_P5 = Main_clientCR.read_holding_registers(35,1)[0] 

                    Status_TORNO_Parado=TornoCNC_client.read_coils(22,1)[0] 
                    Status_CentroUsinagem_Parado=CentroUsinagem_client.read_coils(22,1)[0]
                    passa=0
                    if((Status_TORNO_Parado==False) or (Status_CentroUsinagem_Parado==False)):
                        passa=1
                    
                    pedido2=0 
                    if (int(pedido)>0):
                        if ((Status_TORNO_Pause == False) and (Status_CentroUsinagem_Pause == False) and (EM_Atividade == False) and (passa==0)):                            
                            EM_Atividade=Main_client.read_coils(3,1)[0]
                                                                                  
                            if ((St_Pega_P3==1 )and(St_Pega_P4==1)and(St_Pega_P5==1)and(St_Pega_P2==1) and (St_Pega_P1==1 ))and (EM_Atividade==False)and (Contg_P5<pedido):
                                Main_client.write_single_coil(3,True)
                                reposicao_cabeca()                          #Carrega somente a peça de aluminio
                                Main_client.write_single_register(23,0)     #Status pega peça 3
                                reposicao_capa1()                           #Carrega somente as peças do manipulo preto
                                Main_client.write_single_register(24,0)     #Status pega peça 4
                                reposicao_capa2()                           #Carrega somente as peças do manipulo preto
                                Main_client.write_single_register(25,0)     #Status pega peça 5
                                reposicao_batentes1()                       #Carrega somente as peças das pontas brancas
                                Main_client.write_single_register(21,0)     #Status pega peça 1
                                reposicao_batentes2()                       #Carrega somente as peças das pontas brancas
                                Main_client.write_single_register(22,0)     #Status pega peça 2
                                reinicioOperaçoes()
                                return
                            
                            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Reposição na base AMR
                            if  (St_Pega_P3==1 )and (EM_Atividade==False)and (Contg_P3<(pedido+1)): #(pedido+1) para sempre estar com AMR já abastecido
                                Main_client.write_single_coil(3,True)
                                reposicao_cabeca() #Carrega somente a peça de aluminio
                                Main_client.write_single_register(23,0)   #Status pega peça 3
                                print("Reposição cabeça de Alumínio")
                                return                  
                            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Reposição na base AMR
                            if  (St_Pega_P4==1 )and (EM_Atividade==False)and (Contg_P4 <(pedido+1)):#(pedido+1) para sempre estar com AMR já abastecido
                                Main_client.write_single_coil(3,True)
                                reposicao_capa1() #Carrega somente as peças do manipulo preto
                                Main_client.write_single_register(24,0)   #Status pega peça 4
                                print("Reposição manipulo preto P4")
                                return
                            
                            if  (St_Pega_P5==1 )and (EM_Atividade==False)and (Contg_P5<(pedido+1)):#(pedido+1) para sempre estar com AMR já abastecido
                                Main_client.write_single_coil(3,True)
                                reposicao_capa2() #Carrega somente as peças do manipulo preto
                                Main_client.write_single_register(25,0)   #Status pega peça 5
                                print("Reposição manipulo preto P5")
                                return                         
                            
                            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Reposição na base AMR
                            
                            if (St_Pega_P2==1 )and (EM_Atividade==False)and (Contg_P2<(pedido+1)):#(pedido+1) para sempre estar com AMR já abastecido
                                Main_client.write_single_coil(3,True)
                                reposicao_batentes2() #Carrega somente as peças das pontas brancas
                                print("Reposição pontas brancas P2")
                                Main_client.write_single_register(22,0)   #Status pega peça 2
                                return  

                            if (St_Pega_P1==1 )and (EM_Atividade==False)and (Contg_P1<(pedido+1)):#(pedido+1) para sempre estar com AMR já abastecido
                                Main_client.write_single_coil(3,True)
                                reposicao_batentes1() #Carrega somente as peças das pontas brancas
                                Main_client.write_single_register(21,0)   #Status pega peça 1
                                print("Reposição pontas brancas P1")
                                
                                return  
                        

# Tempo inicial do programa
tempo_inicial = time.time()
print("\033[0;34mInício do programa:\033[0m")
print(time.strftime("%H:%M:%S", time.localtime(tempo_inicial)))


def send_Json():
        Bateria_AMR_bit1=amr_client.read_input_registers(12,1)[0]   #Leitura no AMR nivel de Bateria
        PosicaoAtual_AMR= amr_client.read_input_registers(33,1)[0] #Posicao Atual do AMR

        Status_KanbanCentroUsinagemCabeca=Main_client.read_coils(6,1)[0] 
        Status_KanbanCentroUsinagemManipulo=Main_client.read_coils(5,1)[0] 
        Status_KanbanTORNO=Main_client.read_coils(4,1)[0] 
        Passo_CR = Main_client.read_holding_registers(6,1)[0]
        

        Pega_P1 = Main_client.read_holding_registers(21,1)[0]    #Status pega peça 1
        Pega_P2 = Main_client.read_holding_registers(22,1)[0]    #Status pega peça 2
        Pega_P3 = Main_client.read_holding_registers(23,1)[0]    #Status pega peça 3
        Pega_P4 = Main_client.read_holding_registers(24,1)[0]    #Status pega peça 4
        Pega_P5 = Main_client.read_holding_registers(25,1)[0]    #Status pega peça 5

        Producao = Main_client.read_holding_registers(30,1)[0]
        Qnt_Pedido = Main_client.read_holding_registers(100,1)[0]

        Contg_P1 = Main_clientCR.read_holding_registers(31,1)[0]
        Contg_P2 = Main_clientCR.read_holding_registers(32,1)[0]
        Contg_P3 = Main_clientCR.read_holding_registers(33,1)[0]
        Contg_P4 = Main_clientCR.read_holding_registers(34,1)[0]
        Contg_P5 = Main_clientCR.read_holding_registers(35,1)[0] 
        Contg_P3_Centro= Main_clientCR.read_holding_registers(36,1)[0]
    

        dado1 = str(Bateria_AMR_bit1)  #Bateria AMR
        dado2 = PosicaoAtual_AMR       #Posicao AMR
        dado3 = str (Passo_CR)
        dado4 = Main_client.read_coils(2,1)[0]   #Magazine carregado
        dado5 = [bool(Peca_01), bool(Peca_02), bool(Peca_03PRIMEIROEstagio),bool(Peca_03), bool(Peca_04),bool(Peca_05)]   #status das peças produzidas
        dado6 = [str(Passo_Medicao_Tridimensional_Torno), str(bool(not Passo_Medicao_Tridimensional_Torno)),str(Passo_Medicao_Tridimensional_CentroUsinagem), str(bool(not Passo_Medicao_Tridimensional_CentroUsinagem))] #status da medicção da qualidade
        dado7 = [str(Status_TORNO_Pause), str(Status_TORNO_Parado),str(Status_CentroUsinagem_Pause),str(Status_CentroUsinagem_Parado)] #estado das maquinas TORNO e CENTRO
        dado8 = [str(passo_torno),str(passo_CentroUsinagem)] #PASSO ATUAL DE OPERAÇÃO
        dado9 = [str(Status_KanbanTORNO),str(Status_KanbanCentroUsinagemManipulo),str(Status_KanbanCentroUsinagemCabeca)] #Kanban Realizado
        dado10 = [Main_client.read_holding_registers(113,1)[0],Main_client.read_holding_registers(114,1)[0]]  #Programa atual sendo executado no Torno #Programa atual sendo executado Centro de Usinagem  
        dado11 = [bool(Pega_P1), bool(Pega_P2), bool(Pega_P3),bool(Pega_P4), bool(Pega_P5)]   #status das peças pEGAS
        dado12 = [ str(Producao), str(Qnt_Pedido), str(Contg_P1), str(Contg_P2), str(Contg_P3), str(Contg_P4), str(Contg_P5), str(Contg_P3_Centro)] #Contagem e Pedido
        
        timestamp = time.time()
        horario_local = time.localtime(timestamp)
        hora_formatada = time.strftime("%H:%M:%S", horario_local)

        dados ={'Main': 
                        {
                        'NivelBateriaAMR': dado1,
                        'PosicaoAMR': dado2,
                        'PassoCR': dado3,
                        'AMR_Abastecido': dado4,
                        'St_Producao': dado5,
                        'Inspecao': dado6,
                        'StatusDeMaquina': dado7,
                        'PassoMaquinas':dado8,
                        'Kanban': dado9,
                        'ProgramaEmExecucaoCNC':dado10,
                        'Reposicao':dado11,
                        'ContagemPedidoPecas':dado12,
                        'Timestamp':hora_formatada
                        }
                }
        print(json.dumps(dados)) 

send_Json()
#sys.exit() 

#ABASTECIMENTO INICIAL
if(Status_Base_Carregada==False):
   abastecer()  #Inicio do Truno
   Main_client.write_single_coil(2,True)

Main_client.write_single_coil(3,False)
while(Start_Pedido==False): # Mudar True  bit que recebe o pedido.
    Qnt_Pedido = verificar_totalPedidos()
    Main_client.write_single_register(100,Qnt_Pedido)             #Quantidade de Peças Pedidas Para testes  <<<<<<<
    time.sleep(0.2)                                               #Delay
    check_PedidoEmFila()
    
    if ((Qnt_Pedido>0) and (PedidoAtivoFila == True)):
        Start_Pedido=Main_client.read_coils(1,1)[0]                                                     #Verifica se é para entrar em operação ou seja se tem pedido
        time.sleep(0.2)                                                                                 #Delay
        EM_Atividade=Main_client.read_coils(3,1)[0]                                                     #Verifica se o conjunto AMR/CR esta ocupado
        time.sleep(0.2)                                                                                 #Delay
        PecaAtual_TORNO=Main_client.read_holding_registers(1,1)[0]                                      #Verifica qual peça esta fazendo no TORNO
        PecaAtual_Centro=Main_client.read_holding_registers(2,1)[0]                                     #Verifica qual peça esta fazendo no CENTRO
        #RealizaConexões
        Main_client = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True)                  #IP local
        CentroUsinagem_client = ModbusClient(host="192.168.192.111", port=502, unit_id=1, auto_open=True)   #IP do Centro de Usinagem
        TornoCNC_client = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True)         #IP do torno CNC                                       
        CR_client = ModbusClient(host="192.168.192.6", port=502, unit_id=1, auto_open=True)                 #IP do CR
        amr_client = ModbusClient(host="192.168.192.5", port=502, unit_id=1, auto_open=True)                #IP do AMR 

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #TRATAR NIVEL DE BATERIA DO AMR
        try: 
                Bateria_AMR_bit1=amr_client.read_input_registers(12,1)[0]   #Leitura no AMR nivel de Bateria
                time.sleep(0.2)                                             #Delay
        except:
                logging.error("erro modbus AMR")                            #Ao erro gravar log
            
        Nivel_Bateria = Main_client.read_holding_registers(5,1)[0]          #Toogle Bateria
        if ((Bateria_AMR_bit1<20)and(Nivel_Bateria==0)):                    #Com nivel abaixo de 20% o AMR vai para base de carregamento
                irparaposicao(6)                                            #Movomenta AMR para posicao de carregamento
                Main_client.write_single_register(5,1)                      #Passo AMR Toogle Bateria no servido modbus 
                time.sleep(0.2)
        if (Bateria_AMR_bit1>90):
                Main_client.write_single_register(5,0)                      #Passo AMR Toogle Bateria no servido modbus
                time.sleep(0.2)
               
        Nivel_Bateria = Main_client.read_holding_registers(5,1)[0]          #Se o nivel estiver acima de 20 realiza as operações
        if (Nivel_Bateria==0):
            Status_Base_Carregada=Main_client.read_coils(2,1)[0]            #Verifica se ja esta abastecido a base do AMR
            time.sleep(0.2)
            if(Status_Base_Carregada==False):
                abastecer()  #Inicio do Truno
                Main_client.write_single_coil(2,True)

            else:
                    Peca_01 = Main_client.read_holding_registers(11,1)[0]   #Status peca 1
                    Peca_02 = Main_client.read_holding_registers(12,1)[0]   #Status peca 2
                    Peca_03 = Main_client.read_holding_registers(13,1)[0]   #Status peca 3
                    Peca_03PRIMEIROEstagio  = Main_client.read_holding_registers(16,1)[0]   #Status peca 3 Primeiro Estágio
                    Peca_04 = Main_client.read_holding_registers(14,1)[0]   #Status peca 4
                    Peca_05 = Main_client.read_holding_registers(15,1)[0]   #Status peca 5

                    St_Producao = [bool(Peca_01), bool(Peca_02), bool(Peca_03), bool(Peca_04),bool(Peca_05)]
                    
                    Status_KanbanCentroUsinagem=Main_client.read_coils(5,1)[0] 
                    Status_KanbanTORNO=Main_client.read_coils(4,1)[0] 

                    Status_TORNO_Pause=TornoCNC_client.read_coils(23,1)[0]                  #Verifica status pause do torno
                    time.sleep(0.2)                                                         #Delay
                    Status_TORNO_Parado=TornoCNC_client.read_coils(22,1)[0]                 #Verifica status MaqParada do torno 
                    time.sleep(0.2)                                                         #Delay
                    passo_torno =  Main_client.read_holding_registers(112,1)[0]             #Passo Atual do Torno
                    Status_CentroUsinagem_Pause=CentroUsinagem_client.read_coils(23,1)[0]   #Verifica status pause do CENTRO
                    time.sleep(0.2)                                                         #Delay
                    Status_CentroUsinagem_Parado=CentroUsinagem_client.read_coils(22,1)[0]  #Verifica status MaqParada do CENTRO 
                    time.sleep(0.2)                                                         #Delay
                    passo_CentroUsinagem =  Main_client.read_holding_registers(111,1)[0]    #Passo Atual do CentroUsinagem
                    
                    #Posição atual AMR
                    try:
                        PosicaoAtual_AMR= amr_client.read_input_registers(33,1)[0]          #Posicao Atual do AMR
                        time.sleep(0.2)
                    except:
                        logging.error("erro modbus AMR")

                    Pause_Pedido=Main_client.read_coils(102,1)[0] 

                    if( Pause_Pedido==False):

                        Status_TORNO_Pause=TornoCNC_client.read_coils(23,1)[0]                  #Verifica status pause do torno
                        Main_passo_CentroUsinagem =  Main_client.read_holding_registers(111,1)[0]
                        Main_passo_Torno =  Main_client.read_holding_registers(112,1)[0]
                        try:
                            EM_Atividade=Main_client.read_coils(3,1)[0]
                        except:
                            pass
                        LIBERADO= 0
                        if(((PosicaoAtual_AMR==4)and(Status_TORNO_Pause==False )and(Status_TORNO_Pause==False ))and(Main_passo_Torno!=16)):
                            LIBERADO=1
                        
                        if ((((Status_CentroUsinagem_Pause==True or Status_CentroUsinagem_Parado==False) and (EM_Atividade==False)))and(Main_passo_CentroUsinagem!=20)and(LIBERADO==0)):
                            Main_client.write_single_coil(3,True)    
                            time.sleep(0.2)
                            irparaposicao(9)
                            while(PosicaoAtual_AMR== amr_client.read_input_registers(33,1)[0]!=9):
                                PosicaoAtual_AMR= amr_client.read_input_registers(33,1)[0]          #Posicao Atual do AMR
                                time.sleep(0.1)
                                Main_client = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True)                  #IP local
                                time.sleep(0.1)
                                Main_client.write_single_coil(3,True)
                                time.sleep(0.1)
                            Main_client.write_single_coil(3,True)
                        
                        EM_Atividade=Main_client.read_coils(3,1)[0]
                        try:
                            PosicaoAtual_AMR= amr_client.read_input_registers(33,1)[0]          #Posicao Atual do AMR
                        except:
                            logging.error("erro modbus AMR")
                        
                        
                        print ("Em Atividade_Centro:" +str(EM_Atividade)) 
                        if ((PosicaoAtual_AMR==9) and(EM_Atividade==True)):
                            time.sleep(0.1)
                            Usinar_CENTRO()

                        Main_passo_CentroUsinagem =  Main_client.read_holding_registers(111,1)[0]
                        Main_passo_torno =  Main_client.read_holding_registers(112,1)[0]            #Armazena o numero da Operação atual de usinagem no Torno CNC
                        EM_Atividade=Main_client.read_coils(3,1)[0]            
                        try:
                            Status_CentroUsinagem_Pause=CentroUsinagem_client.read_coils(23,1)[0]   #Verifica status pause do CENTRO
                        except:
                            pass
###################################################################################################################################
                        send_Json()
###################################################################################################################################
                        LIBERADO= 0
                        if(((PosicaoAtual_AMR==9)and(Status_CentroUsinagem_Pause==False ))and(Main_passo_CentroUsinagem!=20)):
                            LIBERADO=1
                        if ((((Status_TORNO_Pause==True or Status_TORNO_Parado==False)and(EM_Atividade==False)))and (Main_passo_torno!=16)and(LIBERADO==0)):        #16 ultimo passo TORNO
                            Main_client.write_single_coil(3,True)        #Classifica Como Ocupado conjunto AMR/CR esta ocupado   
                            time.sleep(0.2)
                            TORNO_Abrir_Porta_sem_checar()               #Torno CNC abre Porta sem verificar sensores
                            irparaposicao(4)                             #AMR se desloca para pposição 3 no mapa que em frente ao Torno CNC
                            while(PosicaoAtual_AMR== amr_client.read_input_registers(33,1)[0]!=4):
                                PosicaoAtual_AMR= amr_client.read_input_registers(33,1)[0]          #Posicao Atual do AMR
                                time.sleep(0.1)
                                Main_client = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True) #IP local
                                time.sleep(0.1)
                                Main_client.write_single_coil(3,True)
                                time.sleep(0.1)
                            Main_client.write_single_coil(3,True)

                        EM_AtivKidade=Main_client.read_coils(3,1)[0]
                        try:
                            PosicaoAtual_AMR= amr_client.read_input_registers(33,1)[0] #Posicao Atual do AMR
                        except:
                            logging.error("erro modbus AMR")
                        print ("Em Atividade_Torno:" +str(EM_Atividade)) 
                        if ((PosicaoAtual_AMR==4) and(EM_Atividade==True)):
                            time.sleep(0.1)
                            Usinar_TORNO()
                        
                        #Abrir Porta se O torno estiver parado
                        try:
                            TornoCNC_client = ModbusClient(host="192.168.192.112", port=502, unit_id=1, auto_open=True) #IP do torno CNC       
                            time.sleep(0.1)
                            Status_TORNO_Parado=TornoCNC_client.read_coils(22,1)[0]                 #Verifica status MaqParada do torno 
                            time.sleep(0.1)
                            if(Status_TORNO_Parado==False):
                                Status_Porta_S1 =TornoCNC_client.read_coils(26,1)[0]
                                time.sleep(0.1)
                                if(Status_Porta_S1==False):
                                    irparaposicao(4)
                                    TORNO_Abrir_Porta_sem_checar()
                                    print("ABRIU PORTA")
                        except:
                            print("Erro Torno")
                                
    ############################################################################################################                                  
                        #logistica()
    ############################################################################################################
                    else:
                        print("\033[33mPrograma Pausado!\033[0m")
                        time.sleep(0.2)

        Status_KanbanCentroUsinagemCabeca=Main_client.read_coils(6,1)[0] 
        Status_KanbanCentroUsinagemManipulo=Main_client.read_coils(5,1)[0] 
        Status_KanbanTORNO=Main_client.read_coils(4,1)[0] 
        Passo_CR = Main_client.read_holding_registers(6,1)[0]
        

        Pega_P1 = Main_client.read_holding_registers(21,1)[0]    #Status pega peça 1
        Pega_P2 = Main_client.read_holding_registers(22,1)[0]    #Status pega peça 2
        Pega_P3 = Main_client.read_holding_registers(23,1)[0]    #Status pega peça 3
        Pega_P4 = Main_client.read_holding_registers(24,1)[0]    #Status pega peça 4
        Pega_P5 = Main_client.read_holding_registers(25,1)[0]    #Status pega peça 5

        Producao = Main_client.read_holding_registers(30,1)[0]
        Qnt_Pedido = Main_client.read_holding_registers(100,1)[0]

        Contg_P1 = Main_clientCR.read_holding_registers(31,1)[0]
        Contg_P2 = Main_clientCR.read_holding_registers(32,1)[0]
        Contg_P3 = Main_clientCR.read_holding_registers(33,1)[0]
        Contg_P4 = Main_clientCR.read_holding_registers(34,1)[0]
        Contg_P5 = Main_clientCR.read_holding_registers(35,1)[0] 
        Contg_P3_Centro= Main_clientCR.read_holding_registers(36,1)[0]
    
###################################################################################################################################
        send_Json()
###################################################################################################################################

        if(Producao == Qnt_Pedido)and(Espera==False):
            irparaposicao(13)
            Espera=True

        St_Producao=1
        if( Pause_Pedido==True):
            St_Producao=4

        #Verifcar se peças  já é do proximo Pedido        
        if((Contg_P1 or Contg_P3 or Contg_P3 )> Qnt_Pedido):
            data_fim = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            serial = datetime.now().strftime("%Y%m%d%H%M%S")
            cursor = conn.cursor()
            cursor.execute(""" WITH atual AS (
            SELECT MIN(id) AS id_atual
            FROM dados_gerais.pedidos
            WHERE quantidade_produzida::INTEGER < quantidade::INTEGER AND status <> '5'
            ),
            proximo AS (
            SELECT MIN(id) AS id_proximo
            FROM dados_gerais.pedidos
            WHERE status <> '5' AND id > (SELECT id_atual FROM atual)
            )
            UPDATE dados_gerais.pedidos
            SET  fim='"""+str(data_fim)+"""',cod_ratreamento="""+str(serial)+""",status = """+str(St_Producao) +""", next_t ='1'
            WHERE id = (SELECT id_proximo FROM proximo);"""+";")
            conn.commit()
            time.sleep(0.2)
        
        if((Contg_P4 or Contg_P5 or Contg_P3_Centro )>Qnt_Pedido):
            data_fim = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            serial = datetime.now().strftime("%Y%m%d%H%M%S")
            cursor = conn.cursor()
            cursor.execute(""" WITH atual AS (
            SELECT MIN(id) AS id_atual
            FROM dados_gerais.pedidos
            WHERE quantidade_produzida::INTEGER < quantidade::INTEGER AND status <> '5'
            ),
            proximo AS (
            SELECT MIN(id) AS id_proximo
            FROM dados_gerais.pedidos
            WHERE status <> '5' AND id > (SELECT id_atual FROM atual)
            )
            UPDATE dados_gerais.pedidos
            SET  fim='"""+str(data_fim)+"""',cod_ratreamento="""+str(serial)+""",status = """+str(St_Producao) +""", next_c ='1'
            WHERE id = (SELECT id_proximo FROM proximo);"""+";")
            conn.commit()
            time.sleep(0.2)


        try:
            #Verificar quantidade anterior  
            totalAtualDePecas = int( int(Producao) - int(ObterQuantidadeAnterior()))
            data_fim = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            serial = datetime.now().strftime("%Y%m%d%H%M%S")
            DadosPedido =ObterDadosPedido()
            cursor = conn.cursor()
            cursor.execute("UPDATE dados_gerais.pedidos SET   fim='"+str(data_fim)+"',cod_ratreamento="+str(serial)+",status = "+str(St_Producao)+", quantidade_produzida = '"+str(totalAtualDePecas)+"' WHERE  id =" + str(DadosPedido["id"])+";")
            conn.commit()
            time.sleep(0.2)
            try:
                finalizarOrdem(DadosPedido["id"])
            except:
                pass
        except:
            pass   
    ############################################################################################################## Reset Kanban
        if ((Status_KanbanCentroUsinagemCabeca==True)and(Status_KanbanCentroUsinagemManipulo==True)and (Status_KanbanTORNO==True)):
                Main_client.write_single_coil(4,False)   # Kanban Peças do Torno
                Main_client.write_single_coil(5,False)   # Kanban Peças do Centro de Usinagem Manipulo
                Main_client.write_single_coil(6,False)   # Kanban Peças do Centro de Usinagem Cabeça do Martelo
                #TRIDIMENSIONAL
                Passo_Medicao_Tridimensional_Torno = random.choice(Medicao_Tridimensiona_Torno)
                Passo_Medicao_Tridimensional_CentroUsinagem = random.choice(Medicao_Tridimensiona_CentroUsinagem)

    ############################################################################################################## TesteControleDePecas
        Peca_01 = bool(Peca_01)  #Batente Reto
        Peca_02 = bool(Peca_02)  #Batende Abaulado

        Peca_03 = bool(Peca_03)  #Cabeça
        Peca_03PRIMEIROEstagio  =  bool(Peca_03PRIMEIROEstagio)  #Cabeça PRIMEIRO ESTAGIO
        
        Peca_04 = bool(Peca_04)  #Manipulo furo conico
        Peca_05 = bool(Peca_05)  #Manipulo furo sextavado pra porca7

        passo_torno =  str(passo_torno) #poasso atual torno CNC
        Passo_CentroUsinagem =  str(passo_CentroUsinagem) #poasso Centro de Usinagem

    #################################################################################################################################
    #REINICIO DE OPERAÇÕES
        Reinicio_Torno = Main_client.read_holding_registers(41,1)[0]   #Toogle_ReinicioTorno
        Reinicio_CentroUsinagem = Main_client.read_holding_registers(42,1)[0]   #Toogle_ReinicioCentroUsinagem

        Toogle_ProducaoBatentes = Main_client.read_holding_registers(37,1)[0]
        Toogle_ProducaoManipulo = Main_client.read_holding_registers(38,1)[0]
        Toogle_ProducaoPrimeiroEstagioCabeca = Main_client.read_holding_registers(39,1)[0]
        Toogle_ProducaoCabecaCentroUsinagemFIm = Main_client.read_holding_registers(40,1)[0]

        if(Reinicio_Torno==True)and(Reinicio_CentroUsinagem==True):
            contagem = (Main_client.read_holding_registers(43,1)[0]) +1
            Main_clientGer.write_single_register(43,contagem)

            if(contagem>10):
                Main_clientGer.write_single_register(41,0)   #Toogle_ReinicioTorno
                Main_clientGer.write_single_register(42,0)   #Toogle_ReinicioCentroUsinagem
                Main_clientGer.write_single_register(43,0)

        if((((Peca_01==True) and (Peca_02==True))) and (Status_KanbanTORNO==False))and(Reinicio_Torno==False): #TORNO
                Toogle_ProducaoBatentes=1
                Main_client.write_single_register(37,1)#Toogle_ProducaoBatentes
        
        if (Toogle_ProducaoBatentes==1):
                print("\033[93mLiberado_Produção para iniciar Batentes\033[0m")
                print("\033[91m---------------------------------------\033[0m")

        #Liberar para iniciar usinagem com P1 -> Passo do Torno:
        if((Peca_03PRIMEIROEstagio==True) and (Status_KanbanCentroUsinagemCabeca==False))and(Reinicio_CentroUsinagem==False):#TORNO
                Toogle_ProducaoPrimeiroEstagioCabeca=1
                Main_client.write_single_register(39,1)#Toogle_ProducaoPrimeiroEstagioCabeca

        if(Toogle_ProducaoPrimeiroEstagioCabeca==1):
                print("\033[93mLiberado_Produção para iniciar Cabeca Torno\033[0m")
                print("\033[91m---------------------------------------\033[0m")

        #Lieberar para iniciar usinagem com P3 -> centro de Usinagem:
        if((Peca_03==True)and (Status_KanbanCentroUsinagemCabeca==False))and(Reinicio_Torno==False)and(Reinicio_CentroUsinagem==False):#CENTRO DE USINAGEM
                Toogle_ProducaoCabecaCentroUsinagemFIm=1
                Main_client.write_single_register(40,1)#Toogle_ProducaoCabecaCentroUsinagemFIm

        if(Toogle_ProducaoCabecaCentroUsinagemFIm==1):
                print("\033[93mLiberado_Produção para iniciar Cabeca Cabeca Centro Usinagem\033[0m")
                print("\033[91m---------------------------------------\033[0m")

        #Lieerar para iniciar usinagem com P4  -> centro de Usinagem:Kanban_Peca_Manipulo
        if((((Peca_04==True) and (Peca_05==True)))and (Status_KanbanCentroUsinagemManipulo==False)):#or(Toogle_ProducaoManipulo==1)): #CENTRO DE USINAGEM
                Toogle_ProducaoManipulo=1
                Main_client.write_single_register(38,1) #Toogle_ProducaoManipulo

        if(Toogle_ProducaoManipulo==1):
                print("\033[93mLiberado_Produção para iniciar Manipulo Centro Usinagem\033[0m")
                print("\033[91m---------------------------------------\033[0m")
  
    ################################################################################################################################
        reinicioOperaçoes()
    ################################################################################################################################
        check_PedidoEmFila()
    ################################################################################################################################
        logistica()
    ################################################################################################################################

        if(CentroUsinagem_client.open)==True: 
                CentroUsinagem_client.close() 
                        
        if(TornoCNC_client.open)==True:
                TornoCNC_client.close()     
                        
        if(amr_client.open)==True:
                amr_client.close() 
                        
        if(CR_client.open)==True:
                CR_client.close()
    else:
        #TRATAR NIVEL DE BATERIA DO AMR
        try: 
                Bateria_AMR_bit1=amr_client.read_input_registers(12,1)[0]   #Leitura no AMR nivel de Bateria
                print("Carregando... NivelBateria: " + str(Bateria_AMR_bit1) + " %")     #Print nivel bateria
                time.sleep(0.2)                                             #Delay
        except:
                logging.error("erro modbus AMR")                            #Ao erro gravar log
        
        Nivel_Bateria = Main_client.read_holding_registers(5,1)[0]          #Toogle Bateria
        if ((Bateria_AMR_bit1<20)and(Nivel_Bateria==0)):                    #Com nivel abaixo de 20% o AMR vai para base de carregamento
                irparaposicao(6)                                            #Movomenta AMR para posicao de carregamento
                Main_client.write_single_register(5,1)                      #Passo AMR Toogle Bateria no servido modbus 
                time.sleep(0.2)
                print("AMR Carregando.")

        if (Bateria_AMR_bit1>90):
                Main_client.write_single_register(5,0)                      #Passo AMR Toogle Bateria no servido modbus
                time.sleep(0.2)
                Main_client.write_single_coil(3,False)                      #Libera robô para realizar operações em outras maquinas
                time.sleep(0.2)
                print("AMR Carregado!")
        if(Nivel_Bateria==0):
            print("Sem Pedido de Producao")
            check_PedidoEmFila()
            finalizaUltimoPedido()
            irparaposicao(13)