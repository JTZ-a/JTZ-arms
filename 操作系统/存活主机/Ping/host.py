# coding=utf-8
# 项目  : Python  文件: host
# @IDE : PyCharm
# @作者 : JTZ
# @时间 : 2023/4/16 15:27
# 存在问题: 多线程终止存在问题: 查看 scanner_host 输出内容
# 优化方向: 1. 设置进度条  2. 优化多线程

import platform
import socket
import os
import struct
import threading
import sys
import getopt

scanner_host = 0  # 已扫描主机个数
lock = threading.RLock()  # 锁


# 获取操作系统的类型
def get_os():
    os_category = platform.system();
    if os_category == "Windows":
        return "n"
    else:
        return "c"


# ping 主机
def ping_ip(ip_set):
    for ip_str in ip_set:
        cmd = ["ping", "-{op}".format(op=get_os()), "1", ip_str]
        output = os.popen(" ".join(cmd)).readlines()

        flag = False

        for line in list(output):
            global scanner_host
            lock.acquire()  # 加锁
            scanner_host += 1

            lock.release()  # 释放锁
            if not line:
                continue
            if str(line).upper().find("TTL") >= 0:
                flag = True
                break
        if flag:
            print("ip: %s 存活" % ip_str + " 当前扫描主机: " + str(scanner_host))
    exit()


def find_ip(ip_prefix, threads=5,):
    # 根据 CIDR 获取子网内所有 IP 地址
    (ip, cidr) = ip_prefix.split('/')  # 以 / 分割
    cidr = int(cidr)  # 获取 CIDR 数
    host_bits = 32 - cidr  # 获取子网掩码
    i = struct.unpack('>I', socket.inet_aton(ip))[0]  # note the endianness
    start = (i >> host_bits) << host_bits  # clear the host bits
    end = start | ((1 << host_bits) - 1)
    net_ip = []

    # excludes the first and last address in the subnet
    for i in range(start, end):
        net_ip.append(socket.inet_ntoa(struct.pack('>I', i)))

    print("扫描主机个数: " + str(len(net_ip)))
    # 将列表切换为五个小列表,便于使用线程启动
    n = len(net_ip) // threads
    net_child = [net_ip[i:i + n] for i in range(0, len(net_ip), n)]

    # 设置多线程启动
    thread = []
    for i in range(threads):
        print(net_child[i])
        thread.append(threading.Thread(target=ping_ip, args=(net_child[i], )))
        thread[i].start()


# 输出帮助信息
def help():
    print("**************扫描存活主机 python3***********")
    print("\t-h(--help) : 输出帮助信息")
    print("\t-i : 指定 IP 范围(只支持 CIDR)")
    print("\t-t : 指定线程树(默认为 5)")
    print('''\t命令例子:
            python3 host.py -i 10.10.10.0/24 -t 5
        tips: 如果想在后台执行可以按照下面方法
            Windows: pythonw.exe host.py -i 10.10.10.0/24 -t 5 >> host.txt
            Linux: python3 host.py -i 10.10.10.0/24 -t 5 >> host.txt &''')
    sys.exit()


def main(argv):
    ip = "127.0.0.1"
    threads = 5
    try:
        options, args = getopt.getopt(argv, "hi:t:")
    except getopt.GetoptError:
        sys.exit()
    for option, value in options:
        if option in "-h":
            help()
        if option in "-i":
            ip = value
        if option in "-t":
            threads = value
    find_ip(ip, threads)


if __name__ == '__main__':
    main(sys.argv[1:])

