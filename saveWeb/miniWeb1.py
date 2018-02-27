# 装饰器把每个客户端请求的路径名,以及对应的函数名用字典的形式存起来
url_func_dict = dict()

# 装饰器存字典用
def route(url_name):  # 装饰器的外层
    def decorate_func(func):
        url_func_dict[url_name] = func
        func()

    return decorate_func


@route('/index.html')
def index():
    with open("./saveHtml/index.html") as f:
        content = f.read()
    return content


@route('/center.html')
def center():
    with open("./saveHtml/center.html") as f:
        content = f.read()
    return content


# 定义一个执行函数.
def application(env, set_header_response):

    num = "200 ok"
    header = [("Content-Type", "text/html")]
    set_header_response(num, header)  # 把传过来的函数执行一遍,使得另一边的实例属性赋值

    path = env["url_path"]
    content = url_func_dict[path]()  # 用传过来的路径来向 字典中找相应的函数,加()是为了运行得到content

    return content  # 这里的content是未编码的,所以后续使用不用解码
