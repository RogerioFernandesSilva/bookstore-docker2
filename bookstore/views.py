from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import git


@csrf_exempt
def update(request):
    if request.method == "POST":
        repo = git.Repo('/home/rogeriodev81/bookstore-docker2')
        origin = repo.remotes.origin
        origin.pull()
        return HttpResponse("Código atualizado no PythonAnywhere")
    else:
        return HttpResponse("Não foi possível atualizar o código no PythonAnywhere")


def hello_world(request):
    template = loader.get_template('hello_world.html')
    return HttpResponse(template.render())