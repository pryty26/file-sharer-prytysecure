import logging
from psycopg2 import errors
from config import get_cursor
import hashlib
import hmac

from prytysecure.config import commonplace_text


def verify_pass(user_input:str, password:str, salt:str=False):
    try:
        if not salt:
            input_pass = hashlib.sha512(user_input.encode('utf-8')).hexdigest()
        else:
            input_pass = hashlib.sha512(user_input.encode('utf-8') + salt.encode('utf-8')).hexdigest()
        return f'{hmac.compare_digest(input_pass, password)}'
    except Exception as e:
        logging.error(f'verify pass error{e}')
        return f'{False}'


def get_data_by_name(user_id, filename, safe_token, user_options):
    if not user_id or not safe_token:
        return {'success':False, 'message':'please fill all input'}
    try:
        with get_cursor(conn_commit=False) as cursor:
            if commonplace_text(user_options) in ['selectall']:
                cursor.execute(
                    '''
                SELECT download_url, save_key, fileName, expires_at, created_at FROM files 
                WHERE filename = %s AND (safe_token = %s OR  user_id = %s)
                ''',(safe_token, user_id)
                               )
            else:
                cursor.execute(
                    '''
                SELECT download_url, save_key, fileName, expires_at, created_at FROM files 
                WHERE filename = %s AND (safe_token = %s OR  user_id = %s)
                ''',(filename, safe_token, user_id)
                               )
            the_all_data = cursor.fetchall()
            if not the_all_data:
                return {'success':False,
                        'message':'File not found. '
                        'You may or may not be logged in, or the file name is incorrect.'
                        }

            results = []
            for row in the_all_data:
                results.append({
                    "download_url": row[0],
                    "save_key": row[1],
                    "fileName": row[2],
                    "expires_at": row[3].isoformat() if row[3] else None,
                    "created_at": row[4].isoformat() if row[4] else None
                })
            results.append({"count": len(results),})
            return {
                "success": True,
                "message": results
            }

    except OperationalError as e:
        logging.error(f'get_url_by_name error{e}')
        return {
            'success': False,
                'message': 'System Critical Failure. '
                           'Please contact the administrator if possible, or try again later.'
                }
    except Exception as e:
        logging.error(f'get_url_by_name error{e}')
        return {
            'success': False,
                'message': 'System error'
                }





