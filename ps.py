# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 23:16:21.

@author: name

@desc: 命令封装
"""
import os
import subprocess

if os.name == "nt":
    BASH_SURFIX = ".bat"
else:
    BASH_SURFIX = ".sh"

SCRIPTS_PATH = os.path.join(".", "scripts")


def run_script(filename):
    """脚本路径调整."""
    path_ = os.path.join(SCRIPTS_PATH, filename + BASH_SURFIX)
    if os.name == "nt":
        return f"poetry run call {path_}"
    else:
        return f"poetry run sh {path_}"


def gen_code():
    """构建单吗."""
    print("gen_code")
    proc = subprocess.Popen(run_script("gen"), shell=True)
    proc.wait()


def check_code():
    """代码静态检查."""
    print("check_code")
    proc = subprocess.Popen("poetry run pre-commit run --all-files", shell=True)
    proc.wait()


def upgrade():
    """构建镜像."""
    print("upgrade")
    proc = subprocess.Popen(run_script("upgrade"), shell=True)
    proc.wait()


def upgrade_test():
    """构建镜像."""
    print("upgrade_test")
    proc = subprocess.Popen(run_script("upgrade_test"), shell=True)
    proc.wait()


def downgrade():
    """构建镜像."""
    print("downgrade")
    proc = subprocess.Popen(run_script("downgrade"), shell=True)
    proc.wait()


def downgrade_test():
    """构建镜像."""
    print("downgrade_test")
    proc = subprocess.Popen(run_script("downgrade_test"), shell=True)
    proc.wait()


def docker_build():
    """构建镜像."""
    print("docker_build")
    proc = subprocess.Popen("docker-compose build", shell=True)
    proc.wait()
