# Tarea3-Redes 

## Ejecución

Se debe ejecutar igual que en el enunciado de la tarea.
Es exactamente lo mismo:
  
    from topology import start, stop
    from send_packet import send_packet
    import json
    routers = start('topology.json')
    send_packet(4321, json.dumps({'destination': "Router#1", 'data': "mensaje"}))
    
**IMPORTANTE:** Dado que el tiempo que se demora
en mandarse las tablas, y dado que en la primera iteración
no todos los routers reciben la info correctamente, es recomendado
esperar cierto tiempo, dependiendo de la topología, para
comenzar a enviar los mensajes.

**ACLARACIÓN:** El problema de la iteración n°1 fue percibido y
correjido, modificando parte del archivo topology.py, sin embargo,
se le consultó a la profesora, y respondió que ese problema no era 
de gran importancia, por lo que se prefirió dejar la tarea como estaba, 
para que no hubiera confusión al momento de correjir el código. 

