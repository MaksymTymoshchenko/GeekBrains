from pprint import pprint

from gungner.requestor import Requestor


class Gungner:

    def __init__(self, urlpatterns: dict, front_controllers: list):
        self.urlpatterns = urlpatterns
        self.front_controllers = front_controllers

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']

        if path.endswith('/') and len(path) > 1:
            path = path.rstrip("/")

        if path in self.urlpatterns:
            view = self.urlpatterns[path]
        else:
            view = PageNotFound()

        request = Requestor().get_request_params(environ)
        for front_controller in self.front_controllers:
            front_controller(request)
            
        code, response = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [response.encode('utf-8')]
class PageNotFound:
    def __call__(self, request):
        return '404 NOT_FOUND', 'Requested page does not found!'

class DebugGungner(Gungner):
    """
    Такой же как основной, только он для каждого запроса 
    выводит информацию (тип запроса и параметры) в консоль
    """
    def __init__(self, urlpatterns: dict, front_controllers: list):
        self.application = Gungner(urlpatterns, front_controllers)
        super().__init__(urlpatterns, front_controllers)

    def __call__(self, environ, start_response):
        print('DEBUG_MODE')
        pprint(environ)
        return self.application(environ, start_response)

class FakeGungner(Gungner):
    """
    На все запросы пользователя отвечает “200 OK”, “Hello from Fake”
    """
    def __init__(self, urlpatterns: dict, front_controllers: list):
        self.application = Gungner(urlpatterns, front_controllers)
        super().__init__(urlpatterns, front_controllers)

    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello from Fake']
        