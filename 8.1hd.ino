#include <ArduinoBLE.h>
#include <Wire.h>
#include <BH1750.h>

BLEService customService("180C");                                               // Custom service UUID
BLEStringCharacteristic customCharacteristic("2A56", BLERead | BLENotify, 20);  // Characteristic to send data
BH1750 lightSensor(0x23);

unsigned long lastMeasurementTime = 0;           // To manage measurement timing
const unsigned long measurementInterval = 1000;  // Measurement interval in milliseconds

void setup() {
  Serial.begin(9600);

  // Initialize the light sensor
  Wire.begin();
  lightSensor.begin();

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
      if (millis() - lastMeasurementTime >= measurementInterval) {
        lastMeasurementTime = millis();  // Update the last measurement time

        // Read light level
        float lux = lightSensor.readLightLevel();

        // Check if reading was successful
        if (lux >= 0) {
          Serial.print("Light Intensity: ");
          Serial.print(lux);
          Serial.println(" lx");

          // Convert the light intensity (lux) to a String for BLE
          String luxString = String((int)lux); // Convert lux to String

          // Send the light intensity over BLE
          customCharacteristic.writeValue(luxString);
        } else {
          Serial.println("Failed to read light level.");
        }
      }

      BLE.poll();
    }

    Serial.println("Disconnected from central");
  }

  BLE.poll();
}
