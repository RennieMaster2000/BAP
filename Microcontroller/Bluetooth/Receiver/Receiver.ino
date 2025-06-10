#include <ArduinoBLE.h>
#include <U8x8lib.h>
#include <Wire.h>
//BLEIntCharacteristic* chargeCharacteristic;//Pointers?
//BLEUnsignedCharCharacteristic* countCharacteristic;

unsigned char lastCount = 99;
void setup(){
    unsigned char newCount;
    //Initialize
    Serial.begin(9600);
    Serial.print("Welcome, Initialising...\n");
    BLE.begin();
    Serial.print("Initialised!\n");

    //Connecting
    BLE.scanForName("Sensor CGM");
    BLEDevice peripheral;
    while(!peripheral){
        Serial.print("Waiting for connection...\n");
        peripheral = BLE.available();
        delay(100);
    }
    Serial.print("Connecting...\n");
    if (peripheral.connect()) Serial.println("Connected!\n");
    else {
        Serial.println("Failed to connect!");
        while(1);
    }
    BLE.stopScan();

    //Init Characteristics
    peripheral.discoverAttributes();
    BLECharacteristic chargeCharacteristic = peripheral.characteristic("8bc73d37-89f4-4d93-9695-21e7262050da");
    BLECharacteristic countCharacteristic = peripheral.characteristic("30e2e053-2e54-480c-9cb6-d74ad8b00345");

    while(1){
      
      if(peripheral.connected()){
          newCount = countCharacteristic.value();
          if(newCount!=lastCount){
            NewCharge(chargeCharacteristic.value());
          }
      }
      delay(100);
    }
}

void loop(){
}

void NewCharge(int charge){
    Serial.print("New charge: ");
    Serial.print(charge);
    Serial.print("\n");
}
