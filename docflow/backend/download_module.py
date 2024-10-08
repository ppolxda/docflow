# -*- coding: utf-8 -*-
"""
@create: 2023-06-02 19:35:09.

@author: name

@desc: 下载缓存
"""
from functools import partial

from huggingface_hub import hf_hub_download
from timm.version import __version__

hf_hub_download = partial(
    hf_hub_download, library_name="timm", library_version=__version__
)

hf_hub_download(
    repo_id="timm/resnet18.a1_in1k", filename="model.safetensors", revision=None
)
