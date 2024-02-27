int l1green = 5;
int l2green = 6;
int l1red = 7;
int l2red = 8;
void setup()
{
Serial.begin(9600);
pinMode(l1green, OUTPUT);
pinMode(l2green, OUTPUT);
pinMode(l1red, OUTPUT);
pinMode(l2red, OUTPUT);
}
void normal()
{
if(Serial.available())
{
String val = Serial.readStringUntil('\n');
int commaIndex = val.indexOf(',');
String str1 = val.substring(0, commaIndex);
String str2 = val.substring(commaIndex+1);
int pc_data = str1.toInt();
int m = str2.toInt();
if(pc_data == 1)
{
lane1(m);
}
else if(pc_data == 2)
{
lane2(m);
}
}
else
{
digitalWrite(l1green, HIGH);
digitalWrite(l2green, LOW);
digitalWrite(l1red, LOW);
digitalWrite(l2red, HIGH);
delay(2000);
digitalWrite(l1green, LOW);
digitalWrite(l2green, HIGH);
digitalWrite(l1red, HIGH);
digitalWrite(l2red, LOW);
delay(2000);
}
}
void loop()
{
normal();
}
int lane1(int a)
{
int e=a*1000;
digitalWrite(l1green, HIGH);
digitalWrite(l2green, LOW);
digitalWrite(l1red, LOW);
digitalWrite(l2red, HIGH);
delay(e);
int f=(30-a)*1000;
digitalWrite(l2green, HIGH);
digitalWrite(l1green, LOW);
digitalWrite(l2red, LOW);
digitalWrite(l1red, HIGH);
delay(f);
}
int lane2(int b)
{
int g=b*1000;
digitalWrite(l1green, LOW);
digitalWrite(l2green, HIGH);
digitalWrite(l1red, HIGH);
digitalWrite(l2red, LOW);
delay(g);
int h=(30-b)*1000;
digitalWrite(l1green, HIGH);
digitalWrite(l2green, LOW);
digitalWrite(l1red, LOW);
digitalWrite(l2red, HIGH);
delay(h);
}