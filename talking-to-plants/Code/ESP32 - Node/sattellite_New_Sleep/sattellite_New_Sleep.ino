// Gateway root
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
#include "painlessmesh/protocol.hpp"
#include <iostream>
#include <vector>

HardwareSerial SerialPort(2); // Use UART2

// WiFi Credentials
#define   MESH_PREFIX     "whateverYouLike"
#define   MESH_PASSWORD   "somethingSneaky"
#define   MESH_PORT       5555

// Variables

SimpleList<uint32_t> nodes;
char buff[7000];
char msg[7000];
int bufferPoint = 0;
bool flag2 = true;
bool start = false;
uint8_t imageNum = 0;
uint8_t segmentNum = 0;
uint8_t totalSegmentNum = 0;
uint8_t runNum = 1;
uint8_t mode = 0;
// Tables arrays for lookup fast
static bool __TABLE_INIT= false;
static unsigned int TABLE_EV[256];

uint32_t root = 2127224661;
int numNodes = 0;
int nodeList[100];
StaticJsonDocument<1024> doc;
Scheduler userScheduler; // To control your personal task
painlessMesh  mesh;

unsigned char reverse(unsigned char b) {
   b = (b & 0xF0) >> 4 | (b & 0x0F) << 4;
   b = (b & 0xCC) >> 2 | (b & 0x33) << 2;
   b = (b & 0xAA) >> 1 | (b & 0x55) << 1;
   return b;
}

/*
namespace protocol {
  struct NodeTree {
    size_t nodeId;
    bool root;
    std::vector<NodeTree> subs;
  };
}

uint32_t getRootId(const protocol::NodeTree& nodeTree) {
  if (nodeTree.root) return nodeTree.nodeId;
  for (const auto& sub : nodeTree.subs) {
    auto id = getRootId(sub);
    if (id != 0) return id;
  }
  return 0;
}
*/

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

void sendMessage(); 

// Routine service
//Task taskSendMessage( TASK_SECOND * 10 , TASK_FOREVER, &sendMessage );

void sendMessage(){
  // Can be used to add functionality
  // Generate msg
  // Read buffer to update ID number & segment number
  start = false;
  imageNum = buff[0];
  segmentNum = buff[1];
  totalSegmentNum = buff[2];
  mode = buff[3];

  //strncpy(msg, buff, bufferPoint); // copy first ith elements from buff into msg

  // Set msg to be null terminator
  
  msg[0] = 0;
  // Start from 4th index => 1&2 are image number , 3&4 are segment number
  //sprintf(msg+strlen(msg),"0x");
  

  for (int i = 0; i < bufferPoint; i++){
    sprintf(msg + strlen(msg), "%02.2X", buff[i]);
    //char str[2] = {buff[i], '\0'}; // Convert current character in buff to a null-terminated string
    //strcat(msg, str); // Append the string to msg
  }
  
  //Serial.println(bufferPoint);
  //buff[bufferPoint] = '\0';
  bufferPoint = 0;
  Serial.println(imageNum);
  Serial.println(segmentNum);
  Serial.println(totalSegmentNum);
  Serial.println(mode);
  Serial.println(msg);
  //Serial.println(strlen(buff));
  mesh.sendSingle(root, msg);
  Serial.println("Sent message");
  
};


void receivedCallback( uint32_t from, String &msg ) {
  // Receiving signal from Root that it is completed
  Serial.println(msg);
  if (msg =="root"){
    root = from;   
    Serial.println("New Root is");
    Serial.println(root); 
  }
  else if (msg=="done"){
    Serial.println("Done 1 part");
    SerialPort.write("bes");
  }
  else{
    // Send through UART that it is ready for next
    SerialPort.write("yes");
    Serial.println("Back Propagate Successful");
    // Read message & send it through UART
    for (int g = 0 ; g<msg.length() ; g+=2){
      // get char value from Hex string
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
        delay(5) ; // delay 0.005s every 128 bytes
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
  Serial.println("stuff");
  //root = getRootId(mesh.asNodeTree());

  //Get root

  Serial.println(root);
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
  //mesh.setRoot(true); // Set this node as root node
  mesh.setContainsRoot(true); // Calls this so that node knows there is a root node
  // 
  //userScheduler.addTask(taskSendMessage);
  //taskSendMessage.enable();
}

void loop() {
  mesh.update();
  // Upon receiving bytes from UART
  /*
  if (SerialPort.available()){
    char inByte = SerialPort.read();
    // carriage return character (\r) 
    if (inByte == '\r'){
      // start of sending
      bufferPoint = 0;
    }
    // newline character (\n) 
    else if (inByte == '\n'){
      // End of sending packet send message funciton
      sendMessage();
    }
    else if (inByte == '\0'){
      // End of message packet
      sendMessage();
    }
    else{
      // Fill up buffer if not
      buff[bufferPoint] = inByte;
      bufferPoint +=1;
    }
  }
  */ 
  // Receive UART

  // Checking UART
  if (flag2){
    Serial.println("checking UART");
    flag2= false;
  }
  
  if (SerialPort.available()){
    
    uint8_t inByte = SerialPort.read();
    //Serial.println(inByte);
    
    // Carriage return character (\r) 
    if (inByte == '\r'&& start == false){
      // Start of sending
      Serial.println("start");
      bufferPoint = 0;
      start = true;
    }
    else if (inByte == '\r' && start==true){
      // End of sending packet send message funciton
      // Check next 2 bytes for '\r'
      Serial.println("Checking");
      //Serial.println(inByte);
      /*
      uint8_t inByte2 = SerialPort.read();
      Serial.println(inByte2);
      uint8_t inByte3 = SerialPort.read();
      Serial.println(inByte3);
      uint8_t inByte4 = SerialPort.read();
      Serial.println(inByte4);
      */
      //uint8_t inByte3 = SerialPort.read();
      //delay(100);

      // Can also try while buffer is empty

      // Check byte 2
      while (!SerialPort.available()){
      }
      uint8_t inByte2 = SerialPort.read();
      //Serial.println(inByte2);
      // Check byte 3
      while (!SerialPort.available()){
      }
      uint8_t inByte3 = SerialPort.read();
      //Serial.println(inByte3);

      // Check byte 4
      while (!SerialPort.available()){
      }
      uint8_t inByte4 = SerialPort.read();
      //Serial.println(inByte4);

      if (inByte2 == '\n' && inByte3 == '\r' && inByte4 == '\n'){
        Serial.println("Done Segment");
        sendMessage();          
      }
      else{
        // Save all 4 bytes into buffer and move forward
        char charByte = (char)inByte;
        buff[bufferPoint] = charByte;
        bufferPoint+=1;
        char charByte2 = (char)inByte2;
        buff[bufferPoint] = charByte2;
        bufferPoint+=1;
        char charByte3 = (char)inByte3;
        buff[bufferPoint] = charByte3;
        bufferPoint+=1;
        char charByte4 = (char)inByte4;
        buff[bufferPoint] = charByte4;
        bufferPoint+=1;
      }
    }
    /*
    else if (inByte == '\0' && start==true){
      // End of message packet
      Serial.println("Done image");
      sendMessage();
    }
    */
    else if (start){
      // Only start if received "\r in buffer"
      // Fill up buffer if not
      // Cast uint8_t to char => openMV sends it as uint8_t
      char charByte = (char)inByte;
      //Serial.println(charByte);
      buff[bufferPoint] = charByte;
      bufferPoint +=1;
    }
  }
}
