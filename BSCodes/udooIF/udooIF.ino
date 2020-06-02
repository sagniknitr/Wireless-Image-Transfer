#include <MQ135.h>

#include <ctype.h>

#include <TinyGPS.h>

String GPS_latitude="NA";
String GPS_longitude = "NA";
String GPS_altitude = "NA";
String GPS_kmph = "NA";

#define gpsSerial Serial3

#include <MT_GPS.h>

MQ135 MQ135Sensor = MQ135(A8);

int UVOUT = A7; //Output from the sensor
int REF_3V3 = A0; //3.3V power on the Arduino board
int SHT_clockPin = 11;  // pin used for clock
int SHT_dataPin  = 10;  // pin used for data
int s1=0;
int s2=0;
int s3=0;
int s4=0;
String  t="",lat="",lon="",alt="",speed1="",ultimate="",ultimate1="";
int bytes,bytes_t,bytes_lat,bytes_long,bytes_alti,bytes_spd;
int byte_gps=-1;
char a;
char t_array[20],lat_array[20],long_array[30],waste[30],alti[20],spd[30];
int i=0,j=0,k=0;
char GPGGA_array[40];


char *dtostrf (double val, signed char width, unsigned char prec, char *sout) {
  char fmt[20];
  sprintf(fmt, "%%%d.%df", width, prec);
  sprintf(sout, fmt, val);
  return sout;
}


void config_sensors()
{

  Serial3.begin(9600);
  pinMode(A0,OUTPUT); /// -----> CANT USE 0 AS IT IS SERIAL0s PIN
  pinMode(UVOUT, INPUT);
  pinMode(REF_3V3, INPUT);
  pinMode(A1,INPUT);
  pinMode(A6,INPUT);
  //pinMode(A8,INPUT);
  pinMode(A9,INPUT);
  pinMode(42,OUTPUT);
 
}

void configuration()
{
  #define xtend Serial2

  #define xtend_pin 42
  
  #define xtend_baud 9600
  // why restarted udoo ???.............

    // put your setup code here, to run once:
  delay(5000);
  Serial.begin(9600);
  
  xtend.begin(xtend_baud);
  //Serial.println("Script started....");
  xtend.println("Script started....");

  pinMode(xtend_pin,OUTPUT);
  digitalWrite(xtend_pin,HIGH);
  
  while(xtend.available())xtend.read(); //flush input 

  gpsSerial.begin(9600);
 
}



void setup() {

config_sensors();
configuration();

}



int find_text(String needle, String haystack) 
{
  int foundpos = -1;

  // for (int i = 0; (i < haystack.length() - needle.length()); i++) ---> this line is present in the above link and is incorrect
  
  // for (int i = 0; (i < haystack.length() - needle.length() + 1); i++)  --> this the correction - haystack.length() - needle.length() + 1
  
  for (int i = 0,haystacklength = haystack.length(),needlelength = needle.length(); (i < haystacklength - needlelength + 1); i++) // modified for performance improvement

  {
      // if (haystack.substring(i,needle.length()+i) == needle) --> this line was present originally 

      if (haystack.substring(i,needlelength+i) == needle) // modified for performance improvement
      {
        foundpos = i;
      }
  }
     
    return foundpos;
}

int find_line(String input,char *output,int offset=0)
{
  int found = -1;
  int input_len = input.length();

  for(int i=offset;  i<input_len;  i++)
  {
    if(input[i]=='\n') {found=i;break;}
  }

  if(found!=-1)
  {
    for(int i=offset; i<=found; i++)
    {
      output[i-offset]=input[i]; 
    }
  }

  return found;
  
}


String check_basestation_command()
{
  String cmd = "";
  if(xtend.available()>0)
  {
    for(int i=0;  i<30 && xtend.available();  i++)
    {
      cmd+=(char)xtend.read();
    }

    int index = find_text("BS",cmd);
    //if not found

    //xtend.println(index);return "";
    if(index==-1)
    {
      //flush input
      while(xtend.available())xtend.read();
      return "invalidCommand:" + cmd;
    }
    else
    {
      char line[20];
      for(int i=0;i<20;i++)line[i]=0;
      find_line(cmd,line,index);
      return String(line);
    }
    
  }
  else
  {
    return "noCommand";
  }
}

String check_udoo_command()
{
  String cmd = "";
  
  while(Serial.available())Serial.read();
  unsigned long now = millis();
  unsigned long timeout = 20000; // in ms

  //xtend.print("waiting\n");
  
 
  
  while(!Serial.available() && millis()-now < timeout);
  delay(500);
  
  if(Serial.available()>0)
  {
    for(int i=0;  i<30 && Serial.available();  i++)
    {
      cmd+=(char)Serial.read();
    }

    int index = find_text("BS",cmd);
    //if not found

    //xtend.println(index);return "";
    if(index==-1)
    {
      //flush input
      while(Serial.available())Serial.read();
      return "invalidCommand:" + cmd;
    }
    else
    {
      char line[20];
      for(int i=0;i<20;i++)line[i]=0;
      find_line(cmd,line,index);
      return String(line);
    }
    
  }
  else
  {
    return "noCommand\n";
  }
}

void pipe_image(unsigned long timeout=30)
{
 unsigned long now = millis();
  
  while(1)
  {
    
    if(Serial.available())xtend.write(Serial.read());
    //xtend.println(millis()-now);

    if(millis()-now>1000*timeout)break;
    if(millis()<now)break;
  }
  //xtend.print("pipe complete...");
}



void serve()
{
    // put your main code here, to run repeatedly:


   //delay(5000);
   String x= check_basestation_command();
   if(find_text("BS",x)!=-1)
   {
     Serial.print(x);
     //Serial.println("BS+PULLIMG");
  
     //delay(7000);
     
     x= check_udoo_command();
     xtend.print(x);
     
     if(find_text("BS",x)==-1);
     else
     {
       String img_size = x.substring(find_text("=",x)+1,x.length()-1);
       char img_size_char[10]={0,0,0,0,0,0,0,0,0,0};
       for(int i=0,l=img_size.length();i<l;i++)
       {
        img_size_char[i] = img_size[i];
       }
       int img_len = atoi(img_size_char);
       int timeout = ( img_len / (xtend_baud/10) ) + 7   ; // % seconds safety factor
       
       pipe_image(timeout);
     }
   }
   
  else
   {
   //if(xtend.available())while(xtend.available()) Serial.write(xtend.read());
    //xtend.println("rcvd cmd:"+x);
    
    delay(100);
    
   }
}


void loop() {

  serve();
  readSensors();
  delay(1000);
}


//////////////////   SENSOR CODES  /////////////////////////


int averageAnalogRead(int pinToRead)
{
  byte numberOfReadings = 8;
  unsigned int runningValue = 0; 
  for(int x = 0 ; x < numberOfReadings ; x++)
    runningValue += analogRead(pinToRead);
  runningValue /= numberOfReadings;
  return(runningValue);  
}
float mapfloat(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
float sensorvalues()
{
  int uvLevel = averageAnalogRead(UVOUT);
  int refLevel = averageAnalogRead(REF_3V3);
  float outputVoltage = 3.3 / refLevel * uvLevel;
  float uvIntensity = mapfloat(outputVoltage, 0.99, 2.8, 0.0, 15.0); //Convert the voltage to a UV intensity level
  
  //delay(1000);
  Serial3.write(13);//ASCII Carriage return=13
  ultimate="";
  ultimate1="";
}

char prepareGPS()
{
  char gps_available_flag = 0;
  
  if (getGPSlatLonAlt())
  {
    char GPSlat[12],GPSlon[12],GPSalt[12];
    
    dtostrf(GPSflat,8,7,GPSlat);  //convert float to char[] buffer/array
    dtostrf(GPSflon,8,7,GPSlon);
    dtostrf(GPSfalt,8,7,GPSalt);
    
    GPS_latitude = String(GPSlat);
    GPS_longitude = String(GPSlon);
    GPS_altitude = String(GPSalt);
    GPS_kmph = String(GPSkmph);
    
    //Serial.print("Actual: ") ; Serial.println(GPSflat,7);
    //Serial.println(GPS_latitude);
    //return;
 
    Serial.println("LAT : " + GPS_latitude);
    Serial.println("LON : " + GPS_longitude);

    
    //Serial.println(String(GPSsentences));
    
    gps_available_flag=1;
  }
  
  if(gps_available_flag)
  {
    return 1; 
  }
  else
  {
    
    return 0;
  }
 
}


void readSensors()
{
  prepareGPS();
  s1=analogRead(A1);
  s2=analogRead(A6);
  float MQ135ppm = MQ135Sensor.getPPM();
  s3 = (int) MQ135ppm;
  //s3=analogRead(A8);
  s4=analogRead(A9);
  digitalWrite(42,HIGH);
  float sen=sensorvalues();
  String datastr =String(s1)+","+String(s2)+","+String(s3)+","+String(s4)+ "," +
      
    GPS_latitude + "," + 
    GPS_longitude + "," + 
    GPS_altitude + "," + 
    GPS_kmph ;
  //Serial.println(datastr);
  xtend.println(datastr);
}

