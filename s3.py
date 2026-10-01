import boto3
import os
from botocore.exceptions import NoCredentialsError

S3_BUCKET_VIDEOS = os.getenv("S3_BUCKET_VIDEOS", "my-videos-bucket")
S3_BUCKET_THUMBNAILS = os.getenv("S3_BUCKET_THUMBNAILS", "my-thumbnails-bucket")

s3_client = boto3.client("s3")

def upload_file_to_s3(file_obj, object_name: str, content_type: str, bucket_name: str):
    """
    Sube un archivo a S3 y retorna la URL pública (si el bucket lo permite) 
    o simplemente el object key para luego generar presigned urls.
    """
    try:
        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            object_name,
            ExtraArgs={'ContentType': content_type}
        )
        return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
    except NoCredentialsError:
        print("Credenciales no disponibles")
        return None
    except Exception as e:
        print(f"Error subiendo archivo a S3: {e}")
        return None

def generate_presigned_url(object_name: str, bucket_name: str, expiration=3600):
    """
    Genera una URL firmada para compartir de manera segura un objeto de S3
    """
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except Exception as e:
        print(f"Error generando url firmada: {e}")
        return None
    return response
