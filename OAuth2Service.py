import os
import requests

class OAuth2Service:
    def __init__(self) -> None:
        self.accessToken = None
    def getAccessToken(self):
        return self.accessToken
    def setAccessToken(self, accessToken):
        self.accessToken = accessToken


_oauth2Instance = None
def getOAuth2Instance():
    global _oauth2Instance
    if _oauth2Instance:
        return _oauth2Instance
    else:
        _oauth2Instance = OAuth2Service()
        return _oauth2Instance

class ConfigService:
    
    def __init__(self) -> None:
        self.redirect_uri_summarisation_task = os.getenv("REDIRECT_URI_SUMMARISE_TASK")
        self.redirect_uri_comparison_task = os.getenv("REDIRECT_URI_COMPARISON_TASK")

        self.tenant_id = os.getenv("TENANT_ID")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.scopes = os.getenv("SCOPES").split(" ")
        self.host_name = os.getenv("HOST_NAME")
        self.site_path = os.getenv("SITE_PATH")
        self.orro_file_path = os.getenv("ORRO_FILE_PATH")
        self.orro_file_sheet_name = os.getenv("ORRO_FILE_SHEET_NAME")
        self.orr_template_path = os.getenv("ORRO_TEMPLATE_PATH")
        self.orro_template_sheet_name = os.getenv("ORRO_TEMPLATE_SHEET_NAME")
        
    def get_redirect_uri_summarisation_task(self):
        return self.redirect_uri_summarisation_task
    
    def get_redirect_uri_comparison_task(self):
        return self.redirect_uri_comparison_task
    
    def get_tenant_id(self):
        return self.tenant_id
    def get_client_id(self):
        return self.client_id
    def get_client_secret(self):
        return self.client_secret
    def get_scopes(self):
        return self.scopes
    def get_host_name(self):
        return self.host_name
    def get_site_path(self):
        return self.site_path
    def get_orro_file_path(self):
        return self.orro_file_path
    def get_orro_sheet_name(self):
        return self.orro_file_sheet_name
    def get_orro_template_path(self):
        return self.orr_template_path
    def get_orro_template_sheet_name(self):
        return self.orro_template_sheet_name
    
_configInstance = None
def getConfigInstance():
    global _configInstance
    if _configInstance is None:
        _configInstance = ConfigService()
    return _configInstance

class SharepointService:
    def __init__(self):
        self._configInstance = getConfigInstance()
        self._oauth2Instance = getOAuth2Instance()

        self.site_id = self.search_site_id()
        self.drive_id = self.search_drive_id()
        
    
    def get_site_id(self):
        return self.site_id
    def get_drive_id(self):
        return self.drive_id
    
    
    def search_site_id(self):
        host_name = _configInstance.get_host_name()
        site_path = _configInstance.get_site_path()
        access_token = self._oauth2Instance.getAccessToken()
        uri = f'https://graph.microsoft.com/v1.0/sites/{host_name}:/{site_path}'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(uri, headers=headers)
        site = response.json()
        if site:
            return site['id']
        else:
            raise Exception("Site not found")
    
    def search_drive_id(self):
        access_token = self._oauth2Instance.getAccessToken()
    
        url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        drives = response.json().get('value', [])
        if drives:
            for drive in drives:
                if drive['name'] == 'IT Category Management':
                    return drive['id']
                raise Exception("Drive not found")
        else:
            raise Exception("Drive not found")
    
_sharepointInstance = None  
def getSharePointInstance():
    global _sharepointInstance
    if _sharepointInstance is None:
        _sharepointInstance = SharepointService()   
    return _sharepointInstance   