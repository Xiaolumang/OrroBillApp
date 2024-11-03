import azure.functions as func
import logging
import msal
import webbrowser
import os
from OAuth2Service import getOAuth2Instance
from OAuth2Service import getSharePointInstance
from OAuth2Service import getConfigInstance
import ProcessFiles.helper as helper 

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
_configInstance = getConfigInstance()


tenant_id = _configInstance.get_tenant_id()
client_id = _configInstance.get_client_id()
client_secret = _configInstance.get_client_secret()
scopes = _configInstance.get_scopes()

redirect_uri_summarisation_task = _configInstance.get_redirect_uri_summarisation_task()
redirect_uri_comparison_task = _configInstance.get_redirect_uri_comparison_task()

authority = f'https://login.microsoft.com/{tenant_id}'
auth_app = msal.ConfidentialClientApplication(client_id,client_secret,authority)

# @app.route(route="http_trigger")
# def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     name = req.params.get('name')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('name')

#     if name:
#         return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
#     else:
#         return func.HttpResponse(
#              "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
#              status_code=200
#         )

def get_access_token(access_code,redirect_uri):
    token_response = auth_app.acquire_token_by_authorization_code(
        access_code, 
        scopes = scopes,
        redirect_uri = redirect_uri)
    
    if 'access_token' in token_response:
        return token_response['access_token']
    else:
        logging.info(token_response)
        raise Exception("Failed to receive access token")



@app.route(route="orro_bill/summarise_login")
def orro_bill_summarise(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('Python HTTP trigger function processed a request.')
    auth_url = auth_app.get_authorization_request_url(scopes=scopes,
                                                 redirect_uri=redirect_uri_summarisation_task)
    
    logging.info(auth_url)
    # webbrowser.open(auth_url)
    # return func.HttpResponse(f'please login first')
    return func.HttpResponse(
        status_code=302,
        headers={'Location': auth_url}
    )

@app.route(route="orro_bill/compare_login")
def orro_bill_compare(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('Python HTTP trigger function processed a request.')
    auth_url = auth_app.get_authorization_request_url(scopes=scopes,
                                                 redirect_uri=redirect_uri_comparison_task)
   
    # webbrowser.open(auth_url)
    # return func.HttpResponse(f'please login first') 
    return func.HttpResponse(
        status_code=302,
        headers={'Location': auth_url}
    )   



@app.route(route="execute_summarisation", auth_level=func.AuthLevel.ANONYMOUS)
def summarisation_task(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    auth_code = req.params.get("code")
    oauthInstance = getOAuth2Instance()

    if auth_code:
        try:
            access_token = get_access_token(auth_code,redirect_uri_summarisation_task)
            oauthInstance.setAccessToken(access_token)
            
        except:
            return func.HttpResponse(f'no access token from server!!')
        helper.summarisation_task(_configInstance.get_orro_file_path(),
                                  _configInstance.get_orro_sheet_name())

    else:
        return func.HttpResponse(f"no auth code received!!")
    return func.HttpResponse(f'acess token succeed!!')
        
@app.route(route="execute_comparison", auth_level=func.AuthLevel.ANONYMOUS)
def comparison_tasks(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    auth_code = req.params.get("code")
    oauthInstance = getOAuth2Instance()

    if auth_code:
        try:
            access_token = get_access_token(auth_code,redirect_uri_comparison_task)
            oauthInstance.setAccessToken(access_token)
            
        except:
            return func.HttpResponse(f'no access token from server!!')
        helper.comparison_task(_configInstance.get_orro_file_path(),
                                  _configInstance.get_orro_sheet_name())

    else:
        return func.HttpResponse(f"no auth code received!!")
    return func.HttpResponse(f'acess token succeed!!')    
    

