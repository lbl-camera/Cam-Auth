import requests
import json
from auth import do_native_app_authentication, CLIENT_ID, REDIRECT_URI, AccessTokenAuthorizer, AuthClient
import pytest

import api

# Normally you would do native app authentication like so:
# token, id = api.authenticate()

# but for testing purposes,
api.TOKEN = 'test'
api.ID = 'test'

def test_api():
    # Create self user
    api.add_user()

    # create foo group for self
    api.create_group('foo')

    # create someone else's user
    api.add_user('jerry@parks.com')

    # add someone else to self's group
    api.add_member_to_group('foo')

    # delete them from the group
    api.delete_member_from_group('foo','jerry@parks.com')

    # make them an admin
    api.add_admin_to_group('foo','jerry@parks.com')

    with pytest.raises(Exception) as e_info:
        api.create_group('foo')

    with pytest.raises(Exception) as e_info:
        api.add_user('jerry@parks.com')

    # Delete doesn't fail if that group isn't in that record
    api.delete_member_from_group('foo','jerry@parks.com')

    # the auth'd user can only see their own record
    assert len(api._get('permissions/')['_items'])==1