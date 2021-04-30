import typer
import re
import urllib
from .utils import repo, Conf
from .dialog import conf_dialog
from prompt_toolkit import print_formatted_text, HTML
import requests

app = typer.Typer(help='Interact with gitlab by accessing gitlab-api')
conf = Conf()


# @app.command()
def config():
    """ configuration for accessing gitlab-api\n
    host : gitlab host info.  example: https://gitlab.com\n
    version : gitlab api version.  example: [v1 | v2 | v3 | v4]\n
    token : gitlab private token. example: 679Pqw11v739pqfy2jRg
    """
    try:
        conf.host, conf.version, conf.token = conf_dialog(host=conf.host, version=conf.version, token=conf.token)
    except TypeError:
        typer.Abort()


@app.command(name='mr')
def merge_request(all: bool = typer.Option(False, '--all', '-a', help='Submit merge request to the submodules of the repository')):
    send_merge_request(repo)
    if all:
        for submodule in repo.submodules:
            sub_repo = submodule.module()
            send_merge_request(sub_repo)


def send_merge_request(repo):
    headers = {"Private-Token": Conf().token}
    # get project id
    remote = repo.remote()
    # todo 多个远端仓库
    url = next(remote.urls)
    host, project_name = re.match('.*@(.*):(.*).git', url).groups()
    parsed_name = urllib.parse.quote(project_name, 'utf-8')
    conf = Conf()
    headers = {"Private-Token": conf.token}
    resp = requests.get(f'https://{host}/api/{conf.version}/projects/{parsed_name}', headers=headers)
    pid = resp.json().get('id')

    # send merge request
    url = f'https://{host}/api/{conf.version}/projects/{pid}/merge_requests'
    data = {
        'source_branch': repo.head.reference.name,
        'target_branch': 'master',
        'title': f'Merge [{repo.head.reference.name}] to [master]'
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.ok:
        print_formatted_text(HTML(f'Merge request: {project_name} <b><style fg="ansigreen">Sucess</style></b>'))
    else:
        print_formatted_text(HTML(f'Merge request: {project_name} <b><style fg="ansired">Fail</style></b>'))
        typer.echo(resp.content)


@app.callback()
def check_config(verbose: bool = False):
    """
    Manage users in the awesome CLI app.
    """
    if conf.token == 'example_token':
        typer.echo('Need gitlab configuration !')
        config()















