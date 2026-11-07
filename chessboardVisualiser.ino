const int S0 = 7;
const int S1 = 8;
const int S2 = 9;
const int S3 = 10;

const int NUM_MUX = 2;
const int SIG_PINS[NUM_MUX] = {A0, A1};
const int NUM_FIELDS = 32;
const int THRESHOLD = 200;

const char* names[NUM_FIELDS] = {
  // MUX 1 (A0): C0-C15 -> kolumny h, g, f, e
  "h1", "h2", "h3", "h4",
  "g1", "g2", "g3", "g4",
  "f1", "f2", "f3", "f4",
  "e1", "e2", "e3", "e4",

  // MUX 2 (A1): C0-C15 -> kolumny d, c, b, a
  "d1", "d2", "d3", "d4",
  "c1", "c2", "c3", "c4",
  "b1", "b2", "b3", "b4",
  "a1", "a2", "a3", "a4"
};

int values[NUM_FIELDS];

void setup() {
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);

  for (int m = 0; m < NUM_MUX; m++) {
    pinMode(SIG_PINS[m], INPUT_PULLUP);
  }

  Serial.begin(115200);
}

void selectChannel(int channel) {
  digitalWrite(S0, channel & 1);
  digitalWrite(S1, (channel >> 1) & 1);
  digitalWrite(S2, (channel >> 2) & 1);
  digitalWrite(S3, (channel >> 3) & 1);
}

void loop() {
  // 1. Odczyt obu multiplekserów dla każdego adresu C0-C15
  for (int channel = 0; channel < 16; channel++) {
    selectChannel(channel);
    delayMicroseconds(500);
    for (int m = 0; m < NUM_MUX; m++) {
      values[m * 16 + channel] = analogRead(SIG_PINS[m]);
    }
  }

  // 2. Wypisanie w układzie szachownicy: rzędy 4 -> 1, kolumny a -> h
  for (int rank = 3; rank >= 0; rank--) {       // rzędy: 4, 3, 2, 1
    for (int file = 7; file >= 0; file--) {     // kolumny: a(7) -> h(0)
      int idx = file * 4 + rank;
      Serial.print(names[idx]);
      Serial.print("=");
      Serial.print(values[idx]);
      Serial.print(values[idx] < THRESHOLD ? "[X] " : "    ");
    }
    Serial.println();
  }
  Serial.println("---");
  delay(100);
}