from ultralytics import YOLO
with open('SRBconfig.txt', 'r') as file:
    modelo = file.readline().strip().split('=')[1].strip()     
    datao = file.readline().strip().split('=')[1].strip() 
    epochso = int(file.readline().strip().split('=')[1].strip())
    imgszo = int(file.readline().strip().split('=')[1].strip())
    batcho = int(file.readline().strip().split('=')[1].strip())
    hsv_vo = float(file.readline().strip().split('=')[1].strip()) 
    save_periodo = int(file.readline().strip().split('=')[1].strip())
print(f"Model: {modelo}")
print(f"Data: {datao}")
print(f"Epochs: {epochso}")
print(f"Img size: {imgszo}")
print(f"Batch: {batcho}")
print(f"Hsv_v: {hsv_vo}")
print(f"Save_period: {save_periodo}")

model = YOLO(modelo)
model.train(data=datao, epochs=epochso, imgsz=imgszo, batch=batcho, hsv_v=hsv_vo , save_period=save_periodo)