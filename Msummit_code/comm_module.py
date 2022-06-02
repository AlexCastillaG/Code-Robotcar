from distutils.log import error
import socket
import time
from numpy import not_equal
import traceback
class communicator():

    def __init__(self,filename):
        self.IP,self.PORT,self.BUFFER,self.CHECK = self.get_ip_and_port(filename)
        self.delay = 0.01

    def get_ip_and_port(self,filename):
        with open(str(filename), "r") as a:
            dict = a.read().split(":")
        return dict[0],int(dict[1]),int(dict[2]),bool(int(dict[3]))

    def decode_data(self,data):
        data = data.decode("utf-8").strip('][').split(', ')
        return data



    
class receiver(communicator):
    
    def __init__(self,filename):
        self.IP,self.PORT,self.BUFFER,self.CHECK = self.get_ip_and_port(filename)
        self.sock = self.create_socket()
        self.delay = 0.01
    
    def create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.IP, self.PORT))
        s.listen(1)
        return s


    def receive(self):
        time.sleep(self.delay)
        conn, addr = self.sock.accept()
        data = conn.recv(self.BUFFER)
        data = self.decode_data(data)
        conn.close()
        return data
    
class server(communicator):
    
    def __init__(self,IP,PORT,BUFFER):
        self.IP,self.PORT,self.BUFFER = IP,PORT,BUFFER
        self.conn = self.create_socket()
        self.data = None
    
    def create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.bind((self.IP, self.PORT))
        s.listen(1)
        self.conn=None

        try:
            self.conn, self.addr = s.accept()
            self.conn.settimeout(1)
        except TimeoutError:
            if self.conn != None:
                self.conn.close()
                self.conn = self.create_socket()
            print("Se perdio la conexión con el dispositivo ")
        
        
        print("Se conecto un nuevo dispositivo con ip ",self.addr[0], " por el puerto ",self.addr[1])
        return self.conn      

    def send(self,*args):
        to_send_data = []
        
        for item in args:
            to_send_data.append(item)
            
        self.delay = 0.01
        try:
            self.data = self.conn.recv(self.BUFFER)
        except (ConnectionAbortedError,ConnectionResetError,TimeoutError):
            print("El dispositivo con ip ",self.addr[0], " y puerto ",self.addr[1]," se desconecto", traceback.format_exc())
            self.data = None      
        except Exception:
            print("Error desconocido: ", traceback.format_exc())  
            self.data = None 

        
    
        if not self.data:
            to_send_data = []
            print("No se recibieron datos del dispositivo con ip ",self.addr[0], " y puerto ",self.addr[1])
            self.conn.close()
            self.conn = self.create_socket()
            
        self.data = to_send_data
        #print("sending :" , data)
        self.conn.sendall(str(self.data).encode("utf-8"))
        
class tcp_request(communicator):
    
    def __init__(self,IP,PORT,BUFFER):
        self.IP,self.PORT,self.BUFFER = IP,PORT,BUFFER
        self.data="hello"
        self.create_socket()

        
    def create_socket(self):  
   
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.IP, self.PORT))

            
    def request(self):

        time.sleep(0.01)
        message = str(self.data).encode("utf-8")
        self.data = self.decode_data(self.s.recv(self.BUFFER))
        self.s.sendall(message)
        print("receiving:" , self.data)
        return self.data

class sender(communicator):

    
    def send(self,device_name,*args):  # send the information to a client
        data=""
        time.sleep(self.delay)
        for n in args:
            data.append(n)
        message = str(data).encode("utf-8")
        
        try:
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)     
            self.sock.connect(( self.IP,self.PORT))  
            self.sock.send(message)
            data = self.sock.recv(self.BUFFER)
            self.sock.close()
        except ConnectionRefusedError:
            print("Connection lost: Attempting to reconnect "+"to {}".format(device_name))
        except ConnectionResetError:
            print("Devices has been disconnected "+"from {}".format(device_name))
        except TimeoutError:
            print("Devices has been disconnected for too long, reconnect or quit the program")
        except OSError:
            print("There is no connection available, connect to the rigth router")
        except Exception as e:
            print("Unknown error: " , e)
            
        #print(data)
            


