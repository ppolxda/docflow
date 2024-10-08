FROM minidocks/ghostscript AS builder

# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9.17-slim-bullseye

EXPOSE 20110

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1


# 更换阿里云源，加速下载
RUN printf "deb http://192.168.186.125:8081/repository/debian-bullseye/ bullseye main contrib non-free\ndeb http://192.168.186.125:8081/repository/debian-bullseye/ bullseye-updates main contrib non-free\ndeb http://192.168.186.125:8081/repository/debian-bullseye/ bullseye-backports main contrib non-free\ndeb http://192.168.186.125:8081/repository/debian-security-bullseye bullseye-security main contrib non-free" > /etc/apt/sources.list
RUN apt-get update && apt install -y gsfonts ghostscript && rm -rf /var/lib/apt/lists/*
# 替换字体，源镜像字体会导致图片无法正常显式
COPY --from=builder  /usr/share/ghostscript/Resource/CIDFSubst/DroidSansFallback.ttf /usr/share/ghostscript/9.53.3/Resource/CIDFSubst/DroidSansFallback.ttf
# RUN apt install -y libsm6 libxext6 libxrender-dev libglib2.0-0

# Install pip requirements
# COPY requirements.txt .
# RUN python -m pip install -r requirements.txt

# 环境变量
ARG PYPI_TRUSTED=192.168.186.125:8081
ARG PYPI_URL=http://192.168.186.125:8081/repository/aliyun-pypi/simple
ARG POETRY_VERSION=1.5.1
ARG REQUIREMENTS_PATH=/app/requirements.txt
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN pip config set global.index-url ${PYPI_URL}
RUN pip config set install.trusted-host ${PYPI_TRUSTED}
RUN python -m pip install --no-cache-dir pip -U
RUN python -m pip install --no-cache-dir "poetry==$POETRY_VERSION"

# 生产环境安装文件
WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock
RUN poetry export -f requirements.txt --output ${REQUIREMENTS_PATH} --without-hashes
RUN python -m pip install --no-cache-dir -r ${REQUIREMENTS_PATH}
RUN python -m pip install --no-cache-dir gunicorn pyyaml


# 安装解压工具
# RUN apt-get update && \
#     apt-get install -yq unzip

# 复制项目文件
# COPY ./depends/nltk_data /home/appuser/nltk_data
COPY ./docker/service_api/policy.xml /etc/ImageMagick-6/policy.xml
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app && chown -R appuser /home/appuser/nltk_data
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# 复制项目文件
COPY ./docflow /app/docflow
COPY ./logging.yaml /app/logging.yaml
COPY ./logging.conf /app/logging.conf
# COPY ./alembic.ini /app/alembic.ini
# RUN python -c 'from ps import init_models; init_models(); init_models()'
# RUN python -m nltk.downloader stopwords --dir=/home/appuser/nltk_data --raise_on_error
# RUN python -m nltk.downloader punkt --dir=/home/appuser/nltk_data --raise_on_error

# # NLP解压模型
# RUN unzip /home/appuser/nltk_data/corpora/stopwords.zip -d /home/appuser/nltk_data/corpora/ && \
#     unzip /home/appuser/nltk_data/corpora/wordnet.zip -d /home/appuser/nltk_data/corpora/ && \
#     unzip /home/appuser/nltk_data/tokenizers/punkt.zip -d /home/appuser/nltk_data/tokenizers/

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:20110", "-k", "uvicorn.workers.UvicornWorker", "--timeout=600", "--log-config=logging.conf", "--access-logfile=-", "--error-logfile=-", "docflow.app.main:get_app"]
# CMD ["uvicorn", "docflow.app.main:get_app", "--host=0.0.0.0", "--port=20110", "--workers=5", "--log-config=/app/logging.yaml"]

