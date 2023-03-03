import ipaddress
from typing import Iterable


def allocate_ip(cidr: str, allocated_ips: Iterable[str]):
    '''
    通过 CIDR 分配 IP 地址
    '''
    allocated_ips_set = set(allocated_ips)
    ip_network = ipaddress.ip_network(cidr)
    for ip in ip_network.hosts():
        if ip.compressed not in allocated_ips_set:
            return ip.compressed
    return ''


def allocate_ip_many(cidr: str, n: int) -> Iterable[str]:
    '''
    通过 CIDR 分配多个 IP 地址
    '''
    ip_network = ipaddress.ip_network(cidr)
    return (
        (ip_network.network_address + x).compressed
        for x in range(1, n + 1)
    )


def compute_ips(cidr: str, occupied: Iterable[str]):
    '''
    计算子网可用信息
    '''
    ip_network = ipaddress.ip_network(cidr)
    total = ip_network.num_addresses
    occupied_set = set(occupied)
    # 不包括广播地址和网络地址
    available = total - len(occupied_set) - 2
    ips = list[dict[str, str]]()
    flag = False
    start = ''
    for x in range(1, total + 1):
        curr = ip_network.network_address + x
        if curr.compressed not in occupied_set:
            if not flag:
                start = curr.compressed
                flag = True
        else:
            if flag:
                ips.append({
                    'start': start,
                    'end': (curr - 1).compressed
                })
                flag = False
    if flag:
        ips.append({
            'start': start,
            'end': (ip_network.broadcast_address - 1).compressed
        })
    return {
        'total': total,
        'available': available,
        'ips': ips,
        'netmask': ip_network.netmask.compressed
    }


def valid_cidr(cidr: str) -> bool:
    '''
    检查 CIDR 是否合法
    '''
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return bool(network)
    except ValueError:
        return False


def valid_ip(ip: str) -> bool:
    '''
    检查 IP 是否合法
    '''
    try:
        ip_address = ipaddress.ip_address(ip)
        return bool(ip_address)
    except ValueError:
        return False
