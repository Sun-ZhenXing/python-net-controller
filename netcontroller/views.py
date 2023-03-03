from django.db import models
from django.http import HttpRequest, HttpResponse
from django.views import View
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .models import Network, Port, Subnet
from .serializers import (NetworkSerializer, PortSerializer, SubnetSerializer,
                          json_error, json_success)
from .utils import allocate_ip, allocate_ip_many, compute_ips, valid_cidr


@api_view(['GET'])
def index(request: HttpRequest) -> HttpResponse:
    ''' 测试接口 '''
    return json_success(request.GET, 'Hello, World!')


def basic_view_factory(model: type[models.Model], serializer: type[serializers.Serializer]):
    '''
    基础视图工厂，支持 `GET`、`POST`
    @param `model`: 模型类
    @param `serializer`: 序列化类

    视图工厂使用闭包机制复用代码
    '''

    class _C(View):
        '''
        基础视图
        '''

        def http_method_not_allowed(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
            return json_error(
                error_msg='405 METHOD_NOT_ALLOWED',
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        def get(self, request: HttpRequest):
            limit = request.GET.get('limit', None)
            offset = request.GET.get('offset', None)
            network_id = request.GET.get('network_id', None)
            subnet_id = request.GET.get('subnet_id', None)
            query = model.objects
            if model == Subnet:
                if network_id is not None:
                    query = query.filter(network_id=network_id)
            elif model == Port:
                if subnet_id is not None:
                    query = query.filter(subnet_id=subnet_id)
            if offset is None:
                offset = 0
            if limit is None:
                curr_model = query.all()[int(offset):]
            else:
                curr_model = query.values()[int(offset):int(limit)]
            ser = serializer(curr_model, many=True)
            return json_success(ser.data)

        def post(self, request: HttpRequest):
            data = JSONParser().parse(request)
            ser = serializer(data=data)
            # CIDR 验证器
            if model == Subnet:
                if not valid_cidr(data['cidr']):
                    return json_error(error_msg='Invalid CIDR')
            # Port 下分配 IP
            if model == Port:
                cidr = Subnet.objects.get(id=data['subnet_id']).cidr
                allocated_ips = (
                    x.ip for x in Port.objects.filter(subnet_id=data['subnet_id'])
                )
                ip = allocate_ip(cidr, allocated_ips)
                if not ip:
                    return json_error(error_msg='IP 地址已被分配完')
                else:
                    data['ip'] = ip
            if ser.is_valid():
                try:
                    ser.save()
                except:
                    return json_error(error_msg='数据重复或异常，不满足约束，无法创建')
                return json_success(ser.data, status=status.HTTP_201_CREATED)
            return json_error(ser.errors)

    return _C


def include_id_factory(model: type[models.Model], serializer: type[serializers.Serializer]):
    '''
    视图工厂，支持使用 ID 获取对象
    @param `model`: 模型类
    @param `serializer`: 序列化类

    视图工厂使用闭包机制复用代码
    '''

    class _C(View):
        '''
        包含 ID 的请求视图
        '''

        def _get_query_model(self, model_id: str):
            '''
            获取查询模型
            '''
            query_model = model.objects.filter(id=model_id)
            if not query_model:
                return json_error(
                    error_msg='404 NOT_FOUND',
                    status=status.HTTP_404_NOT_FOUND
                ), None
            return query_model, query_model.first()

        def get(self, request: HttpRequest, **kwargs):
            model_id = kwargs.get('uuid', None)
            query_model, curr_model = self._get_query_model(model_id)
            if curr_model is None:
                return query_model
            ser = serializer(query_model, many=True)
            # 如果是子网，还需要计算有多少可用地址
            if model == Subnet:
                occupied = (
                    port.ip for port in Port.objects.filter(subnet_id=curr_model.id)
                )
                return json_success(
                    ser.data,
                    available_ip=compute_ips(curr_model.cidr, occupied)
                )
            return json_success(ser.data)

        def put(self, request: HttpRequest, **kwargs):
            model_id = kwargs.get('uuid', None)
            query_model, curr_model = self._get_query_model(model_id)
            if curr_model is None:
                return query_model
            data = JSONParser().parse(request)
            # 子网
            if model == Subnet:
                if not valid_cidr(data['cidr']):
                    return json_error(error_msg='Invalid CIDR')
                # 如果更改了 CIDR，需要重新分配 IP
                # ========================================================
                # 注意此处需要事务一致性，修改时不可以并发写入
                # ========================================================
                if curr_model.cidr != data['cidr']:
                    occupied_number = Port.objects.filter(subnet_id=curr_model.id).count()
                    new_cird_number = compute_ips(data['cidr'], [])['available']
                    if new_cird_number < occupied_number:
                        return json_error(error_msg='无法满足 Port 的 IP 分配')
                    else:
                        ip_pool = allocate_ip_many(data['cidr'], new_cird_number)
                        # 重新分配 IP
                        for ip, port in zip(ip_pool, Port.objects.filter(subnet_id=curr_model.id)):
                            port.ip = ip
                            port.save()
            # Port
            if model == Port:
                # 当 subnet_id 改变时重新分配 IP
                if curr_model.subnet_id != data['subnet_id']:
                    cidr = Subnet.objects.get(id=data['subnet_id']).cidr
                    allocated_ips = (
                        x.ip for x in Port.objects.filter(subnet_id=data['subnet_id'])
                    )
                    ip = allocate_ip(cidr, allocated_ips)
                    if not ip:
                        return json_error(error_msg='IP 地址已被分配完')
                    else:
                        data['ip'] = ip
            ser = serializer(curr_model, data=data)
            if ser.is_valid():
                ser.save()
                return json_success(ser.data)
            return json_error(ser.errors)

        def delete(self, request: HttpRequest, **kwargs):
            model_id = kwargs.get('uuid', None)
            query_model, curr_model = self._get_query_model(model_id)
            if curr_model is None:
                return query_model
            affected_lines = curr_model.delete()[0]
            return json_success(None, affected=affected_lines)

    return _C


def global_404(request: HttpRequest, exception) -> HttpResponse:
    '''
    全局 404 页面
    '''
    return json_error(
        error_msg='404 NOT_FOUND',
        status=status.HTTP_404_NOT_FOUND
    )


def global_500(request: HttpRequest) -> HttpResponse:
    '''
    全局 500 页面
    '''
    return json_error(
        error_msg='500 INTERNAL_SERVER_ERROR',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


networks = basic_view_factory(Network, NetworkSerializer).as_view()
subnets = basic_view_factory(Subnet, SubnetSerializer).as_view()
ports = basic_view_factory(Port, PortSerializer).as_view()
network_id = include_id_factory(Network, NetworkSerializer).as_view()
subnet_id = include_id_factory(Subnet, SubnetSerializer).as_view()
port_id = include_id_factory(Port, PortSerializer).as_view()
