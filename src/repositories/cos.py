import os
from common import config as app_config
import ibm_boto3
import ibm_boto3.s3
from ibm_boto3.s3 import transfer
from ibm_boto3.s3.transfer import TransferConfig as TrsConfig
from ibm_botocore.client import Config, ClientError
import datetime

def saveCSVFile(item_name, file_path):
    try:
        bucket_name = app_config.get("IBM_CLOUD", "BUCKET_NAME")

        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = TrsConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        cos_res = ibm_boto3.resource("s3",
            ibm_api_key_id = app_config.get("IBM_CLOUD", "COS_API_KEY"),
            ibm_service_instance_id = app_config.get("IBM_CLOUD", "COS_IAM_SERVICEID_CRN"),
            ibm_auth_endpoint = app_config.get("IBM_CLOUD", "IBM_AUTH_ENDPOINT"),
            config = Config(signature_version="oauth"),
            endpoint_url = app_config.get("IBM_CLOUD", "ENDPOINT_URL"))

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        file_path_name = file_path + "/" + item_name

        fnsplit = item_name.split(".")
        bucket_file_name = fnsplit[0] + str(datetime.datetime.now()) + "." + fnsplit[1]

        with open(file_path_name, "rb") as file_handle:
            cos_res.Object(bucket_name, bucket_file_name).upload_fileobj(
                Fileobj=file_handle,
                Config=transfer_config
            )

        os.remove(file_path_name)

        print("Transfer for {0} Complete!\n".format(item_name))
        return "File Saved."
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
        return "Unable to Save File.."
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))
        return "Unable to upload File.."