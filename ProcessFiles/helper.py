from OAuth2Service import getOAuth2Instance
from OAuth2Service import getSharePointInstance
from OAuth2Service import getConfigInstance

import requests
import pandas as pd
from io import BytesIO
import ProcessFiles.orro_summarise_task_helper as summarise_task_helper
import ProcessFiles.orro_compare_helper as comparison_task_helper
import  ProcessFiles.excel_helper as excel_helper
from datetime import datetime

_configInstance = getConfigInstance()
_oauth2Instance = getOAuth2Instance()
def content_from_path(file_path):
    _sharepointInstance = getSharePointInstance()
    site_id = _sharepointInstance.get_site_id()
    drive_id = _sharepointInstance.get_drive_id()
    #file_path = _configInstance.get_file_path()
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{file_path}:/content'

    headers = {
    'Authorization': f'Bearer {_oauth2Instance.getAccessToken()}'

}

# Make the GET request to download the file
    response = requests.get(url, headers=headers)

# Check if the request was successful
    if response.status_code == 200:
        return response.content
    else:
        response.raise_for_status()

def file_path_2_df(file_path, sheet_name):
    content = content_from_path(file_path)
    excel_data = BytesIO(content)
    df = pd.read_excel(excel_data,sheet_name=sheet_name)
    
    return df

def summarisation_task(file_path,sheet_name):
    # content = content_from_path(file_path)
    # excel_data = BytesIO(content)
    # df = pd.read_excel(excel_data,sheet_name=sheet_name)
    df = file_path_2_df(file_path, sheet_name)
    df = summarise_task_helper.summarise_by_cost_center(df)
    upload_df(df,'summarisation_4_Bronwyn.xlsx')

def comparison_task(file_path, sheet_name):
    df = file_path_2_df(file_path, sheet_name)
    df = comparison_task_helper.compare_charge_with_expect(df)

    upload_df(df,'comparison_4_Kelly.xlsx')


    

def upload_df(df,file_name):
    _sharepointInstance = getSharePointInstance()
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    if 'summari' in file_name:
        excel_buffer = excel_helper.highlight_excel(excel_buffer)
    if 'compar' in file_name:
        excel_buffer = excel_helper.expand_columns(excel_buffer)

    site_id =  _sharepointInstance.get_site_id()
    drive_id = _sharepointInstance.get_drive_id()
    tmp_folder = datetime.now().strftime("%m-%d-%Y")
    file_path = f'IT Invoices/2025FY/Orro 2025/{tmp_folder}/{file_name}'
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{file_path}:/content"

# Set the headers with the access token
    headers = {
    'Authorization': f'Bearer {_oauth2Instance.getAccessToken()}',
    'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

# Make the PUT request to upload the file
    response = requests.put(url, headers=headers, data=excel_buffer)

# Check the response
    if response.status_code == 201:
        print("File uploaded successfully.")
        print("File metadata:", response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")

