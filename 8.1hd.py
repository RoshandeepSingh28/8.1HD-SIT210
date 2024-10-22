from bluepy.btle import Peripheral, UUID, BTLEException
import RPi.GPIO as GPIO
import time

# MAC address of the Arduino Nano 33 IoT you are trying to connect to
nano_mac_address = "94:b5:55:c0:6c:6e"

# Pin configurations for the LED and Buzzer
LED_PIN = 18    # GPIO pin for controlling the LED
BUZZER_PIN = 23 # GPIO pin for controlling the Buzzer

# Set up GPIO mode to use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# Configure the LED and Buzzer pins as output
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Set up PWM on the LED pin to control brightness (frequency: 100Hz)
pwm_led = GPIO.PWM(LED_PIN, 100)  # PWM frequency 100Hz for LED
pwm_led.start(0)  # Initialize PWM with 0% duty cycle (LED off)

# Function to map distance to LED brightness
# Closer distance = brighter LED (0 to 100 cm -> 0 to 100% brightness)
def map_distance_to_brightness(distance):
    return max(0, min(100, 100 - distance))  # Limit brightness to 0-100%

try:
    # Attempt to connect to the Arduino Nano 33 IoT using its MAC address
    print("Connecting to Arduino Nano 33 IoT...")
    nano = Peripheral(nano_mac_address, addrType="public")  # Specify address type

    # UUIDs for the service and characteristic (must match those on the Arduino side)
    service_uuid = UUID("180C")  # Custom service UUID
    characteristic_uuid = UUID("2A56")  # Custom characteristic UUID

    # Access the custom service and characteristic on the Arduino Nano
    service = nano.getServiceByUUID(service_uuid)
    characteristic = service.getCharacteristics(characteristic_uuid)[0]

    # Main loop: Continuously read distance data and control LED and buzzer accordingly
    while True:
        if characteristic.supportsRead():  # Check if the characteristic supports reading
            try:
                # Read and decode the distance data from the characteristic
                data = characteristic.read().decode('utf-8')
                distance = float(data)  # Convert data to a float value representing the distance
                print(f"Distance from wall: {distance} cm")
            except ValueError:
                # Handle errors in decoding or conversion of the data
                print("Error decoding or converting the distance data.")
                continue  # Skip to the next iteration if there's an error

            # If the distance is less than 60 cm, activate the buzzer and blink the LED
            if distance < 60:
                GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn buzzer on
                for i in range(5):  # Blink LED 5 times
                    pwm_led.ChangeDutyCycle(map_distance_to_brightness(distance))  # Set LED brightness
                    time.sleep(0.2)  # Wait for 0.2 seconds
                    pwm_led.ChangeDutyCycle(0)  # Turn off the LED
                    time.sleep(0.2)  # Wait for 0.2 seconds
            else:
                # If the distance is greater than or equal to 60 cm, turn off the buzzer and LED
                GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn buzzer off
                pwm_led.ChangeDutyCycle(0)  # Ensure the LED is off

            # Adjust LED brightness based on proximity (without blinking)
            if distance < 60:
                brightness = map_distance_to_brightness(distance)  # Map distance to brightness
                pwm_led.ChangeDutyCycle(brightness)  # Set LED brightness based on distance
            else:
                pwm_led.ChangeDutyCycle(0)  # Turn off LED if distance is greater than or equal to 60 cm

            time.sleep(1)  # Wait 1 second before reading the next value

except BTLEException as e:
    # Handle exceptions that occur during the Bluetooth connection
    print(f"Failed to connect to the device: {e}")
finally:
    # Clean up resources before exiting the program
    pwm_led.stop()  # Stop PWM for the LED
    GPIO.cleanup()  # Clean up GPIO settings
    print("GPIO cleanup completed.")
