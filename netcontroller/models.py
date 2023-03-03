import uuid

from django.db import models


class Network(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    availability_zone_hints = models.CharField(max_length=32)
    status = models.CharField(max_length=32, default='INACTIVE')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['availability_zone_hints', 'name'],
                name='zone_name_unique'
            )
        ]

    def __str__(self):
        return self.name


class Subnet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    cidr = models.CharField(max_length=64)
    network_id = models.ForeignKey(Network, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cidr', 'network_id'],
                name='cidr_network_id_unique'
            )
        ]

    def __str__(self) -> str:
        return 'Port<{}: {}>'.format(
            self.name,
            self.cidr
        )


class Port(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    mac = models.CharField(max_length=50, default=None, null=True)
    ip = models.CharField(max_length=50)
    subnet_id = models.ForeignKey(Subnet, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ip', 'subnet_id'],
                name='ip_subnet_id_unique'
            )
        ]

    def __str__(self) -> str:
        return 'Port<{}: {}>'.format(
            self.name,
            self.ip
        )
