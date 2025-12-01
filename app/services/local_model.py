# app/services/local_model.py
import torch
import torchvision.transforms as transforms
from PIL import Image
import timm  # lightweight pretrained models

# Load a simple pretrained classifier
model = timm.create_model("resnet18", pretrained=True)
model.eval()

# Preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def classify_image_file(image_path: str) -> dict:
    try:
        img = Image.open(image_path).convert("RGB")
        input_tensor = preprocess(img).unsqueeze(0)

        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.nn.functional.softmax(outputs[0], dim=0)
            conf, pred_class = torch.max(probs, 0)

        # Simple heuristic: if confidence is too high → Real, else AI
        verdict = "Likely Real" if conf.item() > 0.85 else "Likely AI-generated"

        return {
            "verdict": verdict,
            "confidence": float(conf.item())
        }

    except Exception as e:
        return {"verdict": f"Error: {e}"}
