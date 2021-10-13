/*
  #include <Adafruit_NeoPixel.h>
  #define PINforControl 6 // pin connected to the small NeoPixels strip
  #define NUMPIXELS 8 // number of LEDs on strip
  Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUMPIXELS, PINforControl, NEO_GRB + NEO_KHZ800);
*/

//dotstars
#include <Adafruit_DotStar.h>
#include <SPI.h>
#define NUMPIXELS 144 //temp number
Adafruit_DotStar strip = Adafruit_DotStar(NUMPIXELS, DOTSTAR_BGR); //Royce's strip


const int buttonPin = 2;  //A5 = D19
int buttonState = 0;
int lastButtonState = 1;
long lastDebounceTime = 0;  // the last time the output pin was toggled
long debounceDelay = 10;    // the debounce time; increase if the output flickers

unsigned long lastPatternUpdate = 0; // timestamp of last update to led pattern
uint16_t totalPatternSteps;  // total number of steps in the pattern
uint16_t currentPatternStep;

unsigned long patternUpdateInterval = 30; // milliseconds between updates
unsigned long powerOnSpeed = 25; //lower = faster
unsigned long powerDownSpeed = 30; //lower = faster

uint32_t Color1; // What colors are in use
uint32_t Color2; // What colors are in use
int targetPattern = 0; // which pattern is running

uint32_t red = strip.Color(255, 0, 0);
uint32_t green = strip.Color(0, 255, 0);
uint32_t blue = strip.Color(0, 0, 255);
uint32_t nocolor = strip.Color(0, 0, 0);

long lastPowerOnCompletionCheck = 0;  // the last time the output pin was toggled
long lastPowerDownCompletionCheck = 0;  // the last time the output pin was toggled

#define S_IDLE 1
#define S_FADEIN 2
#define S_FADEOUT 3
static int state = S_IDLE;

bool doFadeOut = false;
bool doFadeIn = false;

void setup() {
  //debug (monitor)
  Serial.begin(115200);

  //neopixel strip setup  (doesnt seem work to reset leds to 'off'
  Serial.println(F("turn all leds off")); //read current volume
  strip.begin(); // Initialize pins for output
  strip.show(); //reset all leds to off
  clearall();

  pinMode(buttonPin, INPUT);
  digitalWrite(buttonPin, HIGH);

  //Color1 = Wheel(random(255)); // What colors are in use
  //Color2 = Wheel(random(255)); // What colors are in use

}

void loop() {
  switch (state) {

    case S_IDLE:
      buttonState = digitalRead(buttonPin);
      if ((buttonState != lastButtonState) && (millis() - lastDebounceTime > debounceDelay)) {
        lastDebounceTime = millis(); //update last time pressed/released
              
        if (buttonState == LOW) {
          state = S_FADEIN;
        } else {
          state = S_FADEOUT;
        }

      }else {
        //no button state change, but still being pressed/held low
        if (buttonState == LOW) {
          //continue updating pattern if button is still pressed.
          if (millis() - lastPatternUpdate > patternUpdateInterval && doFadeIn == true) {
            updatePattern(targetPattern);
          }

        }else {
          //update led pattern/animation
          if (millis() - lastPatternUpdate > patternUpdateInterval && doFadeOut == true) {
            updatePattern(targetPattern);
          }
        }
      }
      lastButtonState = buttonState;
      break;
      

    case S_FADEIN:
      Serial.println(F("[FADE IN]"));
      doFadeIn = true;
      
      //set colors for fade in pattern/animation
      Color1 = strip.getPixelColor(0); //get current color to fade from
      Color2 = red; 

      //update led pattern variables      
      totalPatternSteps = 8;
      currentPatternStep = 0;
      targetPattern = 0;
      patternUpdateInterval = powerOnSpeed;
      updatePattern(targetPattern);

      //update timestamp
      lastPowerOnCompletionCheck = millis(); //update last time checked for file completion

      //return to button checking (idle state)
      state = S_IDLE;
      break;
      
    
    case S_FADEOUT:
      Serial.println(F("[FADE OUT]"));
      doFadeOut = true;
      
      //set colors for fade in pattern/animation
      Color2 = strip.getPixelColor(0); //get current color to fade from
      Color1 = nocolor;

      //update led pattern variables
      totalPatternSteps = 22;
      currentPatternStep = totalPatternSteps;
      targetPattern = 2;
      patternUpdateInterval = powerDownSpeed;
      updatePattern(targetPattern);

      //update timestamp
      lastPowerDownCompletionCheck = millis(); //update last time checked for file completion

      //return to button checking (idle state)
      state = S_IDLE;
      break;
  }

}

//--[neopixel pattern code]--//
void  updatePattern(int newPattern) {
  switch (newPattern) {
    case 0:
      FadeIn();
      //FadeUpdate(); //new addition from tutorial (function only?)
      //setColor(red);
      break;
    case 1:      
      //FadeOut();
      //FadeUpdate();
      setColor(blue);
      break;
    case 2:
      FadeOut();
      //FadeUpdate();
      //setColor(green);
      break;
    case 3:
      setColor(red);
      break;
  }
}

void clearall() {
  for (int i = 0; i < NUMPIXELS; i++) {
    strip.setPixelColor(i, strip.Color(0, 0, 0));
  }
  strip.show();
  //Serial.println(F("--should be all cleared--"));
}

void setColor(uint32_t targetColor) {
  for (int i = 0; i < NUMPIXELS; i++) {
    if (i < 12) {
      strip.setPixelColor(i, targetColor);
    } else {
      strip.setPixelColor(i, 0, 0, 0);
    }
  }
  strip.show();
  lastPatternUpdate = millis();  //update pattern time stamp
}


//update the fade pattern - - //the equation of what does the tweening/easing
void FadeIn() {
  //Serial.println(F("Fade pattern update....."));
  uint8_t red = ((Red(Color1) * (totalPatternSteps - currentPatternStep)) + (Red(Color2) * currentPatternStep)) / totalPatternSteps;
  uint8_t green = ((Green(Color1) * (totalPatternSteps - currentPatternStep)) + (Green(Color2) * currentPatternStep)) / totalPatternSteps;
  uint8_t blue = ((Blue(Color1) * (totalPatternSteps - currentPatternStep)) + (Blue(Color2) * currentPatternStep)) / totalPatternSteps;
  ColorSet(strip.Color(red, green, blue));
  strip.show(); //-there is a call in ColorSet() function to show() ...why here as well?
  
  Serial.print(F("fading in: -------->>  "));
  Serial.println(currentPatternStep);    
  currentPatternStep++;
  
  if (currentPatternStep >= totalPatternSteps) {
    currentPatternStep = 0;
    doFadeIn = false;
    Serial.println(F("[---fade in pattern is complete---]"));       
  }
  
  lastPatternUpdate = millis();  //update pattern time stamp
}

void FadeOut() {
  //Serial.println(F("Fade pattern update....."));
  uint8_t red = ((Red(Color1) * (totalPatternSteps - currentPatternStep)) + (Red(Color2) * currentPatternStep)) / totalPatternSteps;
  uint8_t green = ((Green(Color1) * (totalPatternSteps - currentPatternStep)) + (Green(Color2) * currentPatternStep)) / totalPatternSteps;
  uint8_t blue = ((Blue(Color1) * (totalPatternSteps - currentPatternStep)) + (Blue(Color2) * currentPatternStep)) / totalPatternSteps;
  ColorSet(strip.Color(red, green, blue));
  strip.show(); //-there is a call in ColorSet() function to show() ...why here as well?
    
  Serial.print(F("fading out: -------->>  "));
  Serial.println(currentPatternStep);    
  
  if (currentPatternStep <= totalPatternSteps) {
    if(currentPatternStep <= 0){    
      doFadeOut = false;
      currentPatternStep = 0;
      Serial.println(F("[---fade out pattern is complete---]"));      
    }
  }
  --currentPatternStep;   
  
  lastPatternUpdate = millis();  //update pattern time stamp
}

// Returns the Red component of a 32-bit color
uint8_t Red(uint32_t color) {
  return (color >> 16) & 0xFF;
}

// Returns the Green component of a 32-bit color
uint8_t Green(uint32_t color) {
  return (color >> 8) & 0xFF;
}

// Returns the Blue component of a 32-bit color
uint8_t Blue(uint32_t color) {
  return color & 0xFF;
}

// Set all pixels to a color (synchronously)
void ColorSet(uint32_t color) {
  //Serial.println(F("Setting color....")); 
  for (int i = 0; i < NUMPIXELS; i++) {
    if (i < 12) {
      strip.setPixelColor(i, color);
    } else {
      strip.setPixelColor(i, 0, 0, 0);
    }
  }
  strip.show();
  lastPatternUpdate = millis();  //update pattern time stamp   
}
