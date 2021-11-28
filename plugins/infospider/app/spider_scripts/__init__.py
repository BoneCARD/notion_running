from importlib import import_module
from app.utility.base_world import BaseWorld

if str(__file__).count("spider_scripts") < 1 or str(__file__).count("app") < 1:
    raise Exception("infospider插件在被调用时对路径有严格要求，请不要改动该插件app和spider_scripts两个文件夹的名称")


def load_conf(_yml):
    conf_path = str(__file__)[::-1].split("spider_scripts"[::-1], 1)[1].replace("app"[::-1], "conf"[::-1], 1)[::-1]
    local_conf = BaseWorld.strip_yml(conf_path + _yml)
    return local_conf


def load_scripts():
    scripts_object = {}
    for _name in load_conf("spider_script.yml")[0]["scripts"]:
        scripts_object.update({_name: import_module("plugins.infospider.app.spider_scripts.%s" % _name).spider()})
    return scripts_object


spider_scripts = load_scripts()
