# Generated by Django 2.1.1 on 2018-09-27 10:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=300)),
                ('db_name', models.CharField(max_length=100)),
                ('auth_name', models.CharField(max_length=100)),
                ('auth_password', models.CharField(max_length=100)),
                ('complete_url', models.CharField(max_length=500)),
                ('active', models.BooleanField(default=False)),
                ('next', models.BooleanField(default=False)),
                ('updating', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_id', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=100)),
                ('important', models.BooleanField(default=False)),
                ('first', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('show_graph', models.BooleanField(default=False)),
                ('lowest_optimal', models.FloatField(blank=True, null=True)),
                ('lowest_optimal_required', models.BooleanField(default=True)),
                ('highest_optimal', models.FloatField(blank=True, null=True)),
                ('highest_optimal_required', models.BooleanField(default=True)),
                ('str_optimal', models.CharField(blank=True, max_length=100, null=True)),
                ('str_optimal_required', models.BooleanField(default=True)),
                ('database', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ParameterManager.Database')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ParameterManager.Node')),
            ],
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('float_data', models.FloatField(blank=True, null=True)),
                ('float_data_required', models.BooleanField(default=True)),
                ('str_data', models.CharField(blank=True, max_length=100, null=True)),
                ('str_data_required', models.BooleanField(default=True)),
                ('detail', models.CharField(blank=True, max_length=100, null=True)),
                ('detail_required', models.BooleanField(default=True)),
                ('warning', models.CharField(blank=True, max_length=300, null=True)),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ParameterManager.Node')),
            ],
        ),
    ]
