#include <WiFi.h>
#include <WiFiClient.h>
#include <esp_camera.h>
#include <HTTPClient.h>
#include "base64.h"
#include <ESP32Servo.h>

Servo myservo2;
#define servoPin2 12 

const int ledPin = 4;
const int ledone = 33;

int trig = 15;
int echo = 14;
int cm;
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

const char* ssid = "TP-Link_CHY";
const char* password = "@@062467733";
const char* serverUrl = "http://192.168.1.186:8787/upload";

void ultrasound() {
    digitalWrite(trig, LOW);
    delayMicroseconds(5);
    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig, LOW);
    int echotime = pulseIn(echo, HIGH);
    cm = echotime / 29.4 / 2;
}

void takeandsend() {
    digitalWrite(ledPin, HIGH);
    delay(30);
    camera_fb_t * fb = esp_camera_fb_get();
    delay(30);
    digitalWrite(ledPin, LOW);
    if (!fb) {
        Serial.println("Camera capture failed");
        return;
    }
    String base64Image = base64::encode((uint8_t*)fb->buf, fb->len);
    HTTPClient http;
    http.begin(serverUrl);
    String jsonRequest = "{\"image\":\"" + base64Image + "\"}";
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST((uint8_t*)jsonRequest.c_str(), jsonRequest.length());
    digitalWrite(ledPin, HIGH);
    delay(10);
    digitalWrite(ledPin, LOW);
    esp_camera_fb_return(fb);
    
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println(httpResponseCode);
        Serial.println(response);
        response.trim();
        if (response == "0") {
            myservo2.write(20);
        } else if (response == "1") {
            myservo2.write(70);
        } else if (response == "2") {
            myservo2.write(120);
        }
    } else {
        Serial.printf("Error code: %d\n", httpResponseCode);
    }
    http.end();
}

void setup() {
    Serial.begin(115200);
    ESP32PWM::allocateTimer(0);
    ESP32PWM::allocateTimer(1);
    ESP32PWM::allocateTimer(2);
    ESP32PWM::allocateTimer(3);

    myservo2.setPeriodHertz(50);
    myservo2.attach(servoPin2, 1000, 2000);
    pinMode(trig, OUTPUT);
    pinMode(echo, INPUT);
    pinMode(ledPin, OUTPUT);
    pinMode(ledone, OUTPUT);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 10;
    config.fb_count = 1;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        ultrasound();
        if (cm < 5) {
            takeandsend();
        }
    } else {
        Serial.println("WiFi not connected");
    }
}
