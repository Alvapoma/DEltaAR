#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
#define SERVOMIN 100
#define SERVOMAX 500
int countdelay=11;
char cadena[50]; //Creamos un array que almacenará los caracteres que escribiremos en la consola del PC. Le asignamos  un tope de caracteres, en este caso 30
byte posicion = 0; //Variable para cambiar la posición de los caracteres del array
int P0[] = {300, 300, 300, 300, 300}; //Posicion actual
int P1[] = {300, 300, 300, 300, 300}; //Posicion deseada
int Vp = 1;                   //velocidad predeterminada
int V1[] = {1, 1, 1, 1, 1}; //Velocidad actual
int i, servo = 0, done = 1;
bool toma = false, toma1 = false,msg = false,otracadena=true;
String Aux = "";
int cont=0;
float dif[5];
float increment[5];
float auxfl;
float auxfl1[]={0,0,0,0,0};
float vectP0[5];
int ofset =9;
const int interrupPin=2;
int valorInnterruot=300;
int pinapagado=9;
int pinresep=3;

void stop4axis();

void setup()
{
  Serial.begin(115200);
  //Serial.setTimeout(20);
  pwm.begin();
  pwm.setPWMFreq(50);  // Analog servos run at ~60 Hz updates
  pwm.setPWM(0, 0, 300);
  pwm.setPWM(1, 0, 300);
  pwm.setPWM(2, 0, 300);
  pwm.setPWM(3, 0, 300);
  pwm.setPWM(4, 0, 300);
  attachInterrupt(0,stop4axis,RISING);
  pinMode(pinapagado,OUTPUT);
  digitalWrite(pinapagado,LOW);
  pinMode(pinresep,INPUT);
  
}

void lecturadatos(){
  delay(6);
  if(otracadena){
    memset(cadena, 0, sizeof(cadena)); //memset borra el contenido del array  "cadena" desde la posición 0 hasta el final sizeof
    posicion = 0;
  }
  while (Serial.available() > 0) //Mientras haya datos en el buffer ejecuta la función
  { //Poner un pequeño delay para mejorar la recepción de datos
    cadena[posicion] = Serial.read(); //Lee un carácter del string "cadena" de la "posicion", luego lee el siguiente carácter con "posicion++"
    if(cadena[0]=='#'){
      //inicion de cadena
      otracadena=false;
    }
    if(cadena[posicion]=='\n'){
      //fin de cadena
      otracadena=true;
      //Serial.println("tiene salto de linea");
      cadena[posicion] = ' ';
    }
    if(cadena[0]=='#'){
      posicion++;
    }
    //Serial.println(cadena);
    //posicion++;
  }
  //cadena[posicion] = ' ';
  /*
  if((cadena[0] !=0) && otracadena)
  {
  Serial.print("Recivio=>");
  Serial.println(cadena);
  }*/
}

void condicion1(){
    if (cadena[0] == 'V')
    {
      Serial.println("Be-DePlace\n");
      //Serial.println("SSC32");
    }
}
void condicion2(){
  if (cadena[0] == 'Q')
  {
    bool isdone=true;
    for (i = 0; i <= 3; i++) {
      if (P0[i] != P1[i])
      {
        isdone=false;
      }
    }
    if(isdone){
      Serial.println(".");
    }else{
      Serial.println("o");
    }
  }
}
void analisisdate(){
    if (toma)
    {
        P1[servo]=300;
        if(servo <3 && Aux.toInt()<90 && Aux.toInt()>-90)
        {
          P1[servo] = map(Aux.toInt(), 90+ofset, -90+ofset, SERVOMIN, SERVOMAX);
        }
      if(servo==3  && Aux.toInt()>=0 && Aux.toInt()<360)
      {
          P1[servo] = map(Aux.toInt(), 0, 360, SERVOMIN, SERVOMAX);
      }
      if(servo==4)
      {
        P1[servo] = map(Aux.toInt(), -90, 90, SERVOMIN, SERVOMAX);
          if(P1[servo]>410)//abre el gripper
          {
            P1[servo]=410;
          }
          // valor
          if(digitalRead(2)==HIGH){// esta cerrado el gripper
            if(P1[servo]<=valorInnterruot){
              P1[servo]=valorInnterruot;
            } 
          }
          if(P1[servo]<300)//Gripper cerrado
          {
            P1[servo]=300;
          }
      }
      Serial.println(P1[servo]);
    }
    if (toma1)
    {
      V1[servo] = Aux.toInt();
    }
    toma = false;
    toma1 = false;
    Aux = "";
}
void Optencion_Puntos(){
    if (otracadena == true && cadena[0] == '#')
    {
      Serial.println(cadena);
      for (i = 0; i <= posicion; i++)
      {
        if (cadena[i] == '#')
        {
          servo = (int)cadena[i + 1] - 48;
          //Serial.println(servo);
        }
        if (cadena[i] == ' ')
        {
          analisisdate();
        }
        if (toma || toma1)
        {
          Aux += cadena[i];
        }
        if (cadena[i] == 'P')
        {
          toma = true;
        }
        if (cadena[i] == 'S')
        {
          toma1 = true;
        }
      }
      //////////
      for(int i =0;i<5;i++){
        dif[i]=abs(P1[i]-P0[i]);
      }
      
      if(dif[0]>=dif[1] && dif[0]>=dif[2] && dif[0]>=dif[3] && dif[0]>=dif[4]){
        auxfl=dif[0];
      }
      if(dif[1]>=dif[0] && dif[1]>=dif[2] && dif[1]>=dif[3] && dif[1]>=dif[4]){
        auxfl=dif[1];
      }
      if(dif[2]>=dif[1] && dif[2]>=dif[0] && dif[2]>=dif[3] && dif[2]>=dif[4]){
        auxfl=dif[2];
      }
      if(dif[3]>=dif[1] && dif[3]>=dif[0] && dif[3]>=dif[2] && dif[3]>=dif[4]){
        auxfl=dif[3];
      }
      if(dif[4]>=dif[1] && dif[4]>=dif[0] && dif[4]>=dif[2] && dif[4]>=dif[3]){
        auxfl=dif[4];
      }
      //Serial.println(auxfl);
      for(int i=0;i<5;i++){
        increment[i]=(dif[i]/auxfl);
      }
      ///////////////      //Posicion y
      for (int i=0;i<5;i++){
        vectP0[i]=P0[i];
      }
      msg=true;
    }
}

void MoveMotors(){
    done = 0;
    for (i = 0; i <= 4; i++) {
      if (P0[i] == P1[i]) {
        done = done +1;
      }
      else {
        
        if (P0[i] < P1[i]) {
          //P0[i] = P1[i];
          auxfl1[i]=vectP0[i]+increment[i];
          vectP0[i]=auxfl1[i];
          P0[i] =(int)auxfl1[i];
          if (P0[i] > P1[i]){
            P0[i] = P1[i];
          }
          pwm.setPWM(i, 0, P0[i]);
        }
        else {
          auxfl1[i]=vectP0[i]-increment[i];
          vectP0[i]=auxfl1[i];
          P0[i] =(int)auxfl1[i];
          if (P0[i] < P1[i]){
            P0[i] = P1[i];
          }
          pwm.setPWM(i, 0, P0[i]);
        }
        Serial.println(P0[i]);
      }
    }
   delay(6);
   if((done==5)&& msg ){
    Serial.println(".");
    msg=false;
   }
}


void funapagado(){
  // alimentado de raspberry
  if(digitalRead(pinresep)==LOW){
    digitalWrite(pinapagado,HIGH);
  }
  

}
void loop()
{
  lecturadatos();
  condicion1();// version del dispositvo
  condicion2();// si ya llego al punto
  Optencion_Puntos();
  //ejecucion del movimiento
  MoveMotors();
  funapagado();
}

void stop4axis(){
  valorInnterruot=P0[4];
  P1[4]=valorInnterruot+1;
  //Serial.print(P0[4]);
}

