from django.db import models
from django.utils import timezone


class Database(models.Model):
    url = models.CharField(max_length=300)
    db_name = models.CharField(max_length=100)
    auth_name = models.CharField(max_length=100)
    auth_password = models.CharField(max_length=100)
    complete_url = models.CharField(max_length=500)
    active = models.BooleanField(default=False)
    next = models.BooleanField(default=False)
    updating = models.BooleanField(default=False)


class Node(models.Model):
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    node_id = models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    important = models.BooleanField(default=False)
    first = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)
    show_graph = models.BooleanField(default=False)

    bool_optimal = models.FloatField(null=True, blank=True)
    bool_optimal_required = models.BooleanField(default=True)

    lowest_optimal = models.FloatField(null=True, blank=True)
    lowest_optimal_required = models.BooleanField(default=True)

    highest_optimal = models.FloatField(null=True, blank=True)
    highest_optimal_required = models.BooleanField(default=True)

    str_optimal = models.CharField(max_length=100, null=True, blank=True)
    str_optimal_required = models.BooleanField(default=True)


class Value(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    bool_value = models.BooleanField(null=True, blank=True)
    bool_value_required = models.BooleanField(default=True)

    float_data = models.FloatField(null=True, blank=True)
    float_data_required = models.BooleanField(default=True)

    str_data = models.CharField(max_length=100, null=True, blank=True)
    str_data_required = models.BooleanField(default=True)

    detail = models.CharField(max_length=100, null=True, blank=True)
    detail_required = models.BooleanField(default=True)

    warning = models.CharField(max_length=300, null=True, blank=True)











