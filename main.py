from backend.pipelines import medieval_pipeline, extract_features_pipeline
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = {"image/jpeg", "image/png", "image/webp"}

@app.post("/images/transform")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=415, detail=f"Unsupported type: {file.content_type}")

    image_bytes = await file.read()

    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image")

    result = extract_features_pipeline.main(image=image)

    pipeline = medieval_pipeline.MedievalPipeline()
    prompt = "A human who lives in medieval period"

    try:
        result_image = pipeline.run(image, prompt)
        result_image.save("result_medieval.png")
        print("Image saved to result_medieval.png")
    except Exception as e:
        print(f"Error: {e}")

    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)