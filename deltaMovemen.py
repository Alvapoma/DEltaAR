# Todas las unidades se encuentran expresadas en milimitros
# Version mejorada encontrada https://gist.github.com/hugs/4231272
#https://stackoverrun.com/es/q/4950817
#https://stackoverflow.com/questions/18162880/how-to-correctly-compute-direct-kinematics-for-a-delta-robot
# connet to automaticly arduino  https://stackoverflow.com/questions/24214643/python-to-automatically-select-serial-ports-for-arduino
import serial
import serial.tools.list_ports
import math
import numpy
ports= list(serial.tools.list_ports.comports())
conect = False
for p in ports:
    if(p[0].startswith('/dev/ttyACM')):
        ser = serial.Serial(p[0], 115200,timeout = 0.3)
        ser.close()
        ser.open()
        print(p[0])
        print(p[1])
        ser.write(bytes('V', encoding="UTF-8"))
        xread = ser.readline()
        print(xread.decode('UTF-8'))
        if xread.decode('UTF-8') == "Be-DePlace\n":
            print("se conecto")
            conect = True
            break
        else:
            ser.close()

# datos del robot
e = 196.58
f = 256
re = 349
rf = 178.1
# constantes ocupadas
sqrt3 = math.sqrt(3)
pis = 3.141592653
sin120 = sqrt3/2
cos120 = -0.5
tan60 = sqrt3
tan30 = 1/sqrt3
sin30 = 0.5
# punto inicial
PX = [0, 0]
PY = [0, 0]
PZ = [-300, -300]


def calcForward(theta1, theta2, theta3):
    x0 = 0.0
    y0 = 0.0
    z0 = 0.0

    t = (f-e)*tan30/2.0
    dtr = pis/180.0
    theta1 = theta1 * dtr
    theta2 = theta2 * dtr
    theta3 = theta3 * dtr

    y1 = -(t + rf*math.cos(theta1))
    z1 = -rf*math.sin(theta1)
    y2 = (t + rf*math.cos(theta2))*sin30
    x2 = y2*tan60
    z2 = -rf*math.sin(theta2)

    y3 = (t + rf*math.cos(theta3))*sin30
    x3 = -y3*tan60
    z3 = -rf*math.sin(theta3)

    dnm = (y2-y1)*x3-(y3-y1)*x2
    w1 = y1*y1 + z1*z1
    w2 = x2*x2 + y2*y2 + z2*z2
    w3 = x3*x3 + y3*y3 + z3*z3

    a1 = (z2-z1)*(y3-y1)-(z3-z1)*(y2-y1)
    b1 = -((w2-w1)*(y3-y1)-(w3-w1)*(y2-y1))/2.0

    a2 = -(z2-z1)*x3+(z3-z1)*x2
    b2 = ((w2-w1)*x3 - (w3-w1)*x2)/2.0

    a = a1*a1 + a2*a2 + dnm*dnm
    b = 2.0*(a1*b1 + a2*(b2-y1*dnm) - z1*dnm*dnm)
    c = (b2-y1*dnm)*(b2-y1*dnm) + b1*b1 + dnm*dnm*(z1*z1 - re*re)

    d = b*b - 4.0*a*c

    # discriminant
    if d < 0.0:
        return [1, 0, 0, 0]  # non-existing povar. return error,x,y,z

    z0 = -0.5*(b+math.sqrt(d))/a
    x0 = (a1*z0 + b1)/dnm
    y0 = (a2*z0 + b2)/dnm
    print("cinematica directa x:" + str(int(x0)) + " y:"+str(int(y0)) + " z0:" + str(int(z0)))

    return [0, x0, y0, z0]


def cal_angle(x0, y0, z0):
    y1 = -0.5 * 0.57735 * f
    y0 = y0-0.5 * 0.57735 * e
    a = (x0*x0 + y0*y0 + z0*z0 + rf*rf - re*re - y1*y1)/(2*z0)
    b = (y1-y0)/z0
    d = -(a+b*y1)*(a+b*y1)+rf*(b*b*rf+rf)
    if(d<0):
        return [1,0]
    else:
        yj = (y1 - a*b - math.sqrt(d))/(b*b + 1)  # choosing outer point
        zj = a + b*yj
        theta = 180*math.atan(-zj/(y1 - yj))/pis
        if(yj>y1):
            theta =theta +180
        # print("Cinematicanver")
        # print(theta)
        return [0,theta]


def cinematica_inv(x, y, z):
    theta = ["0", "0", "0"]
    status = cal_angle(x, y, z)
    if(status[0]==0):
        theta[0]=str(int(status[1]))
        status = cal_angle(x*cos120+y*sin120, y*cos120-x*sin120, z)
    if(status[0]==0):
        theta[1]=str(int(status[1]))
        status =cal_angle(x*cos120-y*sin120, y*cos120+x*sin120, z)
        
    theta[2] = str(int(status[1]))
    if(status==1):
        print("no se puede calclualar la cinematica")
    return theta


def movedelta(angulo1, angulo2, angulo3, angulo4, griper):
    astr = '#0 P'+angulo1+' #1 P'+angulo2+' #2 P'+angulo3+' #3 P'+angulo4 + ' #4 P'+griper
    # 0 P10 #1 P10 #2 P10 #3 P10 #4 P10
    print(astr)
    ser.write(bytes(astr, encoding="UTF-8"))
    bandera = True
    while bandera:
        xread = ser.read()
        # print(xread)
        if xread.decode('UTF-8') == '.':
            bandera = False
    print("salio")
    return 0


def robotdeltaline(xx, yy, zz, cc, griper):
    print("x:"+str(xx)+"y:"+str(yy)+"z:"+str(-zz))
    pointList = []
    PX[1] = xx
    PY[1] = yy
    PZ[1] = zz
    distancias = distpoint()
    print("valor de distancias"+str(distancias[2]))
    if distancias[2] > 10:
        x4=PX[0]
        z4=PZ[0]
        diferenciax=abs(PX[1]-PX[0])
        diferenciaz=abs(PZ[1]-PZ[0])
        print("valor inicial de X: \t"+str(PX[0]))
        while x4!=PX[1]:
            y3 = equaline(x4)
            print("valor en x:\t"+str(x4)+"\n valor en y:\t"+str(y3) )
            angulo = cinematica_inv(x4, y3, int(z4))
            pointList.append(angulo) 
            #submov(x4, y3, int(z4), cc, griper)
            if PX[0]<PX[1]:
                x4=x4+1
            else:    
                x4=x4-1
            if PZ[0]<PZ[1]:
                z4=z4+(diferenciaz/diferenciax)
            else:
                z4=z4-(diferenciaz/diferenciax)
                
    PX[0] = PX[1]
    PY[0] = PY[1]
    PZ[0] = PZ[1]
    angulo = cinematica_inv(xx, yy, zz)
    pointList.append(angulo)
    for point in pointList:
        movedelta(point[0], point[1], point[2], cc, griper)

    return submov(xx, yy, zz, cc, griper)
def robotdelta(xx, yy, zz, cc, griper):
    print("x:"+str(xx)+"y:"+str(yy)+"z:"+str(zz))
    PX[1] = xx
    PY[1] = yy
    PZ[1] = zz
    PX[0] = PX[1]
    PY[0] = PY[1]
    PZ[0] = PZ[1]
    return submov(xx, yy, zz, cc, griper)


def submov(xx, yy, zz, cc, griper):
    try:
        angulo = cinematica_inv(xx, yy, zz)  # Se le resta a z por el desfase
        #calcForward(int(angulo[0]), int(angulo[1]), int(angulo[2]))
        print("ang1:"+angulo[0]+"ang2:"+angulo[1]+"ang3:"+angulo[2])
        movedelta(angulo[0], angulo[1], angulo[2], cc, griper)  # Agarra la pieza
        return angulo[0]+" "+angulo[1]+" "+angulo[2]+"\n"
    except Exception as e:
        print(e)
        return "ERROR"


def distpoint():
    distx = PX[1]-PX[0]
    disty = PY[1]-PY[0]
    dist = math.sqrt((distx)**2+(disty)**2)
    distfull = [abs(distx), abs(disty), dist]
    return distfull


def equaline(var2):

    pointequa = ((PY[1]-PY[0])/(PX[1]-PX[0]))*(var2-PX[0])+PY[0]
    return pointequa


if __name__ == "__main__":
    print("thisis main")
