/* ----------------------------------------------------------------------------
This script receives and parses positional values sent by a Raspberry Pi and
continously matches the position of two stepper motors with said values.

Author:   Michael Siebenmann
Date :    08.09.2018

History:
Version   Date        Who     Changes
1.0       08.09.2018  M7ma    created

Copyright © Michael Siebenmann, Matzingen, Switzerland. All rights reserved
-----------------------------------------------------------------------------*/

#include <Wire.h>
#include <Adafruit_MotorShield.h>

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61);

// Connect two stepper motors with 200 steps per revolution (1.8 degree) to the two ports
Adafruit_StepperMotor *altMotor = AFMS.getStepper(200, 2);
Adafruit_StepperMotor *azMotor = AFMS.getStepper(200, 1);

const byte numChars = 32;
char receivedChars[numChars];
char tempchars[numChars];        // temporary array for use when parsing

// variables to hold the parsed data
char messageFromRPi[numChars] = {0};
float altFromRPi = 0.0;
float azFromRPi = 0.0;

boolean newData = false;

// variables for stepper positions
float altStepper = 0.0;
float azStepper = 0.0;

void setup() {
  Serial.begin(9600);
  Serial.println("Dieses Skript erwartet 3 Inputs: einen Text (String) und zwei Gleitkommazahlen");
  Serial.println("Sendeschema: <Mars, 18.9 , 24.7>  ");
  Serial.println();
  AFMS.begin();             // create with the default frequency 1.6KHz
  //AFMS.begin(1000);       // OR with a different frequency, say 1KHz
  altMotor->setSpeed(25);   // 25 rpm
  azMotor->setSpeed(25);    // 25 rpm
}

void loop() {
  recvWithStartEndMarkers();
  if (newData == true) {
    strcpy(tempchars, receivedChars);
    // this temporary copy is necessary to protect the original data
    //   because strtok() used in parseData() replaces the commas with \0
    parseData();
    showParsedData();
    newData = false;
    float altDiff = altFromRPi - altStepper;
    float azDiff  = azFromRPi  - azStepper;

    int altSteps = getMinimumSteps(altFromRPi, altStepper);
    int azSteps  = getMinimumSteps(azFromRPi, azStepper);

    Serial.print("AltSteps: ");
    Serial.println(altSteps);

    Serial.print("AzSteps: ");
    Serial.println(azSteps);
    
    if (altSteps >= 1) {
      altMotor->step(altSteps, FORWARD, MICROSTEP);
      altStepper += altSteps * 0.6;
    }

    else if (altSteps <= -1) {
      altMotor->step(abs(altSteps), BACKWARD, MICROSTEP);
      altStepper += altSteps * 0.6;
    }

    if (azSteps >= 1) {
      azMotor->step(azSteps, FORWARD, MICROSTEP);
      azStepper += azSteps * 0.6;
    }

    else if (azSteps <= -1) {
      azMotor->step(abs(azSteps), BACKWARD, MICROSTEP);
      azStepper += azSteps * 0.6;
    }
    Serial.print("AltStepper: ");
    Serial.println(altStepper);

    Serial.print("AzStepper: ");
    Serial.println(azStepper);
  }
}

void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else {
        receivedChars[ndx] = '\0';              // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

void parseData() {                              // split the data into its parts
  char * strtokIndx;                            // this is used by strtok() as an index

  strtokIndx = strtok(tempchars, ",");          // get the first part - the string
  strcpy(messageFromRPi, strtokIndx);           // copy it to messageFromRPi

  strtokIndx = strtok(NULL, ",");               // this continues where the previous call left off
  altFromRPi = atof(strtokIndx);                // convert this part to a float
  altFromRPi += 90.0;

  strtokIndx = strtok(NULL, ",");
  azFromRPi = atof(strtokIndx);                 // convert this part to a float

}

void showParsedData() {
  Serial.print("Planet: ");
  Serial.println(messageFromRPi);
  Serial.print("Altitude: ");
  Serial.println(altFromRPi);
  Serial.print("Azimuth: ");
  Serial.println(azFromRPi);
}

int getMinimumSteps(float FromRPi, float Pos) { // Function to optimize the amount of steps to be time efficient and as accurat as possible
  float a = FromRPi - Pos;
  if (a > 180) {
    a = -(360 - a);
  } else if (a < -180) {
    a = 360 + a;
  }

  int b = round(a / 0.6);
  return b;
}

