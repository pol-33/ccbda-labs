import logging.handlers
import boto3
import os
from botocore.exceptions import ClientError
from django.conf import settings
import pathlib
from datetime import datetime, timezone
import json

try:
    from elasticsearch import Elasticsearch
except Exception:  # elasticsearch may not be installed locally
    Elasticsearch = None

logger = logging.getLogger('django')
logger_root = logging.getLogger()


class S3RotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, maxBytes=0, backupCount=0, encoding=None, delay=0):
        super().__init__(
            filename=filename, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay
        )
        try:
            # Build S3 client configuration
            # In AWS (EC2/EB), boto3 will automatically use IAM role credentials
            # For local development, it will use environment variables
            s3_config = {"region_name": settings.AWS_REGION}

            # Only add explicit credentials if they are provided (for local dev)
            if getattr(settings, 'AWS_ACCESS_KEY_ID', None) and getattr(settings, 'AWS_SECRET_ACCESS_KEY', None):
                s3_config["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                s3_config["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
                if getattr(settings, 'AWS_SESSION_TOKEN', None):
                    s3_config["aws_session_token"] = settings.AWS_SESSION_TOKEN

            self.s3_client = boto3.client("s3", **s3_config)
            self.bucket_name = getattr(settings, 'AWS_S3_BUCKET_NAME', None)
            self.logs_prefix = getattr(settings, 'AWS_S3_LOGS_PREFIX', 'logs/')
            if self.logs_prefix and not self.logs_prefix.endswith("/"):
                self.logs_prefix += "/"
            self.s3_enabled = bool(self.bucket_name)
        except Exception as e:
            logger_root.warning(f"S3 logging disabled due to initialization error: {e}")
            self.s3_enabled = False

    def rotate(self, source, dest):
        if callable(self.rotator):
            self.rotator(source, dest)
        else:
            if os.path.exists(source):
                os.rename(source, dest)

                # Only upload to S3 if enabled and file has content
                if self.s3_enabled and os.path.exists(dest) and os.stat(dest).st_size > 0:
                    try:
                        stem = pathlib.Path(source).stem
                        suffix = pathlib.Path(source).suffix
                        now = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
                        s3_key = f'{self.logs_prefix}{stem}.{now}{suffix}'
                        self.s3_client.upload_file(dest, self.bucket_name, s3_key)
                        logger_root.info(f"Log file uploaded to S3: {s3_key}")
                    except Exception as e:
                        logger_root.error(f"Failed to upload log to S3: {e}")

                # Remove the rotated file
                if os.path.exists(dest):
                    os.remove(dest)


    def emit(self, record):
        try:
            log_data = self.format(record)
            try:
                if self.shouldRollover(record):
                    self.doRollover()
                self.stream.write(log_data + self.terminator)
            except Exception as err:
                self.handleError(record)
        except ClientError as e:
            logger.error(f"Error sending log to S3: {e}")


class JsonFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.fmt_dict = kwargs.get('basic', {"message": "message"})
        self.default_time_format = kwargs.get('time_format', "%Y-%m-%dT%H:%M:%S")
        self.default_msec_format = kwargs.get('msec_format', "%s.%03dZ")
        self.datefmt = None
        self.extra = kwargs.get('extra', {})

    def usesTime(self) -> bool:
        return "asctime" in self.fmt_dict.values()

    def formatMessage(self, record) -> dict:
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in self.fmt_dict.items()}

    def format(self, record) -> str:
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        # Derive app segment
        try:
            from django.conf import settings as dj_settings
            p = os.path.relpath(record.pathname, dj_settings.BASE_DIR).split('/')
        except Exception:
            p = record.pathname.split('/')
        if record.filename in p:
            try:
                p.remove(record.filename)
            except ValueError:
                pass
        if 'site-packages' in p:
            add_chunk = False
            app_name = ''
            for item in p:
                if item == 'site-packages':
                    add_chunk = True
                    continue
                if add_chunk:
                    app_name += f'/{item}'
            message_dict['app'] = app_name
        else:
            message_dict['app'] = p[0] if p else ''

        if isinstance(record.args, dict):
            for k, v in record.args.items():
                message_dict[k] = v

        for k, v in self.extra.items():
            message_dict[k] = v

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            message_dict["exc_info"] = record.exc_text
        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)


class ElasticsearchHandler(logging.handlers.BufferingHandler):
    def __init__(self, index="logs", capacity=100):
        super().__init__(capacity=capacity)
        if Elasticsearch is None:
            raise RuntimeError("elasticsearch package not installed")
        self.es_client = Elasticsearch(cloud_id=settings.ELK_CLOUD_ID, basic_auth=("elastic", settings.ELK_PASSWORD))
        self.index = index

    def emit(self, record):
        log_entry = self.format(record)
        self.es_client.index(index=self.index, document=json.loads(log_entry))

    def flush(self):
        for record in self.buffer:
            log_entry = self.format(record)
            self.es_client.index(index=self.index, document=json.loads(log_entry))
        self.buffer = []
