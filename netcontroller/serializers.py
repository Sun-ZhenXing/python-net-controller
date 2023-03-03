from django.http.response import JsonResponse
from rest_framework import serializers

from .models import Network, Port, Subnet


def json_success(data, error_msg='ok', status=200, **kwargs):
    '''
    将数据序列化为 JSON 格式，并返回
    @param `data`: 可序列化的对象
    @param `error_msg`: `str` 错误信息
    @return: `HttpResponse`
    '''
    res_data = {
        'code': 0,
        'msg': error_msg,
        'data': data,
        **kwargs
    }
    return JsonResponse(res_data, status=status, safe=False)


def json_error(data=None, code=1, error_msg='error', status=400, **kwargs):
    '''
    将错误信息序列化为 JSON 格式，并返回
    @param `code`: `int` 错误代码
    @param `error_msg`: `str` 错误信息
    @param `status`: `int` 状态码
    @return: `HttpResponse`
    '''
    res_data = {
        'code': code,
        'msg': error_msg,
        'data': data,
        **kwargs
    }
    return JsonResponse(res_data, status=status, safe=False)


class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = '__all__'


class SubnetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subnet
        fields = '__all__'


class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = '__all__'
