#coding:utf-8
# 导入包
import socket
import re
import multiprocessing
# import saveWeb.miniWeb1
import sys


# 创建个类来定义web服务器


class ServerWeb(object):
    # 定义init函数用来创建套接字等固定属性
    def __init__(self, app):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建套接字
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 释放被占用的端口
        self.server_socket.bind(('', 80))  # 绑定端口信息
        self.server_socket.listen(10000)  # 监听的客户端最大的数量为10000
        self.app = app

    # 创建一个处理客户端请求的函数
    def handel_request(self, client_socket):

        # 尝试接收数据,如果没接收到用户数据就报错
        try:
            request_header_data = client_socket.recv(1024)  # 接收的数据解码

        except Exception as f:
            print('客户端没有发送任何请求,请求关闭连接')
            return
        # 如果有数据则尝试正则匹配处url的名字
        if request_header_data:
            url_data = re.match('[^/]+(/[^ ]*)', request_header_data.decode('utf-8'))  # 正则匹配出url

            if url_data:
                url_name = url_data.group(1)
                if url_name == "/":
                    url_name = "/index.html"
        else:
            header_response = "HTTP/1.1 404 not found\r\n"
            header_response += "\r\n"
            header_body = "页面不存在..."

            response = header_response + header_body
            client_socket.send(response.encode('utf-8'))
            print('没有接收到任何数据')
            client_socket.close()  # 关闭客户端
            return
            # 判断是否静态网页,如果是则正常打开,否则进入下一步
        if not url_name.endswith('.html'):

            try:
                with open(url_name, 'rb') as f:
                    content = f.read()

            except Exception as e:
                header_response = "HTTP/1.1 404 not found\r\n"
                header_response += "Content-type:text/html;charset=utf-8\r\n"
                header_response += ""
                header_response += "\r\n"

                body_response = "请求的页面不存在..."
                response = header_response + body_response

                client_socket.send(response.encode('utf-8'))

            else:

                header_response = "HTTP/1.1 200 OK\r\n"
                header_response += "\r\n"

                body_response = content

                client_socket.send(header_response.encode('utf-8'))
                client_socket.send(body_response)

            client_socket.close()

        else:
            env = dict()
            env['url_path'] = url_name  # 建立字典,把路径名传递过去

            body_response = self.app(env, self.set_header_response)  # 导入的包中传如字典还有header头的函数,返回所需的值

            header_response = self.header_response  # 经过导入包时候的运行过程,已经把header运行了一遍,返回的参数回来了

            # 发送header以及body给客户端,完成页面显示
            client_socket.send(header_response.encode('utf-8'))
            client_socket.send(body_response.encode('utf-8'))

            client_socket.close()  # 关闭套接字

    # 创建多线程,用来完成多个客户端的请求并应答,所以做成循环
    def handel_forver(self):

        while True:
            client_socket, addre_socket = self.server_socket.accept()
            mul_handel = multiprocessing.Process(target=self.handel_request, args=(client_socket,))
            mul_handel.start()

            client_socket.close()  # 记得关闭套接字,因为主进程创建了一个,子进程也复制了一个,必须先关闭一个,不然网页会异常
        self.server_socket.close()

    # 创建一个函数用来处理henderson头信息
    def set_header_response(self, num, header):
        num_in = num
        header_in = header

        self.header_response = "HTTP/1.1 %s \r\n" % num_in

        for temp in header_in:
            self.header_response += "%s:%s\r\n" % (temp[0], temp[1])

        self.header_response += "\r\n"

def main():

    if len(sys.argv) != 2:
        print('请按照正确的运行方式运行程序...')
    else:
        web = re.match(r"(.*):(.*)", sys.argv[1])
        mudle = web.group(1)
        print(mudle)
        func = web.group(2)
        print(func)
    with open("searchPath.conf") as f:
        path_dict = eval(f.read())
        sys.path.append(path_dict["search_path"])

        print(path_dict["search_path"])

        web = __import__(mudle)
        app = getattr(web, func)

    run = ServerWeb(app)
    run.handel_forver()

if __name__ == '__main__':
    main()
