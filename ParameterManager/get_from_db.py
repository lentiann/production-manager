from django.shortcuts import render
from django.http import JsonResponse
from opcua import Client
from .models import Database, Node, Value
from .models import Node, Value
from datetime import datetime
import time
from .update_db import get_from_plc
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
import json


def walk_db(node, data):
    if not data:
        data.append({"id": node.node_id, 'parent': '#', 'important': node.important, 'text': node.name})

    a = node.node_set.all()
    for node in a:

        # If it is not an endpoint  create a nested list and call walk_(node) again to get node's children
        if node.node_set.all():

            data.append({"id": node.node_id, 'parent': node.parent.node_id, 'important': node.important, 'text': node.name})

            # Call walk_db again for the child
            walk_db(node, data)

        # If it is an endpoint add nodes to the list -------
        else:

           data.append({"id": node.node_id, 'parent': node.parent.node_id, 'important': node.important,
                        'text': node.name, "state": {"checked":  node.important}})
    return data


# @user_passes_test(lambda u: u.is_superuser)
def get_database(request):
    dbs = Database.objects.filter(updating=True)
    for db in dbs:
    data = []

    databases = Database.objects.all()
    dbs = Database.objects.filter(next=True)
    if dbs:
        curr_db = dbs[0]
    else:
        curr_db = Database.objects.get(pk=1)

    all_nodes = Node.objects.filter(database=curr_db, first=True)
    if all_nodes:
        parent_node = all_nodes[0]
        data = walk_db(parent_node, data)
    else:
        time.sleep(10)
        get_database(request)
    check = False
    for db in databases:
        if db.id == curr_db.id + 1:
            db.next = True
            db.save()
            check = True
        else:
            db.next = False
            db.save()

    if not check:
        first_db = Database.objects.get(pk=1)
        first_db.next = True
        first_db.save()
    return JsonResponse(data, safe=False)


# @user_passes_test(lambda u: u.is_superuser)
def get_importants(request):
    data_list = []
    nodes = Node.objects.filter(important=True)
    for node in nodes:
        if node.value_set:
            last_value = node.value_set.all().order_by('-id')
            if last_value:
                last_value = last_value[0]
                value = last_value.str_data
                if not value:
                    value = last_value.float_data
                data_list.append((node, last_value.date, value))

    if request.is_ajax():
        dict_ = {}
        for parameter in data_list:
            dict_[parameter[0].pk] = [parameter[1], str(parameter[2])]
        return JsonResponse(dict_)
    return render(request, 'show_importants.html', {"parameters": data_list})


# @user_passes_test(lambda u: u.is_superuser)
def get_history(request):
    id = int(request.POST['parameter'])
    parameter = Node.objects.get(id=id)
    values = parameter.value_set.all()
    data_list = []
    for value in values:
        data_fields = []
        all_fields = [value.float_data, value.str_data, value.detail]
        for field in all_fields:
            if field:
                data_fields.append(field)
        data_list.append((value.date.strftime("%Y-%m-%d %H:%M:%S"), data_fields))

    data_list.sort()
    dict_ = {'data': data_list}
    return JsonResponse(dict_)


main_dict = {'Inputs': {}, 'Memory': {}, 'Outputs': {}}


def iomem_db(node):
    global main_dict
    try:
        display_name = str(node.get_display_name())
        start = display_name.index('Text:') + 5
        node_name = display_name[start:-1]
    except:
        node_name = node

    if node_name == "Inputs":
        v = node.get_children()
        for node in v:
            display_name = str(node.get_display_name())
            start = display_name.index('Text:') + 5
            node_name = display_name[start:-1]
            main_dict['Inputs'][node_name] = node.get_value()

    elif node_name == "Outputs":
        v = node.get_children()
        for node in v:
            display_name = str(node.get_display_name())
            start = display_name.index('Text:') + 5
            node_name = display_name[start:-1]
            main_dict['Outputs'][node_name] = node.get_value()

    elif node_name == "Memory":
        v = node.get_children()
        for node in v:
            display_name = str(node.get_display_name())
            start = display_name.index('Text:') + 5
            node_name = display_name[start:-1]
            main_dict['Memory'][node_name] = node.get_value()

    return main_dict


# @login_required()
def get_iomem(request):
    global main_dict

    inputs = Node.objects.filter(name="Inputs")
    outputs = Node.objects.filter(name="Outputs")
    memories = Node.objects.filter(name="Memory")

    if inputs and outputs and memories:
        inputs = Node.objects.filter(parent=inputs[0])
        for input in inputs:
            input_name = input.name
            input_value = input.value_set.all().order_by('-id')
            i_value = input_value[0].str_data
            if not i_value:
                i_value = input_value[0].float_data
            elif not i_value:
                i_value = input_value[0].detail
            main_dict['Inputs'][input_name] = str(i_value)

        outputs = Node.objects.filter(parent=outputs[0])
        for output in outputs:
            output_name = output.name
            output_value = output.value_set.all().order_by('-id')
            o_value = output_value[0].str_data
            if not o_value:
                o_value = output_value[0].float_data
            elif not o_value:
                o_value = output_value[0].detail
            main_dict['Outputs'][output_name] = str(o_value)

        memories = Node.objects.filter(parent=memories[0])
        for memory in memories:
            memory_name = memory.name
            memory_value = memory.value_set.all().order_by('-id')
            m_value = memory_value[0].str_data
            if not m_value:
                m_value = memory_value[0].float_data
            elif not m_value:
                m_value = memory_value[0].detail
            main_dict["Memory"][memory_name] = str(m_value)

    return render(request, 'iomem.html', {'data': main_dict})
    # Walk through all databases
    # node = client.get_objects_node()
    # return render(request, 'iomem.html', {'data': iomem(node)})

    # # Walk through all databases
    # node = client.get_objects_node()
    # main_dict_ = iomem(node)
    # client.disconnect()
    # return render(request, 'iomem.html', {'data': main_dict_})


# @login_required()
def get_certain_data(request):
    client = Client("opc.tcp://192.168.160.215:4840")
    client.connect()
    # ns = request.POST['ns']
    s = request.POST['s']
    # node = client.get_node("ns="+ns+';'+'s=\"'+s+'\"').get_variables()

    vars = {}
    for i in range(1, 6):
        node = client.get_node("ns=" + str(i) + ';' + 's=\"' + s + '\"').get_variables()

        for v in node:
            display_name = str(v.get_display_name())
            start = display_name.index('Text:') + 5
            node_name = display_name[start:-1]
            vars[node_name] = v.get_value()

    client.disconnect()
    return render(request, 'certain-data.html', {'data': vars, 's': s})


# @login_required()
def certain_data_form(request):
    return render(request, "certain-data-form.html", {})


# @login_required()
def filter_by_time(request):
    # start_date = datetime.strptime("2018-09-18 7:00:00", '%Y-%m-%d %H:%M:%S')
    # end_date = datetime.strptime("2018-09-24 12:56:00", '%Y-%m-%d %H:%M:%S')
    start_date = request.GET['startDate']
    end_date = request.GET['endDate']
    hour = start_date.split(' ')
    end_h = end_date.split(' ')
    start_date = datetime.strptime(hour[0], '%Y-%m-%d')
    end_date = datetime.strptime(end_h[0], '%Y-%m-%d')
    start = datetime.strptime(hour[1], '%H:%M')
    end = datetime.strptime(end_h[1], '%H:%M')
    start_hour = start.strftime('%H')
    end_hour = end.strftime('%H')
    start_min = start.strftime('%M')
    end_min = end.strftime('%M')
    parameter_list = []
    parameters = Value.objects.filter(Q(date__range=[start_date, end_date], date__hour__gte=start_hour,
                                      date__hour__lte=end_hour), Q(date__minute__gte=start_min) | Q(date__minute__lte=end_min))
    if parameters:
        for parameter in parameters:
            if parameter.node.important:
                date = parameter.date.strftime("%Y-%m-%d %H:%M:%S")
                value = parameter.str_data
                if not value:
                    value = parameter.float_data
                elif not value:
                    value = parameter.detail
                parameter_list.append(({'parameterName' : parameter.node.name, 'parameterValue' :value, 'parameterDate': date}))
    else:
    return JsonResponse(parameter_list, safe=False)


def filter_by_value(request):
    value = "False"
    number = 0
    dict = {}
    parameters = Value.objects.filter(Q(str_data=value) | Q(float_data=number), node__important=True)
    for parameter in parameters:
        last_value = parameter.node.value_set.all().order_by('-id')
        if last_value:
            last_value = last_value[0]
            value = last_value.str_data
            if not value:
                value = last_value.float_data
            dict[parameter.node.name] = value





