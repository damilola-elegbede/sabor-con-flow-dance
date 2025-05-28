from sabor_con_flow.wsgi import application
from asgiref.wsgi import WsgiToAsgi

app = WsgiToAsgi(application) 