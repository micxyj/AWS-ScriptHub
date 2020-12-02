import boto3
import os
import time
import botocore.exceptions
import datetime
from datetime import timezone
import sys
import uuid
import subprocess
import logging
import re


# 设置日志
current_time = str(datetime.datetime.now()).replace(' ', '-')
logging.basicConfig(level=logging.INFO,
                    filename='job-logging-{}.log'.format(current_time),
                    filemode='w',
                    )

# 获取参数
bucket_name = sys.argv[1]
prefix = sys.argv[2]
convert_template = 'reinvent'
start = sys.argv[3]
end = sys.argv[4]

# 定义所需要用到的服务
transcribe_client = boto3.client('transcribe')
s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')

x = 3
now = datetime.datetime.now(timezone.utc) - datetime.timedelta(seconds=x)


# 检查用户输入的prefix格式是否正确
def check_prefix():
    if not prefix.endswith('/'):
        raise Exception("Invalid prefix, must be endwith /")


# 检查文件是否存在
def check_if_file_exist(file_key):
    pattern = re.compile(r"[^a-zA-Z0-9-_.!*'()/]")
    s = pattern.findall(file_key)
    for i in (set(s)):
        file_key = file_key.replace(i, '-')
    pattern = re.compile(r"[-]{2,}")
    s = pattern.findall(file_key)
    for i in (set(s)):
        file_key = file_key.replace(i, '-')
    response = s3_client.list_objects(
        Bucket=bucket_name, Prefix='reinvent_clip/' + file_key.replace('mp4', 'srt'))
    if 'Contents' in response.keys():
        return True
    else:
        return False


def convert(bucket_name, file_name):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url(
        'get_object', Params={'Bucket': bucket_name, 'Key': file_name})
    cmd = '''./mediainfo --Inform="General;%Duration%" ''' + '\'' + url + '\''
    duration = subprocess.check_output(cmd, shell=True)

    pattern = re.compile(r"[^a-zA-Z0-9-_.!*'()/]")
    file_input = "s3://" + bucket_name + '/' + file_name
    s = pattern.findall(file_name)
    for i in (set(s)):
        file_name = file_name.replace(i, '-')
    pattern = re.compile(r"[-]{2,}")
    s = pattern.findall(file_name)
    for i in (set(s)):
        file_name = file_name.replace(i, '-')
    clip_output = "s3://" + bucket_name + '/reinvent_clip/' + file_name[:-4]
    audio_output = "s3://" + bucket_name + '/reinvent_audio/' + file_name[:-4]

    StartTimecode = "00:" + start + ":00:00"
    EndTimecode = "00:" + str(int(int(duration)/60000) - int(end)) + ":00:00"

    client = boto3.client(
        'mediaconvert', endpoint_url='https://lkbik0yga.mediaconvert.cn-northwest-1.amazonaws.com.cn', region_name='cn-northwest-1')
    try:
        response = client.create_job(
            JobTemplate=convert_template,
            Role='arn:aws-cn:iam::192996968360:role/MediaConvert-reinvent',
            Settings={
                "Inputs": [
                    {
                        "FileInput": file_input,
                        "InputClippings": [
                            {
                                # 例子： "StartTimecode": "00:10:00:00", "EndTimecode": "00:36:00:00" ，截取后的视频从10分钟开始，36分钟结束。
                                "StartTimecode": StartTimecode,  # 使用格式 HH:MM:SS:FF, 其中 HH 是小时，MM 是分钟，SS 是秒，FF 是帧编号
                                "EndTimecode": EndTimecode  # 使用格式 HH:MM:SS:FF，其中 HH 是小时，MM 是分钟，SS 是秒，FF 是帧编号
                            }
                        ],
                    }
                ],
                'OutputGroups': [
                    {
                        "CustomName": "clip",
                        "OutputGroupSettings": {
                            "FileGroupSettings": {
                                "Destination": clip_output
                            }
                        }
                    },
                    {
                        "CustomName": "clip",
                        "OutputGroupSettings": {
                            "FileGroupSettings": {
                                "Destination": audio_output
                            }
                        }
                    }
                ],
            }
        )
    except botocore.exceptions.ClientError as error:
        logging.info(error)


def submit_jobs(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    object_count = 0
    try:
        for obj in bucket.objects.filter(Prefix=prefix):
            file_name = obj.key
            if file_name.endswith('.mp4'):
                if not check_if_file_exist(file_name):
                    convert(bucket_name, file_name)
                    object_count = object_count + 1
    except botocore.exceptions.ClientError as error:
        logging.info(error)
    logging.info('Object numger: ' + str(object_count))


def checking_result():
    client = boto3.client(
        'mediaconvert', endpoint_url='https://lkbik0yga.mediaconvert.cn-northwest-1.amazonaws.com.cn', region_name='cn-northwest-1')
    running_jobs = 1
    success_jobs = 0

    logging.info('----Clippling processing----')
    while running_jobs:
        time.sleep(60)

        submitted_response = client.list_jobs(
            Status='SUBMITTED'  # 'SUBMITTED'|'PROGRESSING'|'COMPLETE'|'CANCELED'|'ERROR'
        )

        processing_response = client.list_jobs(
            Status='PROGRESSING'  # 'SUBMITTED'|'PROGRESSING'|'COMPLETE'|'CANCELED'|'ERROR'
        )

        running_jobs = len(
            submitted_response['Jobs']) + len(processing_response['Jobs'])

    complete_response = client.list_jobs(
        Status='COMPLETE'  # 'SUBMITTED'|'PROGRESSING'|'COMPLETE'|'CANCELED'|'ERROR'
    )
    if len(complete_response['Jobs']):
        for job in complete_response['Jobs']:
            if job['CreatedAt'] >= now:
                success_jobs = success_jobs + 1
   # logging.info('Success jobs: ' + str(success_jobs))


def list_error():
    client = boto3.client('mediaconvert', endpoint_url='https://lkbik0yga.mediaconvert.cn-northwest-1.amazonaws.com.cn',
                          region_name='cn-northwest-1')

    response = client.list_jobs(
        Status='ERROR'  # 'SUBMITTED'|'PROGRESSING'|'COMPLETE'|'CANCELED'|'ERROR'
    )

    if len(response['Jobs']):
        for job in response['Jobs']:
            if job['CreatedAt'] >= now:
                logging.info(job['CreatedAt'].strftime("%m/%d/%Y, %H:%M:%S") + ': ' + job['Settings']['Inputs'][0][
                    'FileInput'] + ': ' + job['ErrorMessage'])


# 启动音频转语音任务
def start_tanscribe(audio_dir, media_format='mp4'):

    # 读取音频文件路径
    audio_lst = []
    list_s3_response = s3_client.list_objects(
        Bucket=bucket_name, Prefix=audio_dir)['Contents']

    # 生成文件路径列表
    for i in list_s3_response:
        if i['Size'] != 0:
            file_route = 's3://{}/'.format(bucket_name) + i['Key']
            audio_lst.append(file_route)

    # 异步启动每一个音频文件的转化任务
    for i in audio_lst:
        s3_prefix = i.replace(
            's3://{}/reinvent_audio/'.format(bucket_name), 'reinvent_clip/')
        s3_prefix = s3_prefix[:-3] + 'srt'
        response = s3_client.list_objects(Bucket=bucket_name, Prefix=s3_prefix)
        if 'Contents' not in response.keys():
            audio_name = i.split('/')[-1].split('.')[0]
            job_id = uuid.uuid4().hex
            try:
                response = transcribe_client.start_transcription_job(
                    TranscriptionJobName=job_id,
                    LanguageCode='en-US',
                    MediaFormat=media_format,
                    Media={
                        'MediaFileUri': i
                    },
                    OutputBucketName=bucket_name,
                    OutputKey='reinvent_subtitle/' +
                    i.replace('s3://' + bucket_name +
                              '/reinvent_audio/', '')[:-3] + 'json',
                    JobExecutionSettings={'AllowDeferredExecution': True,
                                          'DataAccessRoleArn': 'arn:aws-cn:iam::192996968360:role/transcribe_role'}
                )
                logging.info(
                    "{} converting job create...............".format(audio_name))
                logging.info('\n')
            except Exception as e:
                logging.info(e)


# 轮询直到所有transcribe任务完成
def wait_transcribe_job_complete():
    while True:
        time.sleep(20)
        response = transcribe_client.list_transcription_jobs(
            Status='IN_PROGRESS')
        logging.info('Transcribe jobs in progress.....................')
        if len(response['TranscriptionJobSummaries']) == 0:
            logging.info('\n')
            logging.info("Jobs done..........................")
            logging.info('\n')
            break


# 下载transcribe生成的json，转化为srt文件，并上传回s3
def json2src():
    unreg_sym = {'(': 'thisisleftbrackets', ')': 'thisisrightbrackets'}
    wait_transcribe_job_complete()
    list_s3_response = s3_client.list_objects(
        Bucket=bucket_name, Prefix='reinvent_subtitle/')['Contents']
    for i in list_s3_response:
        s3_prefix = i['Key'].replace('reinvent_subtitle/', 'reinvent_clip/')
        s3_prefix = s3_prefix[:-4] + 'srt'
        response = s3_client.list_objects(Bucket=bucket_name, Prefix=s3_prefix)
        if 'Contents' not in response.keys():
            if i['Size'] != 0:
                file_name = i['Key'].split('/')[-1]
                try:
                    s3_resource.Bucket(bucket_name).download_file(
                        i['Key'], file_name)
                    logging.info(
                        "{} is being processed..............".format(file_name))
                    origin_file_name = file_name
                    for bracket in unreg_sym.keys():
                        file_name = file_name.replace(
                            bracket, unreg_sym[bracket])
                    if origin_file_name != file_name:
                        os.rename(origin_file_name, file_name)
                    os.system(
                        'python3 aws-transcribe-captioning-tools/src/srt.py {} {}'.format(file_name, file_name.split('.')[0] + '.srt'))
                    with open(file_name.split('.')[0] + '.srt', 'r') as f_obj:
                        srt_lst = f_obj.readlines()
                    srt_lst.insert(3, "字幕由Amazon Transcribe服务提供\n")
                    srt_string = ''.join(srt_lst)
                    with open(file_name.split('.')[0] + '.srt', 'w') as f_obj:
                        f_obj.write(srt_string)
                    if origin_file_name != file_name:
                        os.rename(file_name, origin_file_name)
                        os.rename(file_name.split('.')[
                            0] + '.srt', origin_file_name.split('.')[0] + '.srt')
                        file_name = origin_file_name
                    s3_resource.Bucket(bucket_name).upload_file(
                        file_name.split('.')[0] + '.srt', 'reinvent_clip/' + i['Key'][:-4].replace('reinvent_subtitle/', '') + 'srt')
                    os.remove(file_name)
                    os.remove(file_name.split('.')[0] + '.srt')
                except Exception as e:
                    logging.info(e)
                logging.info("{} has been converted to srt and uploaded to S3...............".format(
                    file_name))
                logging.info('\n')
    logging.info('Audio to srt task complete............................')


# 检查失败任务，并列出在日志上
def track_failed_file():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=prefix):
        file_key = obj.key
        if file_key.endswith('.mp4'):
            if not check_if_file_exist(file_key):
                logging.info(
                    "Check {} file, audio2srt job failed.................".format(file_key))


if __name__ == "__main__":
    try:
        check_prefix()
        submit_jobs(bucket_name)
        checking_result()
        list_error()
        start_tanscribe('reinvent_audio/' + prefix)
        json2src()
        track_failed_file()
    except Exception as e:
        logging.info(e)
