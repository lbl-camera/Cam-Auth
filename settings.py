from eve.auth import TokenAuth
from auth import AccessTokenAuthorizer, AuthClient
from globus_sdk.exc import AuthAPIError

MONGO_HOST = 'localhost'
MONGO_PORT = 27017

# Skip these if your db has no auth. But it really should.
# MONGO_USERNAME = '<your username>'
# MONGO_PASSWORD = '<your password>'

MONGO_DBNAME = 'cam-auth'

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']

schema = {
    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
    'id': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 100,
        'unique': True,
        'required': True,
        # 'isgroupunique': True,
    },
    'membergroups': {
        'type': 'list',
        'required': True,
        'default': [],
        'schema': {'type': 'string',
                   }
    },
    'admingroups': {
        'type': 'list',
        'required': True,
        'default': [],
        'schema': {'type': 'string',
                   }

    },
}


class GlobusTokenAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        if token == 'test':
            self.set_request_auth_value('test')
            return True

        authorizer = AccessTokenAuthorizer(access_token=token)
        ac = AuthClient(authorizer=authorizer)
        try:
            self.set_request_auth_value(ac.oauth2_userinfo().data['preferred_username'])
            return ac.oauth2_userinfo().http_status == 200
        except AuthAPIError:
            return False


permissions = {
    # 'title' tag used in item links. Defaults to the resource title minus
    # the final, plural 's'
    # 'item_title': 'pluginpackage',

    # by default the standard item entry point is defined as
    # '/pluginpackages/<ObjectId>'. We leave it untouched, and we also enable an
    # additional read-only entry point. This way consumers can also perform
    # GET requests at '/pluginpackages/<name>'.
    # 'additional_lookup': {
    #     'url': 'regex(".+")',
    #     'field': 'id'
    # },

    'item_url': r'regex("[\w@.]+")',

    'item_lookup_field': "id",

    # # We choose to override global cache-control directives for this resource.
    # 'cache_control': 'max-age=10,must-revalidate',
    # 'cache_expires': 10,

    # most global settings can be overridden at resource level
    'resource_methods': ['GET', 'POST', 'DELETE'],

    'schema': schema,

    'authentication': GlobusTokenAuth,

    'id_field': 'id'
}

DOMAIN = {
    'permissions': permissions,
    'membergroups': {'url': 'membergroups/<regex("[\w@.]+"):id>/<regex("[\w]+"):membergroups>',
                     'authentication': GlobusTokenAuth, },
    'admingroups': {'url': 'admingroups/<regex("[\w@.]+"):id>/<regex("[\w]+"):admingroups>',
                    'authentication': GlobusTokenAuth, },
}
