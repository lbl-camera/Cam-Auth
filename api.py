from auth import do_native_app_authentication, CLIENT_ID, REDIRECT_URI, AccessTokenAuthorizer, AuthClient
import requests, json
from typing import List

TOKEN = None
ID = None
SERVER = 'http://127.0.0.1:5000'


def authenticate():
    """
    Starts a local oauth2 server, launches a browser pointing to localhost. After oauth2 flow, the auth token and ID are
    returned.
    """

    global TOKEN, ID

    # Get tokens by doing native app authentication
    tokens = do_native_app_authentication(CLIENT_ID, REDIRECT_URI)

    # Extract the user id from the the Auth token client
    TOKEN = tokens['auth.globus.org']['access_token']
    authorizer = AccessTokenAuthorizer(access_token=TOKEN)
    ac = AuthClient(authorizer=authorizer)
    ID = ac.oauth2_userinfo().data['preferred_username']
    return TOKEN, ID


def add_user(id=None) -> dict:
    if not id: id = ID
    data = {'id': id,
            'membergroups': [],
            'admingroups': []}
    return _post('permissions', data)


def add_member_to_group(group, id=None) -> dict:
    if not id: id = ID
    return _get(f'membergroups/{id}/{group}')


def add_admin_to_group(group, id) -> dict:
    return _get(f'admingroups/{id}/{group}')


def delete_member_from_group(group, id=None) -> dict:
    if not id: id = ID
    return _delete(f'membergroups/{id}/{group}')


def create_group(group) -> dict:
    return _get(f'admingroups/{ID}/{group}')


def get_groups() -> List[str]:
    user = _get('permissions')['_items'][0]
    return user['membergroups'] + user['admingroups']


def _post(path, data) -> dict:
    content = json.loads(requests.post(f'{SERVER}/{path}', json.dumps(data),
                                       headers={'Content-Type': 'application/json', 'Authorization': TOKEN}).content)
    if content.get('_status') == 'ERR': raise Exception('Post failed')
    return content


def _get(path) -> dict:
    content = json.loads(requests.get(f'{SERVER}/{path}', headers={'Authorization': TOKEN}).content)
    if content.get('_status') == 'ERR': raise Exception('Get failed')
    return content


def _delete(path) -> dict:
    # etag = _get(path)['_etag']
    content = json.loads(
        requests.delete(f'{SERVER}/{path}', headers={'Authorization': TOKEN}).content)  # , 'If-Match': etag
    if content.get('_status') == 'ERR': raise Exception('Delete failed')
    return content
