#include <ArduinoBLE.h>
#include <U8x8lib.h>
#include <Wire.h>

//Define Service and Characteristic
BLEService directService("522aa7ea-d185-48c3-9319-bd14e1b60bfa");

BLEIntCharacteristic chargeCharacteristic("8bc73d37-89f4-4d93-9695-21e7262050da",BLERead);
BLEUnsignedCharCharacteristic countCharacteristic("30e2e053-2e54-480c-9cb6-d74ad8b00345",BLERead);

unsigned char  count = 0;

const int ledPin = LED_BUILTIN;

void setup(){
    pinMode(ledPin, OUTPUT);

    //Init Serial
    Serial.begin(9600);
    Serial.print("Welcome, Initializing...\n")

    //Setup Bluetooth
    if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy module failed!");

    while (1);
    }

    BLE.setLocalName("Sensor CGM");
    BLE.setAdvertisedService(directService);

    directService.addCharacteristic(chargeCharacteristic);
    directService.addCharacteristic(countCharacteristic);
    BLE.addService(directService);

    chargeCharacteristic.writeValue(0);
    countCharacteristic.writeValue((unsigned char)0);

    //Advertise
    BLE.advertise();
    Serial.print("Initialized!\n")
}

int values[10] = [1,22,333,4444,55555,6666,777,88,9,0]
int i = 0;
void loop(){
    //Usual
    SendMeasurement(values[i]);
    i++;
    if(i==10) i=0;
    delay(1000);
}

BLEDevice central;
void SendMeasurement(int value){
    //Update count and charge

    //Check if connected
    if(central){
        //Connected
        count++;
        chargeCharacteristic.writeValue(value);
        countCharacteristic.writeValue(count);
        Serial.print("Writing Charge ");
        Serial.print(value);
        Serial.print(" Count ");
        Serial.print(count);
        Serial.print("\n");
    }
    else{
        //Not connected
        //Check for new connections
        Serial.print("Looking for connection\n");
        central = BLE.central();
        if(central) Serial.print("Connection found!\n");
        else Serial.print("Connection not found!\n");
    }
}