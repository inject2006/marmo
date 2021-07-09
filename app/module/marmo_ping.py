# -*- coding:UTF-8 -*-

import os
import struct
import time
import socket
import select
from app.utils.marmo_logger import Marmo_Logger
logger =Marmo_Logger()

class MarmoPing():
    def __init__(self):
        pass
    def checksum(self,data):
        '''
        计算icmp报文校验和
        :param data: icmp报文
        :return checksum: 报文校验和
        '''
        n = len(data)
        m = n % 2
        sum = 0
        for i in range(0, n - m, 2):
            # 传入data以每两个字节（十六进制）通过ord转十进制，第一字节在低位，第二个字节在高位
            sum += (data[i]) + ((data[i + 1]) << 8)
        if m:
            sum += (data[-1])
        # 将高于16位与低16位相加
        sum = (sum >> 16) + (sum & 0xffff)
        sum += (sum >> 16)  # 如果还有高于16位，将继续与低16位相加
        answer = ~sum & 0xffff
        #  主机字节序转网络字节序列（参考小端序转大端序）
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer


    def request_ping(self,data_Sequence):
        '''
        创建request ping报文
        :param data_Sequence:
        :return icmp_packet:
        '''
        data_type = 8
        data_code = 0
        data_checksum = 0
        data_ID = os.getpid() & 0xffff
        payload_body = time.time()
        #  把字节打包成二进制数据，其中>（！）代表是是大端模式，B代表的是一个字节的无符号整数，H代表的是两个字节的无符号整数，d代表的是double
        imcp_packet = struct.pack('>BBHHHd', data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body)
        icmp_chesksum = self.checksum(imcp_packet)  # 获取校验和
        #  把校验和传入，再次打包
        imcp_packet = struct.pack('>BBHHHd', data_type, data_code, icmp_chesksum, data_ID, data_Sequence, payload_body)
        return imcp_packet


    def send_once(self,dst_addr, imcp_packet):
        '''
        连接套接字,并将数据发送到套接字
        :param dst_addr: 目标主机地址
        :param imcp_packet: icmp报文
        :return rawsocket: rawsocket对象
        :return dst_addr: 目标主机地址
        '''
        # 实例化一个socket对象，ipv4，原套接字，分配协议端口
        rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        # 发送数据到网络
        rawsocket.sendto(imcp_packet, (dst_addr, 80))
        # 返回数据
        return rawsocket, dst_addr


    def reply_ping(self,rawsocket, timeout=1):
        '''
        接收icmp报文
        :param rawsocket:
        :param timeout:
        :return ttl: 往返时间
        :return sequence: 报文序列号
        '''
        while True:
            # 开始时间
            started_selected = time.time()
            # 实例化select对象，可读rawsocket，可写为空，可执行为空，超时时间
            what_ready = select.select([rawsocket], [], [], timeout)
            # 等待时间
            wait_for_time = (time.time() - started_selected)
            # 如果没有返回可写内容判断为超时
            if what_ready[0] == []:
                return -1, -1
            # 记录接收时间
            time_received = time.time()
            # 设置接收的包的字节为1024字节
            received_packet, addr = rawsocket.recvfrom(1024)
            # 判断是否超时
            timeout = timeout - wait_for_time
            if timeout <= 0:
                return -1, -1
            # 获取icmp报文的头部
            icmpHeader = received_packet[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack(">BBHHH", icmpHeader)
            # 获取报文中的内容
            send_time = struct.unpack(">d", received_packet[28:36])
            if type == 0:
                return time_received - send_time[0], sequence


    def ping(self,host, count=4, timeout=100):
        '''
        ping host with count times and the timeout
        :param host: 目标主机地址
        :param count: 报文数量
        :param timeout: 最大延迟秒数
        :return:
        '''
        dst_addr = socket.gethostbyname(host)  # ipv4地址

        logger.log("正在 Ping {0} [{1}] 具有 32 字节的数据:".format(host, dst_addr))
        lost = 0
        accept = 0
        sumtime = 0.0
        times = []  # 统计所有包的往返时间长度
        for i in range(count):
            i += 1
            icmp_packet = self.request_ping(i)
            # print(icmp_packet)
            rowsocket, dst_addr = self.send_once(dst_addr, icmp_packet)
            ttl, sequence = self.reply_ping(rowsocket, timeout)
            if ttl < 0:
                print("请求超时")
                lost += 1
                times.append(timeout * 1000)
            else:
                ttl = ttl * 1000
                print("来自 {0} 的回复: 字节=32 seq = {1} 时间={2:.2f}ms".format(dst_addr, sequence, ttl))
                accept += 1
                sumtime += ttl
                times.append(ttl)
        #统计
        print('数据包: 已发送 = {0}，已接收 = {1}，丢失 = {2} ({3}% 丢失)，\n\
    往返行程的估计时间(以毫秒为单位):最短 = {4:.2f}ms，最长 = {5:.2f}ms，平均 = {6:.2f}ms'.format(
            count, accept, lost, lost // (lost + accept) * 100, min(times),
            max(times), sum(times) // (lost + accept)
        ))
        return dst_addr

if __name__ =="__main__":
    marmo_ping = MarmoPing()
    marmo_ping.ping("www.baidu.com")