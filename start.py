from eve import Eve
import json
from flask import g, abort


def pre_get_permissions(request, lookup):
    id = request.view_args.get('id')
    lookup['id']=g.auth_value
    if id and not id == g.auth_value:
        abort(403)

def pre_delete_membergroups(request, lookup):
    group = request.view_args['membergroups']
    id = request.view_args['id']

    # if authed as group owner
    if isadmin(g.auth_value, group) or g.auth_value == id:
        # Delete the record
        app.data.driver.db['permissions'].update({'id': id},
                                            {'$pull': {'membergroups': group}})
    else:
        abort(403)

def post_delete_membergroups(request, payload):
    payload.status_code = 200


def pre_get_admingroups(request, lookup):
    group = request.view_args['admingroups']
    authedid = g.auth_value
    id = request.view_args['id']

    if not app.data.driver.db['permissions'].find_one({'id':id}):
        abort(422)

    if app.data.driver.db['permissions'].find_one({'id':id,'admingroups':group}):
        abort(422)

    if isadmin(authedid,group) or not app.data.driver.db['permissions'].find_one({'admingroups':group}):
        app.data.driver.db['permissions'].update({'id': id},
                                                 {'$push': {'admingroups': group}})
    else:
        abort(403)


def pre_get_membergroups(request, lookup):
    group = request.view_args['membergroups']
    authedid = g.auth_value
    id = request.view_args['id']

    if not isadmin(authedid, group):
        abort(403)

    if app.data.driver.db['permissions'].find_one({'id':id,'membergroups':group}):
        abort(422)

    app.data.driver.db['permissions'].update({'id': id},
                                        {'$push': {'membergroups': group}})



def pre_post_permissions(request):
    groups = request.view_args.get('membergroups',[])
    groups += request.view_args.get('admingroups',[])
    id = request.json['id']

    for group in groups:
        if isadmin(id, group):
            continue
        elif g.auth_value == id and isadmin(id, group):
            continue
        else:
            abort(403)

def isadmin(id, group):
    return bool(app.data.driver.db['permissions'].find_one({'id': id, 'admingroups': group}))

app = Eve()
app.on_pre_GET_permissions += pre_get_permissions
app.on_pre_DELETE_membergroups += pre_delete_membergroups
app.on_pre_POST_permissions += pre_post_permissions
app.on_pre_GET_admingroups += pre_get_admingroups
app.on_pre_GET_membergroups += pre_get_membergroups
app.on_post_DELETE_membergroups += post_delete_membergroups

if __name__ == '__main__':
    app.run()
