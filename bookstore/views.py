import os

import git
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

REPO_PATH = os.environ.get("REPO_PATH", "/home/rogeriodev81/bookstore-docker2")
WSGI_FILE = os.environ.get(
    "WSGI_FILE", "/var/www/rogeriodev81_pythonanywhere_com_wsgi.py"
)


@csrf_exempt
def update(request):
    if request.method == "POST":
        repo = git.Repo(REPO_PATH)
        origin = repo.remotes.origin
        origin.pull()
        # "toca" o arquivo WSGI: o PythonAnywhere recarrega o app sozinho
        if os.path.exists(WSGI_FILE):
            os.utime(WSGI_FILE, None)
        return HttpResponse("Código atualizado no PythonAnywhere")
    return HttpResponse("Não foi possível atualizar o código no PythonAnywhere")


def hello_world(request):
    template = loader.get_template("hello_world.html")
    return HttpResponse(template.render())
