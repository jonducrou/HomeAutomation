#include "LowPower.h"
#include <Adafruit_CC3000.h>
#include <ccspi.h>
#include <SPI.h>
#include <string.h>

#define ADAFRUIT_CC3000_IRQ   2  // MUST be an interrupt pin!
#define ADAFRUIT_CC3000_VBAT  9
#define ADAFRUIT_CC3000_CS    10

Adafruit_CC3000 cc3000 = Adafruit_CC3000(ADAFRUIT_CC3000_CS, ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT,
                                         SPI_CLOCK_DIV2); // you can change this clock speed but DI

#define WLAN_SSID       "Unmarked_ASIO_Van"        // cannot be longer than 32 characters!
#define WLAN_PASS       "ThreeThousandThistles"
#define WLAN_SECURITY   WLAN_SEC_WPA2

#define apiKey "KEY_HERE"
#define SMTP_ENDPOINT "www.devicehub.net"
#define IDLE_TIMEOUT_MS 3000
#define CONNECT_TIMEOUT_MS 60000



#define SENSOR_POWER 7
#define SENSOR_ONE 14
#define SENSOR_TWO 15

#define LED_OUT 13

void setup(void)
{
  Serial.begin(115200);
  pinMode(SENSOR_POWER, OUTPUT);     
  pinMode(LED_OUT, OUTPUT);     
  pinMode(SENSOR_ONE, INPUT);   
  digitalWrite(SENSOR_ONE, HIGH);   
  pinMode(SENSOR_TWO, INPUT);   
  digitalWrite(SENSOR_TWO, HIGH);   
  digitalWrite(LED_OUT, LOW);   
  Serial.println(F("Hello, WaterPlease!\n")); 
  delay(100);
}


void enableSensors(){
    digitalWrite(SENSOR_POWER, HIGH);
}

void disableSensors(){
    digitalWrite(SENSOR_POWER, LOW);
}

boolean isDry(int pin) {
  boolean res = 1 == digitalRead(pin);
  return res;
}

void lowPowerFor4000S(){
for (int i = 0; i < 500; ++i)
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);  
    // See more at: http://www.rocketscream.com/blog/2011/07/04/lightweight-low-power-arduino-library/#sthash.HThYtxuS.dpuf
}

void sendAndRead(Adafruit_CC3000_Client & www, char * out) {
    www.println(out);
    Serial.println(out);
    while (www.available()) {
      char c = www.read();
      Serial.print(c);
    }
}

void callWeb(char * tag) {
  
  Serial.print("Sending tag: ");
  Serial.println(tag);
  
  /* Initialise the module */
  Serial.println(F("\nInitializing..."));
  if (!cc3000.begin())
  {
    Serial.println(F("Couldn't begin()! Check your wiring?"));
    return;
  }
  
  if (!cc3000.connectToAP(WLAN_SSID, WLAN_PASS, WLAN_SECURITY)) {
    Serial.println(F("Failed!"));
    return;
  }
   
  Serial.println(F("Connected!"));
  
  unsigned long lastRead = millis();
  /* Wait for DHCP to complete */
  Serial.println(F("Request DHCP"));
  while (!cc3000.checkDHCP() && (millis() - lastRead < CONNECT_TIMEOUT_MS))
  {
    delay(100); 
    lastRead = millis();
  }  

  Serial.println(F("DHCP Complete!"));
  /* Display the IP address DNS, Gateway, etc. */  
  uint32_t ipAddress, netmask, gateway, dhcpserv, dnsserv;
  
  while(!cc3000.getIPAddress(&ipAddress, &netmask, &gateway, &dhcpserv, &dnsserv) && (millis() - lastRead < CONNECT_TIMEOUT_MS)){
    delay(1000);
     lastRead = millis();
  }
  

  uint32_t ip = 0;
  // Try looking up the website's IP address
  Serial.print(SMTP_ENDPOINT); Serial.print(F(" -> "));
  while (ip == 0) {
    if (! cc3000.getHostByName(SMTP_ENDPOINT, &ip)) {
      Serial.println(F("Couldn't resolve!"));
    }
    delay(500);
  }

  cc3000.printIPdotsRev(ip);

  Adafruit_CC3000_Client www = cc3000.connectTCP(ip, 80);
  Serial.println("connect tcp");
  if (www.connected()) {
    www.print(F("GET /io/537/?apiKey=" apiKey "&HerbGarden="));
    www.print(tag);
    www.println(F(" HTTP/1.1"));
    www.println(F("Host: www.devicehub.net"));
    www.print(F("User-Agent: "));
    www.println(F("devicehub"));
    www.println(F("Connection: close"));
    www.println();
  } else {
    Serial.println(F("Connection failed"));    
    return;
  }

  Serial.println(F("-------------------------------------"));
  
  /* Read data until either the connection is closed, or the idle timeout is reached. */ 
  lastRead = millis();
  while (www.connected() && (millis() - lastRead < IDLE_TIMEOUT_MS)) {
    while (www.available()) {
      char c = www.read();
      Serial.print(c);
      lastRead = millis();
    }
  }
  www.close();
  Serial.println(F("-------------------------------------"));
  
  /* You need to make sure to clean up after yourself or the CC3000 can freak out */
  /* the next time your try to connect ... */
  Serial.println(F("\n\nDisconnecting"));
  cc3000.disconnect();
  
}

void loop(void)
{
  lowPowerFor4000S();

  enableSensors();
  boolean isDryOne = isDry(SENSOR_ONE);
  boolean isDryTwo = isDry(SENSOR_TWO);
  disableSensors();

  if (isDryOne || isDryTwo)
    callWeb("1");
  else
    callWeb("0");

}

