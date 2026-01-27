#author: pryty26(backend)
from psycopg2 import OperationalError, DataError

import psycopg2
from config import (
    get_cursor,
    commonplace_text
)


from config import (
    SUPABASE_S3_ENDPOINT,
    SUPABASE_ACCESS_KEY,
    SUPABASE_SECRET_KEY,
    BUCKET_NAME,
    PRESIGNED_EXPIRES
)
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import uuid
import logging
import boto3
from werkzeug.utils import secure_filename

s3_client = boto3.client('s3',
    endpoint_url=SUPABASE_S3_ENDPOINT,
    aws_access_key_id=SUPABASE_ACCESS_KEY,
    aws_secret_access_key=SUPABASE_SECRET_KEY,
)

def sql_add_files(filename, save_key, download_url, expires_at, user_id, ip, safe_token):

    try:
        with get_cursor(conn_commit=True) as cursor:
            sql = '''
            INSERT INTO files (filename, save_key, download_url , expires_at, user_id, ip, safe_token) 
            VALUES (%s, %s ,%s, %s, %s, %s, %s)            
            '''
            params = (
                filename,  # %s 1: filename
                save_key,  # %s 2: save_key
                download_url,  # %s 3: download_url
                expires_at,  # %s 4: expires_at
                user_id,  # %s 5: user_id
                ip, # %s 6: ip
                safe_token # %s 6 safe_token

            )

            cursor.execute(sql, params)
    except psycopg2.IntegrityError as e:
        if 'unique constraint' in str(e) and 'save_key' in str(e):
            logging.critical(f'!!!!!!!!!!!!!!!!!!!!!!!!!{e}\n the Probability is 1/2^122!!!')
            return {'success': False, 'message': 'save key already exist please try again',
                    'easter_egg':'bro u r just so luc'}
    except OperationalError as e:
        logging.error(f'sql_add_files Operational error:{e}')
        return {
            'success': False,
                'message': 'System Critical Failure. '
                           'Please contact the administrator if possible, or try again later.'
                }
    except DataError:
        return {
            'success': False,
                'message': 'Filename is too large '
                          }
    except Exception as e:
        logging.error(f'sql_add_files error:{e}')
        return {
            'success': False,
                'message': 'System error. '
                           'Please contact the administrator if possible, or try again later.'
                }














def api_add_file(file, filename:str, user_ip, user_id:str, expires:int = PRESIGNED_EXPIRES, safe_token:str=None):
    try:
        if not user_id:
            user_id = 'guest'

        if safe_token and file and filename:
            if (not file.content_length or file.content_length < 1 * 1024
                    or file.content_length > 10 * 1024 * 1024):
                return {'success': False, 'message': 'file size error',
                        'easter_egg': 'hmmm \n ({>u<}) \nperhaps i should make a VIP that users can subscribe! '
                                      'and then if u pay u can upload bigger file?'
                                      'kw kw kw kw kw kw✧( •̀ u •́ )✧'
                }

            if (file.filename.count('.') > 1 or
                    file.filename.count('\\') > 0 or
                    file.filename.count('/') > 0 or
                    not file.filename.strip().lower().endswith(
                    ('.txt', '.pdf', '.docx', '.xlsx', '.pptx', '.rtf', '.odt', '.csv','.zip',
                     '.rar', '.7z', '.tar', '.gz',
                     '.jpg', '.jpeg', '.bmp', '.png', '.gif', '.webp'))):
                return {'success': False, 'message': 'invalid filename'}



            random_name = str(uuid.uuid4()) + secure_filename(file.filename)
            content_type = file.mimetype or 'application/octet-stream'

            s3_client.upload_fileobj(
                file.stream,
                BUCKET_NAME,
                random_name,
                ExtraArgs={'ContentType': content_type}
            )



            download_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': random_name},
                ExpiresIn=expires
            )


            expires_at = datetime.now() + timedelta(seconds=expires)


            #def sql_add_files(filename, save_key, download_url, expires_at, user_id, ip)
            sql_add_files(filename=secure_filename(filename),
                           save_key=random_name,download_url=download_url,
                           expires_at=expires_at.isoformat(),
                           user_id=user_id, ip=user_ip,
                           safe_token=safe_token,
                          )

            return {
                'success': True,
                'message': 'upload success',
                'downloadUrl': download_url,
                'fileName': secure_filename(filename),
                'fileId':random_name,
                'fileSize':file.content_length,
                "uploadedAt": datetime.now(),
                'expires_at':expires_at.isoformat(),
                'user_id':user_id,
                'expires_in_seconds': expires
            }



        return {'success': False, 'message': 'file not found'}

    except Exception as e:
        logging.error(f'\napi_add_file error:\n{e}')
        return {'success': False, 'message': 'system error'}










def delete_files(file_keys=None, bucket_name=BUCKET_NAME,):
    if not file_keys:
        return{'success':False,
                   'message':'No keys exist'}
    try:
        objects = [{'Key': key} for key in file_keys]

        response = s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={
                'Objects': objects,#Objects:[{key:key},{key:key}]
                'Quiet': False
            }
        )

        result = []
        if 'Deleted' in response:
            result.append(f"delete success files count:{len(response.get('Deleted'))} ")

        if 'Errors' in response and response.get('Errors'):
            for error in response['Errors']:
                result.append(f"\ndelete failed: {error.get('Key')} - {error.get('Message')}")
        all_deleted = [deleted.get('Key') for deleted in response.get('Deleted')]
        if not all_deleted:
            logging.error(f'delete files error:{result}')
            return{'success':False,
                   'message':'Fuck, there is not even a single one was deleted successfully.'
                             ' There was only fucking errors.'}
            #this message wont show at front-end or to the user

        return {'success':True, 'message':result, 'all_deleted':all_deleted}

    except ClientError as e:
        logging.error(f"delete multiple file error: {e.response['Error']['Message']}")
        return {'success':False,'message':"client error"}
    except Exception as e:
        logging.error(f"delete multiple file error: {e}")
        return {'success':False,'message':"system error"}








#delete_files(bucket_name, file_keys):
def api_delete_expires():
    try:
        with get_cursor(conn_commit=True) as cursor:
            sql = 'SELECT save_key FROM files WHERE expires_at < NOW()'
            cursor.execute(sql)
            counts = cursor.fetchall()
            if not counts:
                return {'success': False, 'message': f"did not found any expired files"}
            file_keys = [count[0] for count in counts]

            result = delete_files(file_keys=file_keys)

            all_deleted = result.get('all_deleted')
            if not all_deleted:
                return {'success': False, 'message': f"file_func error while deletion"}
            placeholders = ','.join(['%s'] * len(all_deleted))
            delete_sql = f'''
            DELETE FROM files
            WHERE save_key IN ({placeholders})
            '''

            cursor.execute(delete_sql, all_deleted)

            deleted_count = cursor.rowcount

            return{'success':True,'message':f"{deleted_count}"}

    except Exception as e:
        logging.error(f'api_delete_expires error:{e}')
        return {'success': False, 'message': f"error"}


def api_delete_file(user_options:str=None, safe_token:str=None, user_input:str=None):
    if not user_input or not safe_token:
        return {'success': False, 'message': f"please fill save_key and safe_token"}
    if not user_options:
        user_options = "default"
    try:
        user_options = commonplace_text(user_options)
        with get_cursor(conn_commit=True) as cursor:
            if user_options in ['saveid','savetoken','savekey']:
                sql = 'SELECT save_key FROM files WHERE save_key = %s AND safe_token = %s'
                cursor.execute(sql, (user_input, safe_token))
            else:
                sql = 'SELECT save_key FROM files WHERE filename = %s AND safe_token = %s'
                cursor.execute(sql, (user_input, safe_token))
            counts = cursor.fetchall()
            if not counts:
                return {'success': False, 'message': "No files found matching the provided criteria"}
            file_keys = [count[0] for count in counts]

            result = delete_files(file_keys=file_keys)

            all_deleted = result.get('all_deleted')
            if not all_deleted:
                return {'success': False, 'message': f"file_func error while deletion"}
            placeholders = ','.join(['%s'] * len(all_deleted))
            delete_sql = f'''
            DELETE FROM files
            WHERE save_key IN ({placeholders})
            '''
            cursor.execute(delete_sql, all_deleted)

            return{'success':True,'message':f"{user_input} were successfully deleted."}

    except Exception as e:
        logging.error(f'api_delete_expires error:{e}')
        return {'success': False, 'message': f"error"}

