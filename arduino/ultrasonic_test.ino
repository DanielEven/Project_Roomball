#define SENSOR_CNT 2

const int trigPins[SENSOR_CNT] = {9, 2};
const int echoPins[SENSOR_CNT] = {10, 3};

float duration, distance;

void setup() {
  for (int i = 0; i < SENSOR_CNT; i++) {
    pinMode(trigPins[i], OUTPUT);
    pinMode(echoPins[i], INPUT);
  }
  Serial.begin(9600);
}

void loop() {
  Serial.print("Distances:");
  for (int i = 0; i < SENSOR_CNT; i++) {
    digitalWrite(trigPins[i], LOW);
    delayMicroseconds(2);
    digitalWrite(trigPins[i], HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPins[i], LOW);
    duration = pulseIn(echoPins[i], HIGH);
    distance = (duration*.0343)/2;
    Serial.print(" ");
    Serial.print(distance);
  }
  Serial.println("");
  delay(100);
}