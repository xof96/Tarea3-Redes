import json
from json import JSONDecodeError
from threading import Timer
from routing.router_port import RouterPort


class Router(object):
    def __init__(self, name, update_time, ports, logging=True):
        self.name = name
        self.update_time = update_time
        self.table_sending_time = 30  # Intervalo de tiempo en que se manda la tabla del router a los vecinos.
        self.ports = dict()
        self.table = {  # Tabla inicial de cada router.
            self.name: [None, 0]  # Nombre : [Puerto, Hops]
        }
        self._init_ports(ports)
        self.timer = None
        self.logging = logging

    def _success(self, message):
        """
        Internal method called when a packet is successfully received.
        :param message:
        :return:
        """
        print("[{}] {}: {}".format(self.name, 'Success! Data', message))

    def _log(self, message):
        """
        Internal method to log messages.
        :param message:
        :return: None
        """
        if self.logging:
            print("[{}] {}".format(self.name, message))

    def _init_ports(self, ports):
        """
        Internal method to initialize the ports.
        :param ports:
        :return: None
        """
        for port in ports:
            input_port = port['input']
            output_port = port['output']

            router_port = RouterPort(
                input_port, output_port, lambda p: self._new_packet_received(p)
            )

            self.ports[output_port] = router_port

    def _new_packet_received(self, packet):
        """
        Internal method called as callback when a packet is received.
        :param packet:
        :return: None
        """
        self._log("Packet received")
        message = packet.decode()

        try:
            message = json.loads(message)
        except JSONDecodeError:
            self._log("Malformed packet")
            return

        if 'destination' in message and 'data' in message:
            if message['destination'] == self.name:
                self._success(message['data'])
            else:
                # Randomly choose a port to forward
                port = self.table[message['destination']][0]
                self._log("Forwarding to port {}".format(port))
                self.ports[port].send_packet(packet)
        elif 'source' in message and 'table' in message:  #Caso en que recibe una tabla de rutas.
            tab = message['table']
            for key in tab:
                if key in self.table:  # Si está en la tabla, entonces solo la actualiza si le llega algo mejor.
                    if int(tab[key][1]) + 1 < self.table[key][1]:
                        self.table[key][0] = message['source']
                        self.table[key][1] = int(tab[key][1]) + 1
                else:  # Si no está en la tabla, entonces lo agrega.
                    self.table[key] = [message['source'], int(tab[key][1]) + 1]
            self._log("Mi tabla ahora es:\n\t{}".format(self.table))
        else:
            self._log("Malformed packet")

    def _send_table(self):
        """
        Sends table of distance vectors to their neighbors.
        :return: None
        """
        for p in self.ports:
            # Se crea el mensaje con la información de la tabla de rutas.
            message = json.dumps({
                'source': self.ports[p].input_port,
                'table': self.table
            })
            self.ports[p].send_packet(message.encode())
        self.table_timer = Timer(self.table_sending_time, lambda: self._send_table())
        self.table_timer.start()

    def _broadcast(self):
        """
        Internal method to broadcast
        :return: None
        """
        self._log("Broadcasting")
        self.timer = Timer(self.update_time, lambda: self._broadcast())
        self.timer.start()

    def start(self):
        """
        Method to start the routing.
        :return: None
        """
        self._log("Starting")
        self._broadcast()
        for port in self.ports.values():
            port.start()
        # Ahora se envía la tabla a los vecinos, es posible que en la primera iteración, los
        # routers que no tengan sus puertos inicializados aún, no puedan recibir esta información.
        self._send_table()

    def stop(self):
        """
        Method to stop the routing.
        Is in charge of stop the router ports threads.
        :return: None
        """
        self._log("Stopping")
        if self.timer:
            self.timer.cancel()

        for port in self.ports.values():
            port.stop_running()

        for port in self.ports.values():
            port.join()

        self._log("Stopped")
