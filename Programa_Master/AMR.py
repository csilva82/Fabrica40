from pyModbusTCP.client import ModbusClient
from CR import *
from Gerenciamento import *
import time
#from Kanban_Inspecao import *

import time
WAIT_DELAY = 0.2
amr_client = ModbusClient(host="192.168.192.5", port=502, unit_id=1, auto_open=True) #IP do AMR
CR_client = ModbusClient(host="192.168.192.6", port=502, unit_id=1, auto_open=True) #IP do CR

def pos_seguraCR(): #Posição segura no CR tem que ser a 10 -> P10
         CR_atividade(10) 

def aguardardeslocamento():
   is_ok = amr_client.read_input_registers(8,1)[0]
   #Aguarda iniciar Movimento
   while is_ok==4:
      #AMR_STATUS(1)
      is_ok = amr_client.read_input_registers(8,1)[0]
      time.sleep(1)
   #Aguarda Deslocando
   while is_ok!=4:
      is_ok = amr_client.read_input_registers(8,1)[0]
      time.sleep(1)
 
   #Finalizado Movimento
   posicao = amr_client.read_input_registers(33,1)[0] #Posicao Atual do AMR
   print("Movimentação Finalizada pos: " + str(posicao))
   
def irparaposicao(valor)-> int:
   posicao = amr_client.read_input_registers(33,1)[0] #Posicao Atual do AMR
   if (posicao==valor):
      return None
   pos_seguraCR() 
   print("Deslocando pos: " + str(valor)) 
   is_ok = amr_client.write_single_coil(9, bool(True))
   if(is_ok==True):
      amr_client.write_single_register(0,valor)
      aguardardeslocamento()

def irparaposicaoDireto(valor)-> int:
   print("Deslocando DIRETO: " + str(valor)) 
   is_ok = amr_client.write_single_coil(9, bool(True))
   time.sleep(0.2)
   if(is_ok==True):
      amr_client.write_single_register(0,valor)
