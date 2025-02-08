// ---------------------------------
// GPS ADAFRUIT MY VERSION
// ---------------------------------

// Librerías
#include <Adafruit_GPS.h>
#include <HardwareSerial.h>

// Pines GPS
#define RXPIN 16
#define TXPIN 17

// Inicializar comunicación serie para GPS
HardwareSerial mySerial(1);  // UART1 para Raspberry Pi Pico
Adafruit_GPS GPS(&mySerial);

// Constantes
const unsigned long intervaloGPS = 1000; // Intervalo para enviar datos GPS
const int pinLoRa = 5;

// Variables globales
unsigned long tiempoAnteriorGPS = 0;

void setup() {
    // Configurar comunicación serie para depuración
    Serial.begin(115200);
    while (!Serial);

    // Configurar puerto serie del GPS
    mySerial.begin(9600, SERIAL_8N1, RXPIN, TXPIN);

    // Configurar GPS
    GPS.begin(9600);
    GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA); // Salida NMEA con GPRMC y GPGGA
    GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);    // Actualización de 1 Hz

    // Inicializar estado
    Serial.println("Inicialización completa.");
}

void loop() {
    // Leer datos GPS
    while (mySerial.available()) {
        char c = GPS.read();
    }

    // Procesar nueva cadena NMEA
    if (GPS.newNMEAreceived() && GPS.parse(GPS.lastNMEA())) {
        unsigned long tiempoActual = millis();
        if (tiempoActual - tiempoAnteriorGPS >= intervaloGPS) {
            tiempoAnteriorGPS = tiempoActual;
            imprimirDatosGPS();
        }
    }
}

void imprimirDatosGPS() {
    if (GPS.fix) {
        Serial.print("Latitud: "); Serial.println(GPS.latitude, 4);
        Serial.print("Longitud: "); Serial.println(GPS.longitude, 4);
        Serial.print("Altitud: "); Serial.println(GPS.altitude);
        Serial.print("Satélites: "); Serial.println(GPS.satellites);
        Serial.print("HDOP: "); Serial.println(GPS.HDOP);
        Serial.print("Fecha (DDMMYY): "); Serial.print(GPS.day); Serial.print("/");
        Serial.print(GPS.month); Serial.print("/"); Serial.println(GPS.year);
        Serial.print("Hora UTC (HH:MM:SS): ");
        Serial.print(GPS.hour); Serial.print(":");
        Serial.print(GPS.minute); Serial.print(":");
        Serial.println(GPS.seconds);
    } else {
        Serial.println("Sin fijación de posición GPS.");
    }
}
