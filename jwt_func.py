import jwt
from config import JWT_TOKEN
import datetime
from datetime import timezone
import logging

def generate_jwt_token(payload_data:dict=None, expires_minutes:int=None):
    try:
        if not payload_data or not expires_minutes or expires_minutes < 0:
            return {'success':False,'message':'please fill all data'}
        exp = datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=expires_minutes)
        payload_data.update({
            "exp": exp,
            "iat": datetime.datetime.now(timezone.utc),
            "iss": "prytysecure",
        })
        payload = jwt.encode(payload=payload_data,key=JWT_TOKEN,algorithm="HS256")
        return{'success':True,'message':f'{payload}'}


    except jwt.PyJWTError as e:
        logging.error(f'generate_jwt_token JWTerror: {e}')
        return {'success': False, 'message': f'JWT generation error'}

    except (TypeError,ValueError) as e:
        logging.error(f'generate_jwt_token ValueError/TypeError: {e}')
        return {'success': False, 'message': f'Error please check your input'}

    except MemoryError as e:

        logging.error(f'generate_jwt_token MemoryError: {e}')
        return {'success': False, 'message': 'payload too large'}
    except Exception as e:
        logging.error(f'{e}')
        return{'success':False,'message':'system error'}



def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_TOKEN,
            algorithms=["HS256"],
            issuer="prytysecure"
        )
        return {'success': True, 'message': payload}
    except jwt.ExpiredSignatureError:
        return {'success': False, 'message': 'Token has expired'}
    except jwt.InvalidTokenError as e:
        logging.error(f'verify_jwt_token error: {e}')
        return {'success': False, 'message': f'InvalidToken'}
    except Exception as e:
        logging.error(f'verify_jwt_token error: {e}')
        return {'success': False, 'message': 'SystemError'}
