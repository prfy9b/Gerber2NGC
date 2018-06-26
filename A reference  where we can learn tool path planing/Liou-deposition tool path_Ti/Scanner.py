import serial
import string
import time

# **** Basic Settings **** 

# These are in microns:
X_ScanWidth = 10000
Y_ScanWidth = 22000

X_ScanSpacing = 100
Y_ScanSpacing = 100

Feedrate = 500

DepositorSerialDescriptor = "COM5" #CNC NessoBoard
ScannerSerialDescriptor = "COM6" #Scanner

DestinationFileName = "Scan.csv"

OutputFileEolChar = "\n"
OutputFileFieldSeparationChar = ","

# **** Advanced Settings **** 

PrePause = 10
PostPause = 20

DepositorEolChar = "\r"
ScannerEolChar = "\r"

ScannerReadTimeout = 200

ScannerBaud = 9600
DepositorBaud = 9600

DepositorResetChar = "@"
DepositorStartDataChar = "("
DepositorEndDataChar = ")"

# **** Helper Functions ****

def getLineFromScanner():
	# Wait for the scanner to send data
	unformattedScannerResponse = ""
	scannerCharacter = scannerSerial.read()
	while (scannerCharacter != ScannerEolChar):
		unformattedScannerResponse += scannerCharacter
		scannerCharacter = scannerSerial.read()

	# Output from scanner looks like this:
	#   TG,01,XXXXXXX
	# where XXXXXX is the measured value
	# So, separate over the comma character and select the 3rd (index = 2) entry
	commaSeparatedFields = string.split(unformattedScannerResponse, ',')
	return commaSeparatedFields

# **** Program Entry ****

outputFile = open(DestinationFileName, "w")

depositorSerial = serial.Serial(DepositorSerialDescriptor, DepositorBaud)
scannerSerial = serial.Serial(ScannerSerialDescriptor, ScannerBaud, timeout = ScannerReadTimeout)

depositorSerial.write(DepositorResetChar)
raw_input("Go press MANUAL on the CNC. Then, press ENTER here...")
depositorSerial.write(DepositorStartDataChar)
raw_input("Go press START on the CNC. Then, press ENTER here...")

depositorSerial.close()

x = 0
while (x <= X_ScanWidth):
	y = 0

	# This is necessary for some reason. Something is weird with pyserial that means we need a hard reset
	#   every once in a while.
	depositorSerial.open()

	while (y <= Y_ScanWidth):
		# Move the CNC to the correct position
		depositorSerial.write("G1X" + str(x) + "Y" + str(y) + "F" + str(Feedrate) + DepositorEolChar)
		depositorSerial.write("G4P" + str(PrePause) + DepositorEolChar)
		depositorSerial.write("R0L" + DepositorEolChar)
		depositorSerial.write("G4P" + str(PostPause) + DepositorEolChar)

		commaSeparatedFields = getLineFromScanner()
		commaSeparatedFields = getLineFromScanner()

			# The scanner sends two measurement values: one for each OUT channel. Only care about OUT1.
		if commaSeparatedFields[1] == "02":
			# Default value. If this ends up in the output file, it means that this script received a line which it didn't understand.
			z = "????????"

			# Just a sanity check to make sure that the message received from the scanner has three comma-separated values
			if len(commaSeparatedFields) == 3:
				z = commaSeparatedFields[2] # Note: z could be "FFFFFFFF" after this point. "FFFFFFFF" is what the scanner uses when the measurement is out of range

			# This will be a final x,y,z vector where x and y are the xy-coordinates of the measurement in millimeters and z is the measured distance along the z axis (in whatever units the scanner sent)
			formattedDataLine = str(x / 1000.0) + OutputFileFieldSeparationChar + str(y / 1000.0) + OutputFileFieldSeparationChar + str(z) + OutputFileEolChar
		
			# Print to stdout and write to file
			print formattedDataLine
			outputFile.write(formattedDataLine)
		else: print "Error: wrong value received"

		# Increment to next Y position
		y += Y_ScanSpacing

	depositorSerial.close();

	# Increment to next X position
	x += X_ScanSpacing
		
# Clean up
depositorSerial.open()
depositorSerial.write("G1X0Y0Z0F" + str(Feedrate) + DepositorEolChar)
depositorSerial.write(DepositorEndDataChar)
depositorSerial.close()

scannerSerial.close()
outputFile.close();
		