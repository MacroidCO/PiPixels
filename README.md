# PiPixels is my playground to experiment with using a Rasberry Pi to trick-out my holiday lights.

See https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel

and https://github.com/jgarff/rpi_ws281x

uint16_t brightness;
void loop()
{
   brightness = 255;
   strip.setPixelColor(n, (brightness*255/255) , (brightness*0/255), (brightness*100/255));
   strip.show();
   delay(1000);
   brightness = 50;
   strip.setPixelColor(n, (brightness*255/255) , (brightness*0/255), (brightness*100/255));
   strip.show();
   delay(1000);
}

from https://forums.adafruit.com/viewtopic.php?t=41143

