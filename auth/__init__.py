#!/usr/bin/env python

import webbrowser

from .utils import start_local_server, is_remote_session

from globus_sdk import (NativeAppAuthClient, TransferClient,
                        AccessTokenAuthorizer, AuthClient,
                        BasicAuthorizer)


CLIENT_ID = 'd7fb8a54-25bd-4337-bc92-e7c26e2c4c5b'
REDIRECT_URI = 'http://localhost:8000'
SCOPES = ('openid email profile')
# 'urn:globus:auth:scope:transfer.api.globus.org:all '
# 'urn:globus:auth:scope:datasearch.api.globus.org:all')

SERVER_ADDRESS = ('127.0.0.1', 8000)


def do_native_app_authentication(client_id, redirect_uri,
                                 requested_scopes=None):
    """
    Does a Native App authentication flow and returns a
    dict of tokens keyed by service name.
    """
    client = NativeAppAuthClient(client_id=client_id)
    client.oauth2_start_flow(requested_scopes=SCOPES,
                             redirect_uri=redirect_uri)
    url = client.oauth2_get_authorize_url()

    server = start_local_server(listen=SERVER_ADDRESS)

    if not is_remote_session():
        webbrowser.open(url, new=1)

    auth_code = server.wait_for_code()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    server.shutdown()

    # return a set of tokens, organized by resource server name
    return token_response.by_resource_server

def do_basic_authentication(userid,password):
    client = BasicAuthorizer(userid,password)

def main():

    # start the Native App authentication process
    tokens = do_native_app_authentication(CLIENT_ID, REDIRECT_URI)
    transfer_token = tokens['datasearch.api.globus.org']['access_token']
    authorizer = AccessTokenAuthorizer(access_token=transfer_token)
    print(authorizer.access_token)

if __name__ == '__main__':
    if not is_remote_session():
        main()
    else:
        print('This example does not work on a remote session.')