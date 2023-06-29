from PIL import Image
import io

async def Image2BufferedReader(img:Image):
    '''
        ref:https://stackoverflow.com/questions/70168141/convert-bytes-into-bufferedreader-object-in-python
    '''
    b_handle = io.BytesIO()
    img.save(b_handle, format="PNG")
    b_handle.seek(0)
    b_handle.name = "temp.jpeg"
    b_br = io.BufferedReader(b_handle)
    return b_br