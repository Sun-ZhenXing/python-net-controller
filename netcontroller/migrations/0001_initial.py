# Generated by Django 4.0.4 on 2022-06-12 09:08

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('available_zone_hints', models.CharField(max_length=32)),
                ('status', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Subnet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('cidr', models.CharField(max_length=64)),
                ('network_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='netcontroller.network')),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('mac', models.CharField(default=None, max_length=50, null=True)),
                ('ip', models.CharField(max_length=50)),
                ('subnet_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='netcontroller.subnet')),
            ],
        ),
        migrations.AddConstraint(
            model_name='network',
            constraint=models.UniqueConstraint(fields=('available_zone_hints', 'name'), name='zone_name_unique'),
        ),
        migrations.AddConstraint(
            model_name='subnet',
            constraint=models.UniqueConstraint(fields=('cidr', 'network_id'), name='cidr_network_id_unique'),
        ),
    ]
