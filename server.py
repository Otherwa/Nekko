import lzma
import io
from fastapi import FastAPI, File,  UploadFile
from pymongo import MongoClient
import gridfs
import os
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse


load_dotenv()
client = MongoClient()
app = FastAPI()

# client
fs = gridfs.GridFS(MongoClient(os.getenv('CON_')).Cat)


# routes
@app.get("/get_cat_images", responses={
    200: {
        "content": {"image/png": {}}
    }
})
async def get_image(name, keyword):
    if keyword == "Tatakae":
        try:
            image_bytes = fs.find_one({"filename": name}).read()
            image_stream = lzma.decompress(image_bytes)
            image_stream = io.BytesIO(image_stream)
            print(image_stream)
            return StreamingResponse(content=image_stream, media_type="image/png")
        except:
            # print(Exception)
            return {"Not Valid or File Not Found": True}
    else:
        return {"Not Valid": True}


@ app.post("/post_cat_image")
async def post_image(keyword, image: UploadFile = File(...)):
    if keyword == "Tatakae":
        # image buffer
        image_buffer = await image.read()

        compressed_buffer = lzma.compress(image_buffer)
        # ratio
        compress_ratio = (float(len(image_buffer)) -
                          float(len(compressed_buffer))) / float(len(image_buffer))
        print('Compressed: %d%%' % (100.0 * compress_ratio))

        fs.put(compressed_buffer, filename=image.filename)
        return {"filename": image, "posted": True, "compression_ratio": compress_ratio * 100.0}
    else:
        return {"Not Valid": True}
