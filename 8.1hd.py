from bluepy.btle import Peripheral, UUID, BTLEException
import RPi.GPIO as GPIO
import time

# Connect to the Arduino Nano 33 IoT by specifying its MAC address
nano_mac_address = "94:b5:55:c0:6c:6e"
LED_PIN = 18    # LED pin
BUZZER_PIN = 23 # Buzzer pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# PWM setup for LED brightness
pwm_led = GPIO.PWM(LED_PIN, 100)  # PWM frequency 100Hz for LED
pwm_led.start(0)

# Function to map distance to LED brightness (0 to 100 cm -> 0 to 100% brightness)
def map_distance_to_brightness(distance):
    return max(0, min(100, 100 - distance))  # Closer distance = brighter LED

try:
    # Specify address type 'random' or 'public' depending on the scan result
    print("Connecting to Arduino Nano 33 IoT...")
    nano = Peripheral(nano_mac_address, addrType="public")  # Try 'public' if 'random' fails

    # UUIDs for the custom service and characteristic (must match those on the Arduino side)
    service_uuid = UUID("180C")
    characteristic_uuid = UUID("2A56")

    # Get the custom service and characteristic
    service = nano.getServiceByUUID(service_uuid)
    characteristic = service.getCharacteristics(characteristic_uuid)[0]

    while True:
        if characteristic.supportsRead():
            try:
                data = characteristic.read().decode('utf-8')
                distance = float(data)
                print(f"Distance from wall: {distance} cm")
            except ValueError:
                print("Error decoding or converting the distance data.")
                continue  # Skip to the next loop iteration

            if distance < 60:
                GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn buzzer on
                for i in range(5):  # Blink LED 5 times
                    pwm_led.ChangeDutyCycle(map_distance_to_brightness(distance))
                    time.sleep(0.2)
                    pwm_led.ChangeDutyCycle(0)  # Turn off LED
                    time.sleep(0.2)
            else:
                GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn buzzer off
                pwm_led.ChangeDutyCycle(0)  # Ensure LED is off

            # Adjust LED brightness based on proximity (if not blinking)
            if distance < 60:
                brightness = map_distance_to_brightness(distance)
                pwm_led.ChangeDutyCycle(brightness)
                #print(f"LED Brightness: {brightness}%")
            else:
                pwm_led.ChangeDutyCycle(0)  # Turn off LED if distance >= 100 cm

            time.sleep(1)

except BTLEException as e:
    print(f"Failed to connect to the device: {e}")
finally:
    # Clean up resources
    pwm_led.stop()
    GPIO.cleanup()
    print("GPIO cleanup completed.")

