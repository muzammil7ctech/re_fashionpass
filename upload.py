
from Code.utils.libraries import * 
import requests
from Code.utils.logs import *
from sessions import *
import boto3
confing_name='config.ini'
BASE_PATH=os.getcwd()
configur = ConfigParser() 
configur.read(os.path.join(BASE_PATH,'Code',confing_name)  ) #for dev
aws_access_key_id = configur.get('credantials','ACCESS_KEY')
aws_secret_access_key = configur.get('credantials','SECRECT_ACCESS_KEY')
bucket_name = 'our-picks-for-you-section'
cosin_path=str(os.path.join(BASE_PATH,'Code','cosin_similarity_registry')).replace('\\', '/')
val_path=f"{cosin_path}/{str(time.strftime('%Y_%m_%d'))}/" 

csv_file_path =f'{val_path}cosin_similarity_{datetime.date.today()}.csv'#'D:/fp5/fp-new/Code/notebook/cosin_similarity_date_diff_2024-02-21.csv' #f'{val_path}cosin_similarity_{datetime.date.today()}.csv'
print(csv_file_path)
csv_file_path_exp=f'{val_path}cosin_similarity_exp{datetime.date.today()}.csv'
print(csv_file_path_exp)
s3_key = f"cosin_csv/cosin_similarity_{datetime.date.today()}.csv"
s3_keyx = f"cosin_csv/cosin_similarity_x{datetime.date.today()}.csv"
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Upload the file
url = 'https://dev-api.fashionpass.com/api/v1/Content/UploadFiles'
files = {'file': ('cosin_similarity_dev.csv', open(csv_file_path,'rb'))} #dev
data = {'folder': 'ml_csv'}
files1 = {'file': ('cosin_similarity_stage.csv', open(csv_file_path,'rb'))} #stage
files2 = {'file': ('cosin_similarity_live.csv', open(csv_file_path,'rb'))} #live





filesx = {'file': ('cosin_similarity_dev.csv', open(csv_file_path_exp,'rb'))}#dev
data2 = {'folder': 'ml_csv_experiment'}
filesx1 = {'file': ('cosin_similarity_stage.csv', open(csv_file_path_exp,'rb'))}#stage
filesx2 = {'file': ('cosin_similarity_live.csv', open(csv_file_path_exp,'rb'))} #live



try:
    try:
        s3.upload_file(csv_file_path, bucket_name, s3_key)
        s3.upload_file(csv_file_path_exp, bucket_name, s3_keyx)
        logging.info(f'{csv_file_path} uploaded {bucket_name}/{s3_key}')
    except:
        logging.info(f'{csv_file_path} has not been uploaded to {bucket_name}/{s3_key}')
    logging.info('file uploading to ml pick ')
    try:

        #--added csv with out normalization--#
        response = requests.post(url, files=files, data=data)
        response1 = requests.post(url, files=files1, data=data)
        response2 = requests.post(url, files=files2, data=data)

        #--added csv with  normalization--#
        response = requests.post(url, files=filesx, data=data2)
        response1 = requests.post(url, files=filesx1, data=data2)
        response2 = requests.post(url, files=filesx2, data=data2)
        logging.info(f'--api--{response.text}')
        logging.info(f'--api--{response1.text}')
        logging.info(f'--api--{response2.text}')
    except:
        logging.info('not upload through api')
except:
    logging.info('uploading file not found')
    
