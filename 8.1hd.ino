#include <ArduinoBLE.h>

BLEService customService("180C");                                               // Custom service UUID
BLEStringCharacteristic customCharacteristic("2A56", BLERead | BLENotify, 20);  // Characteristic to send data
// Define pins for the ultrasonic sensor
const int trigPin = 9;
const int echoPin = 10;

// Variable to store the duration and distance
long duration;
int distance;

void setup() {
  Serial.begin(9600);
    pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  BLE.begin();
  // Initialize BLE
  if (!BLE.begin()) {
    Serial.println("Failed to initialize BLE!");
    while (1);
  }

  // Set local name and advertise the service
  BLE.setLocalName("Nano33IoT");
  BLE.setAdvertisedService(customService);

  // Add the characteristic to the service
  customService.addCharacteristic(customCharacteristic);

  // Add the service
  BLE.addService(customService);

  // Start advertising
  BLE.advertise();

  Serial.println("BLE device active, waiting for connection...");
}


void loop() {
  // Wait for a BLE central to connect
  BLEDevice central = BLE.central();
  
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      // Send data to the central device
      digitalWrite(trigPin, LOW);
      delayMicroseconds(2);

      // Trigger the sensor by setting the trigPin HIGH for 10 microseconds
      digitalWrite(trigPin, HIGH);
      delayMicroseconds(10);
      digitalWrite(trigPin, LOW);

      // Read the echoPin to get the duration of the pulse
      duration = pulseIn(echoPin, HIGH);

      // Calculate the distance in centimeters
      distance = duration * 0.034 / 2;

     
        String distanceStr = String(distance);
        customCharacteristic.writeValue(distanceStr);
        Serial.println("Sent distance: " + distanceStr + " cm");
      // Print the distance to the serial monitor
      Serial.print("Distance: ");
      Serial.print(distance);
      Serial.println(" cm");

      delay(1000);  // Send data every second
    }

    Serial.println("Disconnected from central");
  }
}
