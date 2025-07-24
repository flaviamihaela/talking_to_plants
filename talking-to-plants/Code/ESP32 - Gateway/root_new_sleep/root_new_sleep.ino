// Root ESP => No HTTP
#include "driver/gpio.h"
#include "painlessMesh.h"
#include <ArduinoJson.h>
#include <Arduino.h>
#include <HardwareSerial.h>
#include <string.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <stdio.h>
#include <stdbool.h>

HardwareSerial SerialPort(2); // use UART2

// WiFi Credentials
#define   MESH_PREFIX     "whateverYouLike"
#define   MESH_PASSWORD   "somethingSneaky"
#define   MESH_PORT       5555


// Variables
SimpleList<uint32_t> nodes;
char buff[7000];
int root = 0;
int numNodes = 0;
int nodeList[100];
uint8_t imageNum = 0;
uint8_t segmentNum = 0;
uint8_t totalSegmentNum = 0;
uint8_t runNum = 1;
int numImage = 0;
int timeDiff = 0;
int bufferPoint = 0;
int nodeID = 123;
int mode = 0; // SMFI = 0, MSI = 1
StaticJsonDocument<1024> doc;
Scheduler userScheduler; // To control your personal task
painlessMesh  mesh;
char frequencyTable [3] ;
char timeDiffTable[4];


// Tables arrays for lookup fast
static bool __TABLE_INIT= false;
static unsigned int TABLE_EV[256];

unsigned char reverse(unsigned char b) {
   b = (b & 0xF0) >> 4 | (b & 0x0F) << 4;
   b = (b & 0xCC) >> 2 | (b & 0x33) << 2;
   b = (b & 0xAA) >> 1 | (b & 0x55) << 1;
   return b;
}

// Input is start of char array address & n == number of bytes
unsigned int CRC32_Table(unsigned char  * bytes, int n)
{
    const unsigned int polynomial = 0x04C11DB7; /* Divisor is 32bit */
    unsigned int crc = 0xffffffff; /* CRC value is 32bit */
    unsigned char b;
    unsigned char bk;

    if (__TABLE_INIT) {
        // Nothing to do - follow by lookup
    } 
    else {
        // Init all tables first 
            for (int j = 0; j < 256; j++){
             b = j; crc = 0;
                     crc ^= (unsigned int)(b << 24);  // Move byte into MSB of 32bit CRC 
                     for (int k = 0; k < 8; k++)
                     {
                         if ((crc & 0x80000000) != 0)  // Test for MSB = bit 31 
                         {
                             crc = (unsigned int)((crc << 1) ^ polynomial);
                         }
                         else
                         {
                             crc <<= 1;
                         }
                     }
             // Now add value to table
             TABLE_EV[j] = crc;
        } // j 0-255
            __TABLE_INIT = true;
    }
    // Start calculations
    crc = 0xffffffff; /* CRC value is 32bit */

    for (int j=0; j<n; j++)
    {
        b = bytes[j];
        b = reverse(b); bk = b;
        b = b ^ ((crc>>24) & 0x0ff);
        crc = (crc<<8) ^ TABLE_EV[b]; 
        //printf("2..Computing for %x %x is %x\n",bk,b,crc);

    }

    crc = crc ^ 0xffffffff;
    // NOW REVERSE COMPLETE 32 bit WORD BIT BY BIT 
    crc = 
        reverse((crc & 0xff000000)>>24)   + 
    (reverse((crc & 0x00ff0000)>>16)<<8)   + 
    (reverse((crc & 0x0000ff00)>>8)<<16)   + 
    (reverse((crc & 0x000000ff))<<24) ;

    return crc;
}
// Sends the packet delimiter start
void sendUartStart();

void sendUartStart(){
  SerialPort.write('\r');
};

// Sends the packet delimiter end
void sendUartEnd();

void sendUartEnd(){
  SerialPort.write('\r');
  SerialPort.write('\n');
  SerialPort.write('\r');
  SerialPort.write('\n');
};

void sendMessage(); 

// Routine service
//Task taskSendMessage( TASK_SECOND * 10 , TASK_FOREVER, &sendMessage );

void sendMessage(){
  // Can be used to add functionality
};

// Save message packet and send to SPRESENSE => then send message back once completed
void receivedCallback( uint32_t from, String &msg ) {
  /*
  // Send msg through UART to SPRESENSE
  for (int i = 0 ; i<msg.length ; i++){
    SerialPort.write(msg[i]);
    if (i%128==0){
      delay(500) ; // delay 0.5s every 128 bytes
    }
  }
  // Done sending through UART
  // Send message to "from" to inform ready for next packet
  String str = "D";
  mesh.sendSingle(from, str);
  Serial.println("EndTime");
  */
  // [TODO] Send datapacket to web server [add]

  Serial.println(msg);
  // Print msg

  // Sends message to cloud !!
  //msg.remove(0, 3); // Removes first 3 char

  // Send msg via uart to Gateway
  // Send starting message
  sendUartStart();
  // Send nodeID
  char byte1 = (from >> 24) & 0xFF;
  char byte2 = (from >> 16) & 0xFF;
  char byte3 = (from >> 8) & 0xFF;
  char byte4 = from & 0xFF;
  /*
  char char1 = static_cast<char>(byte1);
  char char2 = static_cast<char>(byte2);
  char char3 = static_cast<char>(byte3);
  char char4 = static_cast<char>(byte4);
  */
  SerialPort.write(byte1);
  SerialPort.write(byte2);
  SerialPort.write(byte3);
  SerialPort.write(byte4);

  // Send message 
  for (int g = 0 ; g<msg.length() ; g+=2){
    // Get char value from Hex string
    int val = 0;
    for (int i = 0; i < 2; i++) {
      val *= 16;  // Shift left by one hexadecimal digit
      if (msg[g+i] >= '0' && msg[g+i] <= '9') {
        val += msg[g+i] - '0';  // Convert digit from ASCII to decimal
      } else if (msg[g+i] >= 'A' && msg[g+i] <= 'F') {
        val += msg[g+i] - 'A' + 10;  // Convert letter from ASCII to decimal
      } else if (msg[g+i] >= 'a' && msg[g+i] <= 'f') {
        val += msg[g+i] - 'a' + 10;  // Convert letter from ASCII to decimal
      }
    }
    printf("%d", val);
    SerialPort.write(val);
    if (g%256==0){
      delay(5) ; // Delay 0.005s every 128 bytes
    }
  }
  sendUartEnd();
  // Wait for response from gateway
  while(true){
    if (SerialPort.available()){
      char newByte = SerialPort.read();
      if(newByte=='\r'){
        Serial.println("Done");
        String returnMsgg = "done";
        mesh.sendSingle(from, returnMsgg);
        break;
      }
      else if (newByte == '\n'){
        Serial.println("Final Image");
        // Check for the new frequencies 
        frequencyTable[0] = SerialPort.read();
        frequencyTable[1] = SerialPort.read();
        frequencyTable[2] = SerialPort.read();
        numImage = SerialPort.read();
        mode = SerialPort.read();
        //timeDiff = SerialPort.read();
        for (int i = 0 ; i <4 ; i++){
          timeDiffTable[i] = SerialPort.read();
        }

        /*
        timeDiff = (static_cast<unsigned long>(byte1) << 24) |
                           (static_cast<unsigned long>(byte2) << 16) |
                           (static_cast<unsigned long>(byte3) << 8) |
                           static_cast<unsigned long>(byte4);
        */
        // Send to node that it is done
        char returnMsg[30];
        returnMsg[0] = 0;

        // Start from 4th index => 1&2 are image number , 3&4 are segment number
        //sprintf(msg+strlen(msg),"0x");
        
        for (int i = 0; i < 3; i++){
          sprintf(returnMsg + strlen(returnMsg), "%02.2X", frequencyTable[i]);
          //char str[2] = {buff[i], '\0'}; // Convert current character in buff to a null-terminated string
          //strcat(msg, str); // Append the string to msg
        }
        sprintf(returnMsg + strlen(returnMsg), "%02.2X", numImage);
        //sprintf(returnMsg + strlen(returnMsg), "%02.2X", timeDiff);
        sprintf(returnMsg + strlen(returnMsg), "%02.2X", mode);
        for (int i = 0 ; i<4 ; i++){
          sprintf(returnMsg + strlen(returnMsg), "%02.2X", timeDiffTable[i]);
        }
        Serial.println(returnMsg);
        mesh.sendSingle(from, returnMsg);
        break;
      }
    }
  }
}

void newConnectionCallback(uint32_t nodeId) {
  Serial.printf("--> startHere: New Connection, nodeId = %u\n", nodeId);
  Serial.printf("--> startHere: New Connection, %s\n", mesh.subConnectionJson(true).c_str());
  // Prints mesh subconnections
}

// Create & save layout of node tree
void changedConnectionCallback() {
  Serial.printf("Changed connections\n");
  nodes = mesh.getNodeList();
  numNodes = nodes.size();
  Serial.printf("Num nodes: %d\n", numNodes);
  Serial.printf("Connection list:");
  // Does not contain itself
  SimpleList<uint32_t>::iterator node = nodes.begin();
  int nodeCount = 0;
  while (node != nodes.end()) 
    {
    nodeList[nodeCount] = *node ; // Adds subnodes into list
    //Serial.println(nodeList[nodeCount]);
    Serial.printf(" %u", *node);
    node++;
    nodeCount +=1;
    }
  
  Serial.println();
  
  long nodeId = mesh.getNodeId();
  Serial.print("nodeID =  ");
  Serial.println(nodeId);
  Serial.print("stuff");
  // Broadcast message that it is node
  String msg = "root";
  mesh.sendBroadcast(msg);
}

void nodeTimeAdjustedCallback(int32_t offset) {
  Serial.printf("Adjusted time %u. Offset = %d\n", mesh.getNodeTime(), offset);
}

void setup() {

  // Put your setup code here, to run once:
  Serial.begin(115200);
  SerialPort.begin(115200, SERIAL_8E1, 16, 17); 
  // 16 is RX
  // 17 is TX
  gpio_set_direction(GPIO_NUM_0, GPIO_MODE_OUTPUT);
  //mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE ); // All types on
  mesh.setDebugMsgTypes( ERROR | STARTUP );  // Set before init() so that you can see startup messages
  mesh.init( MESH_PREFIX, MESH_PASSWORD, &userScheduler, MESH_PORT );
  mesh.onReceive(&receivedCallback);
  mesh.onNewConnection(&newConnectionCallback);
  mesh.onChangedConnections(&changedConnectionCallback);
  mesh.onNodeTimeAdjusted(&nodeTimeAdjustedCallback);
  mesh.setRoot(true); // Set this node as root node
  mesh.setContainsRoot(true); // Calls this so that node knows there is a root node
  // 
  /*
  userScheduler.addTask(taskSendMessage);
  taskSendMessage.enable();
  */

}

void loop() {
  mesh.update();
  
}
