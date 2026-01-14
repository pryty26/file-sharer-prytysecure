print('author:pryty26(back-end)\nWeartime(front-end)')
import logging
from logging.handlers import RotatingFileHandler
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import FastAPI, File, UploadFile, Request, Depends, HTTPException, status, Form
from main_func import api_add_file, api_delete_file, api_delete_expires
from functools import wraps
import uuid
from typing import Optional
from jwt_func import verify_jwt_token, generate_jwt_token
from config import commonplace_text
app = FastAPI()
def jwt_check(func):
    @wraps(func)
    def wrapper(request: Request,*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token:
            raise HTTPException(status_code=401, detail="token unfound")
        result = verify_jwt_token(token=token)
        if not result.get('success') or not result['message'].get('safe_key'):
            raise HTTPException(status_code=418, detail='lvaIIid T0k#n '
                                                        'St@t%s c*d#: 99999999999999999')
        kwargs['data'] = result.get('message')
        return func(request, *args, **kwargs)
    return wrapper






handler = RotatingFileHandler(
    'honeypot.log',
    maxBytes=10*1024*1024,
    backupCount=3
)

logging.basicConfig(
    level=logging.WARNING,
    format = '%(asctime)s - %(message)s',
    handlers=[handler]
)


limiter = Limiter(
    key_func = get_remote_address,
    default_limits = ['360 per minute, 3600 per days'],
)


limiter.app = app


@app.delete('/api/delete')
@jwt_check
@limiter.limit("20/minute, 150/hours, 220/days")
def api_delete_page(
        request:Request,
        user_input: str = Form(..., alias="userinput"),
        user_options: Optional[str] = Form(None, alias="useroptions"),
        **kwargs
):
    #api_delete_file(user_options: str = None, safe_token:str = None, user_input:str = None):
    safe_token = kwargs['data'].get('safe_token')
    return api_delete_file(user_options=user_options,safe_token=safe_token,user_input=user_input)

@app.post("/api/upload")
@limiter.limit("10/minute, 100/hours, 200/days")
async def upload_file_page(
        request: Request,
        file: UploadFile = File(...),
):
    filename = file.filename


    user_ip = request.client.host


    result = api_add_file(
        file=file,
        filename=filename,
        user_ip=user_ip,
        user_id="guest",
        expires=3600
    )

    return result
@app.post("/api/get_token")
@limiter.limit("20/minute, 150/hours, 220/days")
async def api_get_token_page(
    request:Request,
):

    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        print('debug mode')
        if token:
            result = verify_jwt_token(token=token)
            if result.get('success',None) and result['message'].get('safe_key'):
                print(token)
                return {'success':True,'message':'Process success Token exists','token':f'{token}'}
        payload = {
            'safe_key':f"{uuid.uuid4()}",
            'user_id':'guest',
            'role':'guest',
            'gmail_verified':False
        }
        #maybe i should change the payload?hmmm
        expires_minutes = 60*24*7
        generate_result = generate_jwt_token(payload_data=payload, expires_minutes=expires_minutes)
        if generate_result.get('success'):
            return {
                'success': True,
                'message': 'Token generation success',
                'token': f"{generate_result.get('message')}"
                }

        return {'success': True, 'message': f'Token generation error:{generate_result.get('message')}', 'token': ""}
    except MemoryError as e:
        return {'success':False, 'message':'Token too large or user too much'}
    except Exception as e:
        return {'success':False, 'message':'System error please contact with admin'}
