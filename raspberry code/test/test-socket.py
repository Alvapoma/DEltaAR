import socket
import testMove
TCP_IP = ''
TCP_PORT = 5001
BUFFER_SIZE = 1024 #20 for fast response # Normally 1024, but we want fast response
storedValue = "Yo, what's ip?"

ispath = False

## lastValue = [x,y,z,cc,gripper]

lastValue = [0,0,-300,0,0] # solo puede ser xyz

def setupServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created.")
    try:
        s.bind((TCP_IP, TCP_PORT))
    except socket.error as msg:
        print(msg)
    print("Socket bind complete")
    return s


def setupConnection(s):
    s.listen(1) # Allows one connection at a time.
    conn, address = s.accept()
    print('Connected to:' + address[0] + ':' + str(address[1] ))
    return conn



def  dataTransfer(conn):
    reply ="";
    global ispath    
    # A big loop that sends/receives data until told not to.
    while True:
        # recive the data
        data = conn.recv(BUFFER_SIZE)
        data = data.decode('utf-8')
        print("data:/"+data+"/") 
        print("recived: " + data)
        print("logitud: "+ str(len(data)));
        # Split the data such that you separate the command
        # from the rest of the data.
        # dataMessage = data.split(' ' ,1)
        
        #angulo = delta31.robotdelta(auxxx ,auxyy ,auxzz,auxgri ,tamano)
 
        if  ispath == False and data[0].isdigit():
            # No esta en el path esta en JOG
            dataMessage = data.rsplit()
            print("valor de longitud de datos:\t"+str(len(dataMessage)))
            if data[0] == '1' :
                # envia xyz
                print("moviendo xyz")
                lastValue[0] = int(dataMessage[1])
                lastValue[1] = int(dataMessage[2])
                lastValue[2] = int(dataMessage[3])
                reply = testMove.robotdelta(int(dataMessage[1]) ,int(dataMessage[2]) ,int(dataMessage[3]),dataMessage[4] ,dataMessage[5])+"\n"
            else:
                # data[0] == '1' envia angulos
                print("moviendo Angulos")
                auxarray = testMove.calcForward(int(dataMessage[1]) ,int(dataMessage[2]) ,int(dataMessage[3]))
                if auxarray[0]== 0:
                    lastValue[0] = int(auxarray[1])
                    lastValue[1] = int(auxarray[2])
                    lastValue[2] = int(auxarray[3])
                    testMove.movedelta(dataMessage[1] ,dataMessage[2] ,dataMessage[3],dataMessage[4] ,dataMessage[5])
                    reply = str(int(auxarray[0]))+" "+ str(int(auxarray[1]))+" "+ str(int(auxarray[2]))+" "+ str(int(auxarray[3]))+"\n"
                
                else:
                    reply = "ERROR/n"
        elif  ispath == True and data[0].isdigit():#cambie el if por elif
            # todo cuando este el path
            dataMessage = data.rsplit()
            print("valor de longitud de datos:\t"+str(len(dataMessage)))
            if len(dataMessage)>6:
                valuedat=0
                while valuedat< len(dataMessage) :
                    if dataMessage[0+valuedat] == '1' :
                        #cuando es Lineal
                        reply = testMove.robotdeltaline(int(dataMessage[1+valuedat]) ,int(dataMessage[2+valuedat]) ,int(dataMessage[3+valuedat]),dataMessage[4+valuedat] ,dataMessage[5+valuedat])+"\n"
                    
                    else:
                        # data[0] == '0' cuando es ptp
                        reply = testMove.robotdelta(int(dataMessage[1+valuedat]) ,int(dataMessage[2+valuedat]) ,int(dataMessage[3+valuedat]),dataMessage[4+valuedat] ,dataMessage[5+valuedat])+"\n"
                    valuedat=valuedat+6
            else:
                if data[0] == '1' :
                    #cuando es Lineal
                    reply = testMove.robotdeltaline(int(dataMessage[1]) ,int(dataMessage[2]) ,int(dataMessage[3]),dataMessage[4] ,dataMessage[5])+"\n"
                else:
                    # data[0] == '0' cuando es ptp
                    reply = testMove.robotdelta(int(dataMessage[1]) ,int(dataMessage[2]) ,int(dataMessage[3]),dataMessage[4] ,dataMessage[5])+"\n"
            
            print("termino")
            reply="termino\n";
            
            

        elif data =='PATH':
            ispath = True
            print(" set path")
            reply="PATHSET\n";

        elif data =='JOG':
            ispath = False
            print(" set JOG")
            reply="JOGset\n";
            # habilita el envio de datos ara path
            
        elif data =='Angle':
            angulo = testMove.cinematica_inv(lastValue[0],lastValue[1],lastValue[2])
            reply = "Angle "+str(angulo[0])+" "+str(angulo[1])+" "+str(angulo[2])+"\n"
            # devuelve el valor de los angulos
        elif data =='XYZ':
            # devuelve xyz
            ## lastValue = [x,y,z,cc,gripper]
            reply= "XYZ "+str(lastValue[0])+" "+str(lastValue[1])+" "+str(lastValue[2])+"\n"
        elif data.startswith( 'print' ):
            dataMessage = data.split(' ' ,1)
            print('Mostrar:'+ dataMessage[1])
        elif data.startswith('EXIT'):
            print("Our Client has left us :( ")
            break
        elif data == 'KILL' :
            print("Our server is shutting down.")
            s.close()
            break
        else:
            reply = 'Unknown Command \n '
        # Send  the reply back to the client
        print("reply=>"+reply)
        conn.sendall(str.encode(reply))
        print("Data has been sent!")
    conn.close()
    

def main():
    s = setupServer()
    while True:
        try:
            conn = setupConnection(s)
            dataTransfer(conn)
        except Exception as e:
            print(e)
            break

if __name__ == "__main__":
    main()
