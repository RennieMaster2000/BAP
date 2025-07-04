/*********************************************************************
 This is an example for our nRF52 based Bluefruit LE modules

 Pick one up today in the adafruit shop!

 Adafruit invests time and resources providing this open source code,
 please support Adafruit and open-source hardware by purchasing
 products from Adafruit!

 MIT license, check LICENSE for more information
 All text above, and the splash screen below must be included in
 any redistribution
*********************************************************************/



 /*
 Behavioural analysis
 - Receives bluetooth prints on Serial
 - Starts the other's counter via bluetooth


 */

#include <bluefruit.h>
#include <Arduino.h>
#include <Adafruit_LittleFS.h>
#include <Adafruit_TinyUSB.h>
#include <InternalFileSystem.h>

#define integratorPin 6
#define sensorPin 9
#define chargePin A3

// BLE Service
BLEDfu  bledfu;  // OTA DFU service
BLEDis  bledis;  // device information
BLEUart bleuart; // uart over ble
BLEBas  blebas;  // battery


void setup()
{
  initPins();
  Serial.begin(115200);
  



  
  Serial.println("Bluefruit52 BLEUART Example");
  Serial.println("---------------------------\n");

  // Setup the BLE LED to be enabled on CONNECT
  // Note: This is actually the default behavior, but provided
  // here in case you want to control this LED manually via PIN 19
  Bluefruit.autoConnLed(true);

  // Config the peripheral connection with maximum bandwidth 
  // more SRAM required by SoftDevice
  // Note: All config***() function must be called before begin()
  Bluefruit.configPrphBandwidth(BANDWIDTH_MAX);

  Bluefruit.begin();
  Bluefruit.setTxPower(4);    // Check bluefruit.h for supported values
  //Bluefruit.setName(getMcuUniqueID()); // useful testing with multiple central connections
  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);

  // To be consistent OTA DFU should be added first if it exists
  bledfu.begin();

  // Configure and Start Device Information Service
  bledis.setManufacturer("Adafruit Industries");
  bledis.setModel("Bluefruit Feather52");
  bledis.begin();

  // Configure and Start BLE Uart Service
  bleuart.begin();

  // Start BLE Battery Service
  blebas.begin();
  blebas.write(100);

  // Set up and start advertising
  startAdv();

  Serial.println("Please use Adafruit's Bluefruit LE app to connect in UART mode");
  Serial.println("Once connected, enter character(s) that you wish to send");
}

void startAdv(void)
{
  // Advertising packet
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();

  // Include bleuart 128-bit uuid
  Bluefruit.Advertising.addService(bleuart);

  // Secondary Scan Response packet (optional)
  // Since there is no room for 'Name' in Advertising packet
  Bluefruit.ScanResponse.addName();
  
  /* Start Advertising
   * - Enable auto advertising if disconnected
   * - Interval:  fast mode = 20 ms, slow mode = 152.5 ms
   * - Timeout for fast mode is 30 seconds
   * - Start(timeout) with timeout = 0 will advertise forever (until connected)
   * 
   * For recommended advertising interval
   * https://developer.apple.com/library/content/qa/qa1931/_index.html   
   */
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(32, 244);    // in unit of 0.625 ms
  Bluefruit.Advertising.setFastTimeout(30);      // number of seconds in fast mode
  Bluefruit.Advertising.start(0);                // 0 = Don't stop advertising after n seconds  
}

void loop()
{
  // Forward data from HW Serial to BLEUART
  while (Serial.available())
  {
    // Delay to wait for enough input, since we have a limited transmission buffer
    delay(2);

    unsigned long stringThree;
    //in the void loop:
    ///////////////////////!!!!!!!!!!!!!!!Stuck in loop cuz doesn't read serial
    //stringThree =  millis();
    char charBuf[20];
    //itoa(stringThree, charBuf, 10);
    Serial.readBytes(charBuf,19);
    Serial.write("[Sensor(TX)]: ");
    Serial.write(charBuf);
    Serial.write('\n');
    bleuart.write(charBuf);
    ParseCommand(charBuf);
  }

  // Forward from BLEUART to HW Serial
  if(bleuart.available()){
    Serial.write("[PC(RX)]: ");
    char charBuf[20];
    int i = 0;
    while ( bleuart.available() )
    {
      uint8_t ch;
      ch = (uint8_t) bleuart.read();
      charBuf[i] = ch;
      i++;
      Serial.write(ch);
    }
    ParseCommand(charBuf);
  }
}

// callback invoked when central connects
void connect_callback(uint16_t conn_handle)
{
  // Get the reference to current connection
  BLEConnection* connection = Bluefruit.Connection(conn_handle);

  char central_name[32] = { 0 };
  connection->getPeerName(central_name, sizeof(central_name));

  Serial.print("Connected to ");
  Serial.println(central_name);
}

/**
 * Callback invoked when a connection is dropped
 * @param conn_handle connection where this event happens
 * @param reason is a BLE_HCI_STATUS_CODE which can be found in ble_hci.h
 */
void disconnect_callback(uint16_t conn_handle, uint8_t reason)
{
  (void) conn_handle;
  (void) reason;

  Serial.println();
  Serial.print("Disconnected, reason = 0x"); Serial.println(reason, HEX);
}
void initPins(void){
  pinMode(sensorPin, OUTPUT);
  pinMode(integratorPin,OUTPUT);
  digitalWrite(sensorPin,LOW);
  digitalWrite(integratorPin,LOW);
  analogReadResolution(12);
  analogReference(AR_INTERNAL_1_2);
}
void sendM(char* str){
  Serial.write("[Sensor(TX)]: ");
  Serial.write(str);
  Serial.write('\n');
  bleuart.write(str);
}
void sendMeasurement(int charge){
  String chargeString = String(charge);
  sendM("(Meas)");
  char chargeChar[20];
  chargeString.toCharArray(chargeChar,20);
  sendM(chargeChar);
}
void measureCycle(void){
  Serial.print("Starting measurement1\n");
  //Sensor on
  //digitalWrite(integratorPin,HIGH);//--
  digitalWrite(sensorPin,HIGH);
  Serial.print("Sensor on\n");
  //Wait till start integration window
  delay(2000);//2s
  //Integrator on
  digitalWrite(integratorPin,HIGH);//HIGH
  Serial.print("Integrator on\n");
  //Wait till end integration window
  delay(20000);//22s
  //Integrator off, send measurement
  sendMeasurement(analogRead(chargePin));
  
  Serial.print("Send measurement\n");
  digitalWrite(integratorPin,LOW);
  Serial.print("Integrator off\n");
  //Wait till end meaurement window
  delay(1000);//1s
  //Sensor off
  digitalWrite(sensorPin,LOW);
  Serial.print("Sensor off\n");
  //Wait till end measurement cycle
  //delay(277000);//5min/300s
  Serial.print("Finished measurement\n");
}
void ParseCommand(char* com){
  if(com[0]=='%'){
    if(com[1]=='1'){
      measureCycle();
    }
    else if(com[1]=='a'){
      digitalWrite(sensorPin,HIGH);
    }
    else if(com[1]=='b'){
      digitalWrite(sensorPin,LOW);
    }
    else if(com[1]=='c'){
      digitalWrite(integratorPin,HIGH);
    }
    else if(com[1]=='d'){
      digitalWrite(integratorPin,LOW);
    }
    else if(com[1]=='e'){
      sendMeasurement(analogRead(chargePin));
    }
    else if(com[1]=='2'){
      AlternativeMeas();
    }
  }
}
void AlternativeMeas(){
  Serial.print("Starting measurement2\n");
  digitalWrite(sensorPin,HIGH);
  Serial.print("Sensor on\n");
  //Wait till start integration window
  delay(2000);//2s
  for(int i = 0; i <10;i++){
      Serial.print("Measurement ");
      Serial.print(i);
      Serial.print('\n');
      sendMeasurement(analogRead(chargePin));
      delay(2000);//2s
  }
  delay(1000);
  digitalWrite(sensorPin,LOW);
  Serial.print("Sensor off\n");
  Serial.print("Measurement finished\n");
}
