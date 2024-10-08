# For more information, please refer to https://aka.ms/vscode-docker-python
FROM cnstark/pytorch:1.12.1-py3.9.12-cuda11.6.2-ubuntu20.04

# EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 更换阿里云源，加速下载
RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN sed -i 's/security.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 && rm -rf /var/lib/apt/lists/*
# RUN apt-get update && apt install -y tesseract-ocr imagemagick python3-opencv
# RUN apt install -y libsm6 libxext6 libxrender-dev libglib2.0-0

# Install pip requirements
# COPY requirements.txt .
# RUN python -m pip install -r requirements.txt

# 环境变量
# ARG PYPI_TRUSTED=mirrors.aliyun.com
# ARG PYPI_URL=https://mirrors.aliyun.com/pypi/simple
ARG PYPI_TRUSTED=192.168.186.125:8081
ARG PYPI_URL=http://192.168.186.125:8081/repository/aliyun-pypi/simple
ARG POETRY_VERSION=1.5.1
ARG REQUIREMENTS_PATH=/app/requirements.txt
ARG AWS_ACCESS_KEY_ID=minioadmin
ARG AWS_SECRET_ACCESS_KEY=minioadmin
ARG MLFLOW_TRACKING_URI=http://127.0.0.1/mlflow
ARG MLFLOW_S3_ENDPOINT_URL=http://127.0.0.1:9000
ARG MLFLOW_ARTIFACT_URI_PDFCLASS_BERT="models:/pdfclassificationBert/7"
ARG MLFLOW_ARTIFACT_URI_PDFCLASS="models:/pdfclassification/1"
ARG MLFLOW_ARTIFACT_URI_KEYINFO="models:/keyinfo/4"
ARG MLFLOW_ARTIFACT_URI_PDFSIDE="models:/pdfside/1"
ARG MLFLOW_ARTIFACT_URI_TABLE_STRUCTURE="models:/tabletransformer_structure/1"
ARG MLFLOW_ARTIFACT_URI_TABLE_DETECTION="models:/tabletransformer_detection/1"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ENV KEYINFO_MODULE="/app/modules/keyinfo"
ENV PDFCLASS_MODULE="/app/modules/pdfclassification"
ENV PDFCLASS_BERT_MODULE="/app/modules/pdfbertclassification"
ENV PDFSIDE_MODULE="/app/modules/pdfside"
ENV TABLE_STRUCTURE_MODULE="/app/modules/tabletransformer_structure"
ENV TABLE_DETECTION_MODULE="/app/modules/tabletransformer_detection"
ENV TIMM_USE_OLD_CACHE="1"

RUN pip config set global.index-url ${PYPI_URL}
RUN pip config set install.trusted-host ${PYPI_TRUSTED}
RUN python -m pip install --no-cache-dir pip -U
RUN python -m pip install --no-cache-dir "poetry==$POETRY_VERSION"

# 生产环境安装文件
WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock
RUN poetry export -f requirements.txt --output req.txt --without-hashes --with=predict --without=cpu
RUN grep -v 'torch' req.txt > ${REQUIREMENTS_PATH}
RUN python -m pip install --no-cache-dir -r ${REQUIREMENTS_PATH}
RUN python -m pip install --no-cache-dir gunicorn

RUN mlflow artifacts download --artifact-uri ${MLFLOW_ARTIFACT_URI_PDFCLASS_BERT} --dst-path ${PDFCLASS_BERT_MODULE}
RUN mlflow artifacts download --artifact-uri ${MLFLOW_ARTIFACT_URI_PDFCLASS} --dst-path ${PDFCLASS_MODULE}
RUN mlflow artifacts download --artifact-uri ${MLFLOW_ARTIFACT_URI_KEYINFO} --dst-path ${KEYINFO_MODULE}
RUN mlflow artifacts download --artifact-uri ${MLFLOW_ARTIFACT_URI_PDFSIDE} --dst-path ${PDFSIDE_MODULE}
RUN mlflow artifacts download --artifact-uri ${MLFLOW_ARTIFACT_URI_TABLE_STRUCTURE} --dst-path ${TABLE_STRUCTURE_MODULE}
RUN mlflow artifacts download --artifact-uri ${MLFLOW_ARTIFACT_URI_TABLE_DETECTION} --dst-path ${TABLE_DETECTION_MODULE}

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app && chown -R appuser /home/appuser/.cache
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# 复制项目文件
COPY ./docker/service_backend/backend /app/backend
COPY ./logging.yaml /app/logging.yaml
COPY ./logging.conf /app/logging.conf

# 下载依赖模型，可能会服务下载成功
RUN mkdir -p /home/appuser/.cache/huggingface/hub
COPY ./docker/module/timm.resnet18.a1_in1k /home/appuser/.cache/huggingface/hub/models--timm--resnet18.a1_in1k

# RUN python -c 'from ps import init_models; init_models(); init_models()'
# RUN python -m nltk.downloader stopwords --dir=/home/appuser/nltk_data --raise_on_error
# RUN python -m nltk.downloader punkt --dir=/home/appuser/nltk_data --raise_on_error

# # NLP解压模型
# RUN unzip /home/appuser/nltk_data/corpora/stopwords.zip -d /home/appuser/nltk_data/corpora/ && \
#     unzip /home/appuser/nltk_data/corpora/wordnet.zip -d /home/appuser/nltk_data/corpora/ && \
#     unzip /home/appuser/nltk_data/tokenizers/punkt.zip -d /home/appuser/nltk_data/tokenizers/

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
WORKDIR /app
CMD ["python3", "-m", "backend.worker.main"]
