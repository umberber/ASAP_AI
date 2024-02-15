import time
from PIL import Image
from fastapi import FastAPI, UploadFile
from draw_image import *
from edit_image import *
from eval_image import evalulate_image
from db.update_db import *
from db.read_db import *

app=FastAPI()
BASE_PATH="samples"
@app.get("/")
async def root():
    return {"message":"hello world"}

@app.post("/upload")
async def upload(user_id:str,prompt:str,img_input:UploadFile):
    start=time.time()
    img_input = await img_input.read()
    update_image_to_db(img_input,
                       user_id,
                       upload_time=int(start),
                       isinput=True)
    update_text_to_db(prompt,user_id)
    end=time.time()
    return {
        "time_consumption":f"{end-start:.2f}"
    }

@app.get("/read")
async def read():
    start=time.time()
    img_input, img_file_name, prompt = read_infos_from_db(img_chunk_tbl,img_meta_tbl,text_tbl)
    end=time.time()
    return {
        "img_file_name":img_file_name,
        "prompt":prompt,
        "time_consumption":f"{end-start:.2f}"
    }

@app.get("/draw")
async def draw():
    start=time.time()
    img_input, img_file_name, prompt = read_infos_from_db(img_chunk_tbl,img_meta_tbl,text_tbl)
    user_id = img_file_name.split('_')[0]
    DALLE_img,DALLE_acc=draw_filtered_image_by_DALLE(prompt)
    SD_img=draw_image_by_SD(img_input,prompt)
    img_output=add_images(DALLE_img,SD_img)
    update_image_to_db(img_output,
                       user_id,
                       upload_time=int(start),
                       isinput=False)
    end=time.time()
    return {
        "DALLE_accuracy":f"{DALLE_acc:.2f}",
        "time_consumption":f"{end-start:.2f}"
    }