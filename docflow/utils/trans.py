# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 23:32:52.

@author: name

@desc: 多语言模块定义
"""
import gettext

# t = gettext.translation('spam', '/usr/share/locale')
# _ = t.gettext

gettext.install("pdf_ocr")


def _(message):
    return message
