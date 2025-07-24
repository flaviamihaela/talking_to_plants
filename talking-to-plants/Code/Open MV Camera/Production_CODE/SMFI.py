# Code Integration

# Library/Module imports
import sensor, image, pyb, os, time, math
from pyb import UART
from array import array
from pyb import DAC
from pyb import Timer

# User defined parametters
DAC_startvalue=3095 #4095 - 0, 3095
Lookuptable_active=0 #0 or 1 => 1 to activate oscillation
DC_offset = 2480 #3500 - 600 = 2900
#Amplitude = 60 # 4095-DC_offset-200-700-700 = -405
#Frequency = [1,0.5,0.1]

PeriodTable = [60,2,1]
Period= 10 #works within 1 to 10
Num_per_wave=100
capture_delay= Period/Num_per_wave
buffersize=1024
flag = True
packetSize = 3000
headerSize = 5
TotalSteps = 1

# Lookup table parameters
startingValue = 2800              # Reference Card: startingValue = 2400, endValue = 3000
endValue = 3300                   # Plant: startingValue = 2800, endValue = 3300
increment = 1
intensityA = 30                   # Reference Card: Amplitude = 0.85, Offset = 3.67
intensityOffset = 39              # Plant: Amplitude = 30, Offset = 39

flagHigh = 0
flagLow = 0

def GreenBlink(duration):
    green_led.on()
    time.sleep(duration)
    green_led.off()

def sendEndPacket():
    uart.write('\r'.encode()) # string end null character
    uart.write('\n'.encode()) # string end null character
    uart.write('\r'.encode()) # string end null character
    uart.write('\n'.encode()) # string end null character

def CRC32_Table(bytes, n):
    # Define constants
    POLYNOMIAL = 0x04C11DB7  # Divisor is 32-bit
    TABLE_SIZE = 256

    # Initialize lookup table
    TABLE_EV = bytearray(TABLE_SIZE*4)  # Allocate 256 * 4 bytes for lookup table
    __TABLE_INIT = False

    # Compute lookup table if not initialized
    if __TABLE_INIT:
        pass  # Follow lookup
    else:
        # Initialize all tables
        for j in range(TABLE_SIZE):
            b = j
            crc = 0
            crc ^= (b << 24)  # Move byte into MSB of 32-bit CRC
            for k in range(8):
                if (crc & 0x80000000) != 0:  # Test for MSB = bit 31
                    crc = ((crc << 1) ^ POLYNOMIAL) & 0xffffffff
                else:
                    crc <<= 1
            # Now add value to table
            TABLE_EV[j*4:j*4+4] = crc.to_bytes(4, 'little')
        __TABLE_INIT = True

    # Start CRC32 calculations
    crc = 0xffffffff  # CRC value is 32-bit

    for j in range(n):
        b = bytes[j]
        b = reverse(b)
        bk = b
        b = b ^ ((crc >> 24) & 0x0ff)
        crc = (crc << 8) ^ int.from_bytes(TABLE_EV[b*4:b*4+4], 'little')

    crc = crc ^ 0xffffffff

    # Reverse complete 32-bit word bit by bit
    crc = (
        reverse((crc & 0xff000000) >> 24) +
        (reverse((crc & 0x00ff0000) >> 16) << 8) +
        (reverse((crc & 0x0000ff00) >> 8) << 16) +
        (reverse((crc & 0x000000ff)) << 24)
    )

    return crc

def rev(s):
    r = ""
    for c in s:
        r = c+r

    return r

def reverse(b):
    binary_str = bin(b)[2:]  # Remove '0b' prefix from binary string
    padded_str = '0' * (8 - len(binary_str)) + binary_str  # Pad with zeros
    reversed_str = rev(padded_str)  # Reverse the string
    return int(reversed_str, 2)

# Status LED Setup
red_led = pyb.LED(1)    #Setup Red LED
green_led = pyb.LED(2)  #Setup Green LED

red_led.on()            #LED RED durring setup

# UART Setup
uart = UART(1, 115200) #Bus ,  baudrate
uart.init(115200, bits = 8, parity = 0, stop = 1, timeout=1000)
#time.sleep_ms(3000) #More delay
imageCount = 0
freqCount = 0
runNum = 0
# Botton Setup
button = pyb.Pin("P2", pyb.Pin.IN, pyb.Pin.PULL_DOWN)
pressed = 1 # If PULL_Down=1 if PULL_UP=0

# Sleep condition
sleepFlag = False

dac = DAC(2,bits=12)
dac.write(DAC_startvalue)

## TO DO WITH INTENSITY SETUP
columns = 2
rows = int((endValue - startingValue) / increment) + 1

lookupTable = [[0] * columns for _ in range(rows)]
intensityArray = [[0] * 1 for _ in range(1024)]
outputValues = [[0] * 1 for _ in range(1024)]
buf = bytearray(1024)

for i in range(rows):
    # Calculate DAC Values and corresponding intensity values with below equation, then fill look-up table
    DACValue = startingValue + increment * i

    # y = 0.000000110910x^3 - 0.000821821692x^2 + 2.037508154827x - 1,688.974974291580
    intensity = 0.000000110910*DACValue**3 - 0.000821821692*DACValue**2 + 2.037508154827*DACValue - 1688.974974291580
    intensity = round(intensity, 2)

    lookupTable[i][0] = DACValue
    lookupTable[i][1] = intensity

    print(str(DACValue) + ", " + str(intensity))

# Look-up table has now been formed so start sine wave and find appropriate outputs
for i in range(1024):
    intensity = intensityOffset + intensityA * math.sin(2 * math.pi * i / 1024)
    intensityArray[i] = intensity
    #print(intensity)

smallestDifference = intensityArray[1]
index = 0

for i in range(1024):
    desiredIntensity = intensityArray[i]
    start = index

    if ((desiredIntensity - intensityArray[i-1] > 0 ) and i != 0):
        end = rows
        step = 1

    elif ((desiredIntensity - intensityArray[i-1] < 0 ) and i != 0):
        end = 0
        step = -1

    elif ((desiredIntensity - intensityArray[i-1] == 0 ) or i == 0):
        end = rows
        step = 1

    previousDifference = 100

    for n in range(start, end, step):
        difference = abs(desiredIntensity - lookupTable[n][1])

        if (previousDifference < difference):
            break

        if difference < smallestDifference:
            smallestDifference = difference
            index = n

        previousDifference = difference

    #print(index - start)

    smallestDifference = 100

    output = lookupTable[index][0]
    outputValues[i] = output

    if (output > endValue):
        flagHigh = 1
    elif (output < startingValue):
        flagLow = 1

    print(output)

# Global shutter camera setup and confugurations
sensor.reset() # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA) # Set frame size to QVGA (320x240)
sensor.set_auto_gain(False,10)
sensor.set_auto_exposure(False, exposure_us=150000) # make smaller to go faster
sensor.set_windowing((120, 120)) #!!!Make sure to include this line!!! (windowing is not optional but might be scalable)
sensor.skip_frames(time = 2000) # Wait for settings take effect.

red_led.off()
GreenBlink(0.2)

print("Ready to capture")

#Image capture function

while(True):
    #print(button.value())
    if (button.value()== pressed or sleepFlag == True): # button.value=1 when button pressed
        sleepFlag = False
        # Reset sleepFlag
        # for loop => take every 2 sec
        runNum += 1
        print("Capture Started")
        freqCount = 0
        while freqCount <3:
            # Update Period
            
            #Period = int(1/Frequency[freqCount])
            Period = PeriodTable[freqCount]
            print(Period)
            # Update dac
            dac = DAC(2,bits=12)
            #dac.write(DAC_startvalue)
            #dac.write(DC_offset)
            dac.write(outputValues[0])

            steps = 1

            capture_delay= int(Period/Num_per_wave*1000)

            buf = array('H', outputValues)

            for i in range(1024):
                print(str(intensityArray[i]) + ", " + str(buf[i]) + ", " + str(outputValues[i]))

            if (flagHigh):
                print("Out of range - High")
            elif (flagLow):
                print("Out of range - Low")

            dac.write_timed(buf, len(buf)//Period, mode=DAC.CIRCULAR)

            while steps < TotalSteps:

                print("Step: " + str(steps))

                time.sleep_ms(capture_delay*Num_per_wave)
                steps += 1
            # Update delay time

            print(capture_delay)

            imageCount = 0
            # Get 1st image & Generate mask for the other x images
            img = sensor.snapshot()
            cpy= img.copy()
            cpy2= img.copy()
            cpy.gaussian(3, unsharp=True, threshold=False)
            cpy.laplacian(3, sharpen=True, threshold=True)
            cpy.invert()
            cpy.dilate(1, threshold=6)
            cpy.erode(1, threshold=7)
            cpy2.clear(cpy)
            th=cpy2.get_histogram().get_threshold()
            th_int= th.value()
            thresholdNG = [(0, th_int)]
            b=img.binary(thresholdNG,to_bitmap=True, copy=True)
            img.clear(b).to_grayscale
            img.save("%d.jpg"%(imageCount), quality = 80) # Store image under the name "0.jpg"
            print("Capture Success")
            imageCount +=1
            # Wait x sec
            
            #dac.write(DC_offset)

            time.sleep_ms(capture_delay)

            print("Capture Start")
            while imageCount < Num_per_wave:

                #dac.write(outputValues[imageCount])
                #print(outputValues[imageCount])
                time.sleep_ms(capture_delay)
                img = sensor.snapshot()     # Capture image

                # Mask is reused here
                img.clear(b).to_grayscale
                # Segmentation End
                img.save("%d.jpg"%(imageCount), quality = 80) # Store image under the name "0.jpg"
                #print("Capture Sucess")
                print("Image No. " + str(imageCount) + " captured")
                imageCount +=1

            # Done Images
            # Turn off LED
            print("Capture Done")
            dac.write(0)
            dac.deinit()
            #time.sleep_ms(2000)

            #for loop sending all images
            for u in range(imageCount):
                img = image.Image("%d.jpg"%(u), copy_to_fb = True)


                x = img.size()
                print(x)
                count = 0
                segmentCount = 0;
                # Sends img in segments of
                totalSegmentCount = math.floor(x/packetSize)+1
                print("totalSegmentCount")
                print(totalSegmentCount)
                for i in range (x):
                    """
                    elif count > 64:
                        print("Done Packet ",(segmentCount-1))
                        count = 0
                        time.sleep_ms(1000)
                    """
                    if count == 0:
                        # Send packet header
                        uart.write('\r'.encode()) #packet start
                        uart.writechar(u+1) #image number
                        uart.writechar(segmentCount+1) # segment count
                        uart.writechar(totalSegmentCount) #total segment count
                        uart.writechar(Period) #current period
                        uart.writechar(runNum)
                        uart.writechar(img[i])
                        time.sleep_ms(5)
                        # Get crc

                        # Form arr =>
                        arr = []
                        summ = packetSize+i
                        if summ >= x:
                            summ = x
                        for j in range (i,summ):
                            arr.append(img[j])
                        crc = CRC32_Table(arr,len(arr))
                        print(hex(crc))

                    elif count%128 == 0:
                        # Send 128th byte and stop
                        uart.writechar(img[i])
                        print("Done Packet ",(segmentCount),"  ",(u))
                        time.sleep_ms(50) # Pause a bit

                    elif i == x-1 or count==packetSize-1:
                        print("done")

                        uart.writechar(img[i])

                        print("Done")
                        sendEndPacket()
                        # Wait for next uart signal (notified by '\r')
                        count = -1
                        segmentCount +=1

                        while True:
                            if (uart.any()):
                                print("yes")
                                temp = uart.read(3)
                                if (temp == b'bes'):
                                    print("correct")
                                    time.sleep_ms(1000)
                                    break
                                elif (temp==b'yes'):
                                    print("correct Final")
                                    time.sleep_ms(1000)
                                    # Only update if freq count is last
                                    if (freqCount ==2 and segmentCount == totalSegmentCount):
                                        PeriodTable[0]= int.from_bytes(uart.read(1), 'big', False)
                                        PeriodTable[1]= int.from_bytes(uart.read(1), 'big', False)
                                        PeriodTable[2]= int.from_bytes(uart.read(1), 'big', False)

                                        #PeriodTable[1] = uart.read(1)
                                        #PeriodTable[2] = uart.read(1)
                                        for k in range(3):
                                            print(PeriodTable[k])
                                        Num_per_wave = int.from_bytes(uart.read(1), 'big', False)
                                        print(Num_per_wave)
                                        buffer = [None]*4
                                        for k in range(4):
                                            buffer[k] = int.from_bytes(uart.read(1), 'big', False)
                                        # Recombine the bytes into a 32-bit integer
                                        timeDiff = (buffer[0] << 24) | (buffer[1] << 16) | (buffer[2] << 8) | buffer[3]

                                        print(timeDiff)  # Output: timeDIff
                                    else:
                                        # Dump the 4 bytes
                                        dump = int.from_bytes(uart.read(8), 'big', False)
                                    break
                    else:
                        uart.writechar(img[i])

                    count +=1
                    # End of for => done one byte

                # End of for done 1 image
                print("End of UART Transmission")
                print("ImageCount = " )
                print(u)
                print("segmentCount = ")
                print(segmentCount)
                '''
                #wait for uart signal
                while True:
                    if (uart.any()):
                        print("yes")
                        if (uart.read()=="yes"):
                            print("yes")
                            break

                '''
            freqCount +=1
            print(freqCount)
        # Sleep for x and turn on sleep flag
        dac.write(0)
        dac.deinit()
        time.sleep_ms(timeDiff*1000)
        sleepFlag = True
