#from CR import *
#from TornoCNC import *
#from CentroUsinagem import *
#from Gerenciamento import *
#from Estacao_Buffer import *
#from AMR import irparaposicao

from AMR import *
from pyModbusTCP.client import ModbusClient
import paho.mqtt.client as mqtt
import time
import json


Main_clientKanban = ModbusClient(host="127.0.0.1", port=5050, unit_id=1, auto_open=True)                   #IP local
broker = "192.168.192.175"  # Você pode usar um broker público
topic = "Advantech/74FE48482855/data"
topic_send = "Advantech/74FE48482855/ctl/do1"
mensagemMQTT = ""
client_id= "kanban"
contagem_Reprovado = 0

# Função de callback quando uma mensagem é recebida
def on_message(client, userdata, message):
    global mensagemMQTT 
    mensagemMQTT = message.payload.decode()
    #print(f"Recebido: {message.payload.decode()}")


#client = mqtt.Client()
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id)
# Conectar ao broker
client.connect(broker)
client.subscribe(topic)
client.on_message = on_message
# Loop para manter o cliente ativo
client.loop_start()
client.publish(topic_send, "{\"v\":true}", qos=0)
time.sleep(0.2)


def reset_MQTT():
    client.publish(topic_send, "{\"v\":true}", qos=0)
    time.sleep(0.2)
#reset_MQTT()

def check_MQTT():
        cont_estado=0
        global mensagemMQTT
        while (mensagemMQTT==""):
            cont_estado=cont_estado+1
            time.sleep(0.5)
            print("Mesg MQTT_Nullo!" +str(cont_estado))
            if(cont_estado>10):
                print("Erro_Mqtt!")
                #Reinicia 
                Main_clientKanban.write_single_coil(3,False)
                time.sleep(0.2)
                return

            client.loop_stop()
            client.disconnect()
            client.connect(broker)
            client.subscribe(topic) 
            pass

        cont_estado=0
        dados = json.loads(mensagemMQTT)
        # Exemplo: acessar uma chave
        estado = dados["di1"]
        print(estado)

        if (estado==bool(False)):
            global contagem_Reprovado
            contagem_Reprovado=contagem_Reprovado+1
            print("Cont!" + str(contagem_Reprovado))
            if(contagem_Reprovado>10):
                client.publish(topic_send, "{\"v\":true}", qos=0)
                print("Reprovado!")
                #client.loop_stop()
                #client.disconnect()
                Main_clientKanban.write_single_coil(3,False)
                time.sleep(0.5)
                return
            #return
            
        if (estado==bool(True)):
            client.publish(topic_send, "{\"v\":true}", qos=0)
            print("Aprovado!")
            #client.loop_stop()
            #client.disconnect()
            Main_clientKanban.write_single_coil(3,False)
            time.sleep(0.2)
            return
        else:
           mensagemMQTT=""
           estado==""
           time.sleep(0.2)
           check_MQTT()
#check_MQTT()
def Medir_Tridimensional():
    #client.connect(broker)
    #client.subscribe(topic)
    #client.on_message = on_message
    # Loop para manter o cliente ativo
    #client.loop_start()
    #time.sleep(1)
    client.publish(topic_send, "{\"v\":false}", qos=0)
    time.sleep(0.3)
    client.publish(topic_send, "{\"v\":false}", qos=0)
    time.sleep(0.3)
    client.publish(topic_send, "{\"v\":false}", qos=0)
    time.sleep(0.3)

    irparaposicao(14) #Posicao do Buffer para abastecimento
    global contagem_Reprovado
    contagem_Reprovado=0
    print("EstagioMQTT")
    check_MQTT()
    #Main_clientKanban.write_single_coil(2,True)     #
    Main_clientKanban.write_single_coil(3,False)    #Libera robÃ´ para realizar operaÃ§Ãµes em outras maquinas
    return

def Kanban_TODAS_Montagem():
    Main_clientKanban.write_single_coil(3,True)
    print("\033[1;31mEstagio_Kanban Todas.\033[0m")
    irparaposicao(11) 
    CR_atividade(60)
    print("Estagio_Kanban Todas REALIZADO")
    Main_clientKanban.write_single_coil(4,True)
    time.sleep(0.2)
    Main_clientKanban.write_single_coil(5,True)
    time.sleep(0.2)
    Main_clientKanban.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    Main_clientKanban.write_single_coil(6,True)
    time.sleep(0.2)
    Main_clientKanban.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    Main_clientKanban.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return

def Kanban_Pecas_Torno():
    Main_clientKanban.write_single_coil(3,True)
    #print("Estagio_Kanban TORNO") 
    print("\033[1;31mEstagio_Kanban TORNO.\033[0m")
    irparaposicao(11) 
    CR_atividade(44)
    print("Estagio_Kanban TORNO REALIZADO")
    #irparaposicao(13)  
    Main_clientKanban.write_single_coil(4,True)
    time.sleep(0.2)
    Main_clientKanban.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return

def Kanban_Pecas_Centro_Manipulo():
    Main_clientKanban.write_single_coil(3,True)
    #print("Estagio_Kanban Centro de Usinagem Manipulo")
    print("\033[1;31mEstagio_Kanban Centro de Usinagem Manipulo.\033[0m")
    irparaposicao(11) 
    CR_atividade(46)
    print("Estagio_Kanban Centro de Usinagem Manipulo REALIZADO")
    #irparaposicao(13)  
    Main_clientKanban.write_single_coil(5,True)
    time.sleep(0.2)
    Main_clientKanban.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return

def Kanban_Pecas_Centro_CabecaMartelo():
    Main_clientKanban.write_single_coil(3,True)
    #print("Estagio_Kanban Centro de Usinagem Cabeca Martelo")
    print("\033[1;31mEstagio_Kanban Centro de Usinagem Cabeca Martelo.\033[0m")
    irparaposicao(11) 
    CR_atividade(45)
    print("Estagio_Kanban Centro de Usinagem Cabeca Martelo REALIZADO")
    #irparaposicao(13)  
    Main_clientKanban.write_single_coil(6,True)
    time.sleep(0.2)
    Main_clientKanban.write_single_coil(3,False)    #Libera robô para realizar operações em outras maquinas
    return

