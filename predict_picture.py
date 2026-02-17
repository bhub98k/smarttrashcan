from ultralytics import YOLO

# Load a model
#model = YOLO("yolo11n-cls.pt")  # load an official model
model = YOLO("bestv4.pt")  # load a custom model

# Predict with the model
results = model("20241106_223846.png")  # predict on an image
for result in results:
    to_port=str(result.probs.top5[0])
    conf=result.probs.top5conf
print(to_port,end='  ')
print(conf)