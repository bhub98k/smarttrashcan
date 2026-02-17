#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Update.h>

const char* host = "chosemaker";
const char* ssid = "S23+";  // 替换为您的WiFi SSID
const char* password = "bhub98k9487666";  // 替换为您的WiFi密码
WebServer server(80);

// 登录页面 HTML
String loginIndex = 
"<html lang='zh-TW'>"
"<head>"
"<meta charset='UTF-8'>"
"<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
"<title>登入</title>"
"<style>"
"body { font-family: Arial, sans-serif; background-color: #f0f2f5; color: #333; text-align: center; margin: 0; padding: 0; }"
"h2 { color: #4d79ff; }"
".form-input { width: 100%; padding: 10px; margin: 10px 0; border-radius: 4px; border: 1px solid #ccc; font-size: 16px; }"
".btn { background-color: #4d79ff; color: #fff; cursor: pointer; }"
".btn:hover { background-color: #3c63d2; }"
"#login-error { color: red; display: none; }"
"</style>"
"</head>"
"<body>"
"<div class='container'>"
"<h2>救世回收桶控制面板</h2>"
"<input id='username' class='form-input' type='text' placeholder='使用者名稱'>"
"<input id='password' class='form-input' type='password' placeholder='密碼'>"
"<button id='login-btn' class='btn' onclick='login()'>登入</button>"
"<p id='login-error'>帳號或密碼錯誤</p>"
"</div>"
"<script>"
"function login() {"
"const username = document.getElementById('username').value;"
"const password = document.getElementById('password').value;"
"if (username === 'admin' && password === 'admin') {"
"window.location.href = '/serverIndex';"  // 登录成功后跳转到控制面板
"} else {"
"document.getElementById('login-error').style.display = 'block';"
"}"
"}"
"</script>"
"</body>"
"</html>";

// 控制面板 HTML
String serverIndex =
"<html lang='zh-TW'>"
"<div class='container'>"
"<meta charset='UTF-8'>"
"<div id='control-panel'>"
"<h2>控制板首頁</h2>"
"<h3>連線狀態</h3> <h4>已連線(增強版)</h4>"
"<div>"
"<button class='btn' onclick=\"sendCommand('START')\">韌體更新</button>"
"<button class='btn' onclick=\"sendCommand('STOP')\">關機</button>"
"<button class='btn' onclick=\"sendCommand('RESTART')\">重啟</button>"
"<button class='btn' onclick=\"sendCommand('mode')\">前往選用模組控制</button>"
"</div>"
"<div id='data-display'>救世回收桶監控視窗: <span id='esp32-data'>-</span></div>"
"</div>"
"<div id='file-upload'>"
"<h2>自訂模型上傳</h2>"
"<input id='file-input' type='file'>"
"<button class='btn' onclick='uploadFile()'>上傳檔案</button>"
"<div id='prgbar'>"
"<div id='bar'></div>"
"</div>"
"<p id='upload-status'></p>"
"</div>"
"</div>"
"<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js'></script>"
"<script>"
"function sendCommand(command) {"
"fetch(`/command?cmd=${command}`, { method: 'GET' })"
".then(response => response.text())"
".then(data => { console.log('Command response:', data); })"
".catch(error => { console.error('Command error:', error); });"
"}"

"setInterval(() => {"
"fetch('/data')"
".then(response => response.json())"
".then(data => {"
"document.getElementById('esp32-data').innerText = data.value;"
"})"
".catch(error => { console.error('Data error:', error); });"
"}, 1000); // 每秒更新一次"

"function uploadFile() {"
"const fileInput = document.getElementById('file-input');"
"const file = fileInput.files[0];"
"const formData = new FormData();"
"formData.append('update', file);"

"const xhr = new XMLHttpRequest();"
"xhr.open('POST', '/update', true);"
"xhr.upload.onprogress = function(event) {"
"if (event.lengthComputable) {"
"const percentComplete = (event.loaded / event.total) * 100;"
"document.getElementById('bar').style.width = percentComplete + '%';"
"}"
"};"

"xhr.onload = function() {"
"if (xhr.status === 200) {"
"document.getElementById('upload-status').innerText = '上傳成功';"
"fileInput.value = ''; // Reset the file input"
"document.getElementById('bar').style.width = '0%'; // Reset progress bar"
"} else {"
"document.getElementById('upload-status').innerText = '上傳失敗: ' + xhr.responseText;"
"}"
"};"

"xhr.onerror = function() {"
"document.getElementById('upload-status').innerText = '上傳過程中出現錯誤';"
"};"

"xhr.send(formData);"
"}"
"</script>";

void setup(void) {
  Serial.begin(115200);
  // Connect to WiFi network
  WiFi.begin(ssid, password);
  Serial.println("");
 
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
 
  // 使用mDNS，網址 http://chosemaker.local
  if (!MDNS.begin(host)) { 
    Serial.println("Error setting up MDNS responder!");
    while (1) {
      delay(1000);
    }
  }
  Serial.println("mDNS responder started");
  
  // Return login page
  server.on("/", HTTP_GET, []() {
    server.sendHeader("Connection", "close");
    server.send(200, "text/html", loginIndex);
  });

  // Return server index page
  server.on("/serverIndex", HTTP_GET, []() {
    server.sendHeader("Connection", "close");
    server.send(200, "text/html", serverIndex);
  });
  
  // Handle uploading firmware file 
  server.on("/update", HTTP_POST, []() {
    server.sendHeader("Connection", "close");
    server.send(200, "text/plain", (Update.hasError()) ? "FAIL" : "OK");
    ESP.restart();
  }, []() {
    HTTPUpload& upload = server.upload();
    if (upload.status == UPLOAD_FILE_START) {
      Serial.printf("Update: %s\n", upload.filename.c_str());
      if (!Update.begin(UPDATE_SIZE_UNKNOWN)) { // start with max available size
        Update.printError(Serial);
      }
    } else if (upload.status == UPLOAD_FILE_WRITE) {
      /* flashing firmware to ESP */
      if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
        Update.printError(Serial);
      }
    } else if (upload.status == UPLOAD_FILE_END) {
      if (Update.end(true)) { // true to set the size to the current progress
        Serial.printf("Update Success: %u\nRebooting...\n", upload.totalSize);
      } else {
        Update.printError(Serial);
      }
    }
  });
  
  server.begin();
}
 
void loop(void) {
  server.handleClient();
  delay(1);
}
