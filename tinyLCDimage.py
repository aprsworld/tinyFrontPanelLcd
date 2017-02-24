import Adafruit_SSD1306
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Raspberry Pi pin configuration:
RST = 24

def dispLogo(message,imageFile):

	# 128x32 display with hardware I2C:
	disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

	# Initialize library.
	disp.begin()

	# Clear display.
	disp.clear()
	disp.display()

	# Load PPM
	image = Image.open(imageFile).convert('1')

	draw = ImageDraw.Draw(image)
	font = ImageFont.load_default()

	draw.text((0, 2 + 20), message, font=font, fill=255)

	# Display image.
	disp.image(image.rotate(180))
	disp.display()

if __name__ == '__main__':
	message='Please wait...'
	image='res/images/dash.ppm'

	# first (optional) argument is message to put below image 
	if len(sys.argv) >= 2:
		message=sys.argv[1]
	# second (optional) argument is the image
	if len(sys.argv) >= 3:
		image=sys.argv[2]


	dispLogo(message,image);


