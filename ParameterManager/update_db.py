from django.shortcuts import HttpResponse, redirect, render
import threading
from django.http import JsonResponse
from opcua import Client
from uaclient.uaclient import UaClient
from random import randint
from .models import Node, Value, Database
import re
import time
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test


# @user_passes_test(lambda u: u.is_superuser)
def add_database(request):
    db_name = request.POST['db-name']
    uname = request.POST['uname']
    psw = request.POST['psw']
    url = request.POST['url']
    auth_ = str(uname) + ':' + str(psw) + '@'
    indx = url.index('//') + 2
    complete_url = url[:indx] + auth_ + url[indx:]
    databases = Database.objects.all()
    for database in databases:
        database.active = False
        database.save()

    database = Database(url=url, db_name=db_name, auth_name=uname, auth_password=psw, complete_url=complete_url,
                        updating=True)
    database.save()
    db_id = database.id
    get_from_plc(db_id)
    if request.is_ajax():
        return JsonResponse({'error_message': 's'})


def connect_to_plc(count_2, db_id):
    database = Database.objects.get(id=db_id)
    if count_2 > 2:
        database.delete()
        return False
    count_2 += 1
    try:
        try:

            client = Client(database.url)
            client.connect()
        except :
            client = Client(database.complete_url)
            client.connect()
    except Exception as e:
        print('-------')
        print(type(e).__name__, e)
        print("Couldn't connect to PLC database")
        print('-------')
        time.sleep(5)
        client = connect_to_plc(count_2, db_id)

    return client


def walk_plc(count, db_id, node, data):
    database = Database.objects.get(id=db_id)
    if not data:
        try:
            display_name = str(node.get_display_name())
            start = display_name.index('Text:') + 5
            parent_name = display_name[start:-1]
        except:
            parent_name = node

        # Get parent id
        parent_id = re.findall("(?<=\().*", str(node.nodeid))[0][:-1]
        data.append({"id": parent_id, 'parent': '#', 'text': parent_name})

    # Get parent name
    try:
        display_name = str(node.get_display_name())
        start = display_name.index('Text:') + 5
        parent_name = display_name[start:-1]
    except:
        parent_name = node

    # Get parent id
    parent_id = re.findall("(?<=\().*", str(node.nodeid))[0][:-1]

    parent = Node.objects.filter(database=database, node_id=parent_id)
    if not parent:
        if count:
            parent = Node(database=database, node_id=parent_id, name=parent_name, first=True)
        else:
            parent = Node(database=database, node_id=parent_id, name=parent_name)
        parent.save()
    else:
        parent = parent[0]

    a = node.get_children()
    for node in a:

        # Get node name ---------------------------------
        try:
            display_name = str(node.get_display_name())
            start = display_name.index('Text:') + 5
            node_name = display_name[start:-1]
        except:
            node_name = node

        # Get node id ------------------------------------
        node_id = re.findall("(?<=\().*", str(node.nodeid))[0][:-1]

        node_ = Node.objects.filter(database=database, node_id=node_id)
        if not node_:
            node_ = Node(database=database, parent=parent, node_id=node_id, name=node_name)
            node_.save()

        else:
            node_ = node_[0]

        # If it is not an endpoint  create a nested list and call walk_(node) again to get node's children
        if node.get_children():

            data.append({"id": node_id, 'parent': parent_id, 'text': node_name})

            # Call walk_ again for the child
            walk_plc(count, db_id, node, data)

        # If it is an endpoint add nodes to the list -------
        else:
            try:
                value = node.get_value()
            except:
                value = None

            data.append({"id": node_id, 'parent': parent_id, 'text': node_name})

            node_value = Value(node=node_)

            if str(value).lower() == 'true':
                node_value.bool_value = True
                node_value.save()
            elif str(value).lower() == 'false':
                node_value.bool_value = False
                node_value.save()
            else:
                try:
                    node_value.float_data = float(str(value))
                    node_value.save()
                except:
                    node_value.str_data = str(value)
                    node_value.save()
    return data


def get_from_plc(db_id):
    # Walk through all databases
    data = []
    count_2 = 0
    client = connect_to_plc(count_2, db_id)
    if client:
        node = client.get_objects_node()
        inputs = client.get_node('ns=3;s=Inputs')
        print("Getting database from PLC ...")
        count = True
        data = walk_plc(count, db_id, node, data)
        database = Database.objects.get(id=db_id)
        database.updating = False
        database.save()
        print("PLC database loading finished.")
        return data


# @user_passes_test(lambda u: u.is_superuser)
def set_checks(request):
    check_ids = request.POST.getlist('varg[]')
    uncheck_ids = request.POST.getlist('unvarg[]')
    print(check_ids)
    db_id = int(check_ids[-1])
    check_ids = check_ids[:-1]
    database = Database.objects.get(id=db_id)
    nodes = Node.objects.filter(database=database, important=True)
    for node in nodes:
        node_id = node.node_id
        if node_id not in check_ids:
            node.important = False
            node.save()

    for check in check_ids:
        print(check)
        nodes = Node.objects.filter(database=database)
        for node in nodes:
            try:
                if node.node_id == check:
                    node.important = True
                    node.save()
                    print(node.name)
                elif node.parent.node_id == check:
                    node.important = True
                    node.save()
                    print(node.name)
            except:
                pass

    print('Updated important data.')
    return HttpResponse('')


def check_plc(count, db_id, node, data):
    print('...')
    database = Database(id=db_id)
    error_messages = {}
    # Get parent name
    try:
        display_name = str(node.get_display_name())
        start = display_name.index('Text:') + 5
        parent_name = display_name[start:-1]
    except:
        parent_name = node

    # Get parent id
    parent_id = re.findall("(?<=\().*", str(node.nodeid))[0][:-1]

    parent = Node.objects.filter(node_id=parent_id)
    if not parent:
        if count:
            first_node_list = Node.objects.filter(first=True)
            for item in first_node_list:
                item.first = False
                item.save()
                count = False
                print(parent_name, parent_id)
            parent = Node(database=database, node_id=parent_id, name=parent_name, first=True)
        else:
            parent = Node(database=database, node_id=parent_id, name=parent_name)
        parent.save()
    else:
        parent = parent[0]

    a = node.get_children()
    for node in a:

        # Get node name ---------------------------------
        try:
            display_name = str(node.get_display_name())
            start = display_name.index('Text:') + 5
            node_name = display_name[start:-1]
        except:
            node_name = node

        # Get node id ------------------------------------
        node_id = re.findall("(?<=\().*", str(node.nodeid))[0][:-1]

        node_ = Node.objects.filter(node_id=node_id)
        if not node_:
            node_ = Node(database=database, parent=parent, node_id=node_id, name=node_name)
            node_.save()

        else:
            node_ = node_[0]
            node_.parent = parent
            node_.node_id = node_id
            node_.name = node_name
            node_.save()

        # If it is not an endpoint  create a nested list and call walk_(node) again to get node's children
        if node.get_children():

            # Call walk_ again for the child
            check_plc(count, db_id, node, data)

        # If it is an endpoint add nodes to the list -------
        else:
            try:
                value = node.get_value()
            except:
                value = None
            node_value = Value.objects.filter(node=node_).order_by('-id')
            if node_value:
                node_value = node_value[0]

                if str(value).lower() == 'true' or str(value).lower() == 'false':
                    if str(node_value).lower() == 'true':
                        value_ = Value(node=node_, bool_value=True)
                        value_.save()
                    elif str(value).lower() == 'false':
                        value_ = Value(node=node_, bool_value=False)
                        value_.save()

                    if node_.bool_optimal:
                        if str(node_.bool_optimal).lower() != str(value).lower():
                            message = node_name + "'s value is different from optimal one"
                            error_message = {'message': message, 'tag': 'danger'}
                            error_messages[node_name] = error_message

                else:
                    try:
                        float_value = float(str(value))
                        if node_value.float_data:
                            if float_value != node_value.float_data:
                                value_ = Value(node=node_, float_data=float_value)
                                value_.save()
                        if node_.lowest_optimal:
                            if float_value < node_.lowest_optimal:
                                message = node_name + "'s value is low"
                                error_message = {'message': message, 'tag': 'danger'}
                                error_messages[node_name] = error_message
                        if node_.highest_optimal:
                            if float_value > node_.highest_optimal:
                                message = node_name + "'s value is high"
                                error_message = {'message': message, 'tag': 'danger'}
                                error_messages[node_name] = error_message

                    except:
                        str_value = str(value)
                        if node_value.str_data:
                            if str_value != node_value.str_data:
                                value_ = Value(node=node_, str_data=str_value)
                                value_.save()
                        if node_.str_optimal:
                            if str_value != node_.str_optimal:
                                message = node_name + "'s value is different"
                                error_message = {'message': message, 'tag': 'danger'}
                                error_messages[node_name] = error_message

    return data, error_messages


# @user_passes_test(lambda u: u.is_superuser)
def refresh_db(request):
    id_list = request.POST.getlist('id[]')
    db_id = id_list[0][0]
    db_id = int(db_id)

    count_2 = 0
    # Connect with PLC
    client = connect_to_plc(count_2, db_id)
    if client:
        database = Database.objects.get(id=db_id)
        if not database.updating:
            database.updating = True
            database.save()
            print("Checking for updates ...")
            # Walk through all databases
            node = client.get_objects_node()
            inputs = client.get_node('ns=3;s=Inputs')
            plc = client.get_node('ns=3;s=PLC')
            data = []
            count = True
            data, error_messages = check_plc(count, db_id, node, data)
            error_messages = {
                'error_message': 'the value changed drastically',
                'error_message1': 'the value didnt change',
            }

            client.disconnect()
            database = Database.objects.get(id=db_id)
            database.updating = False
            database.save()
            print('Checking for updates finished.')
            if request.is_ajax():
                return JsonResponse({'error_message': error_messages})
        else:
            print('Database is being updated already ...')
            if request.is_ajax():
                return JsonResponse({'error_message': {}})


# @user_passes_test(lambda u: u.is_superuser)
def delete_important(request):
    id = int(request.POST['parameter'])
    parameter = Node.objects.get(id=id)
    parameter.important = "False"
    parameter.save()
    return render(request, 'show_importants.html')


def set_optimal_values(request):
    field_list = []
    id = int(request.POST['parameter'])
    node = Node.objects.get(id=id)
    if node.value_set.all():
        last_value = node.value_set.all().order_by('-id')[0]
        if last_value.bool_value is not None:
            print(node.name, last_value.bool_value)
            field_list.append('radio')
        if last_value.float_data is not None:
            field_list.append('number')
        if last_value.str_data is not None:
            field_list.append('text')
    if request.is_ajax():
        return JsonResponse({'field_list': field_list})


def update_optimal_values(request):
    for key in request.POST:
        if key == 'bool':
            print(request.POST[key])
    return redirect('get-importants')


# @user_passes_test(lambda u: u.is_superuser)
def make_graph(request):
    id = int(request.POST['parameter'])
    parameter = Node.objects.get(id=id)
    parameter.show_graph = True
    parameter.save()
    return JsonResponse({'msg': 'ok'}, safe=False)






