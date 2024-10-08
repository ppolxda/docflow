# -*- coding: utf-8 -*-
"""
Gen enum.

@author: test

@desc: enum files
"""

from enum import Enum


class EnumByteIsEnable(object):
    """EnumByteIsEnable."""

    EBIE_DISABLE = b"\x00"
    EBIE_ENABLE = b"\x01"

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.EBIE_DISABLE,
            cls.EBIE_ENABLE,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)


class TransEnum(Enum):
    """TransEnum."""

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        raise NotImplementedError

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        raise NotImplementedError


class EnumIsEnableType(str, TransEnum):
    """EnumIsEnableType."""  # noqa

    IES_DISBALE = "IES_DISBALE"  # 禁用
    IES_ENABLE = "IES_ENABLE"  # 启用

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.IES_ENABLE,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumIsEnableType.IES_DISBALE: "禁用",
            EnumIsEnableType.IES_ENABLE: "启用",
        }[val]


class EnumProjectGroupType(str, TransEnum):
    """EnumProjectGroupType."""  # noqa

    PGT_PROJECT = "PGT_PROJECT"  # 项目
    PGT_DATASET = "PGT_DATASET"  # 数据集

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.PGT_DATASET,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumProjectGroupType.PGT_PROJECT: "项目",
            EnumProjectGroupType.PGT_DATASET: "数据集",
        }[val]


class EnumSexType(str, TransEnum):
    """EnumSexType."""  # noqa

    ST_NULL = "ST_NULL"  # 无效
    ST_MALE = "ST_MALE"  # 男
    ST_FEMALE = "ST_FEMALE"  # 女
    ST_OTHER = "ST_OTHER"  # 其他

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.ST_MALE,
            cls.ST_FEMALE,
            cls.ST_OTHER,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumSexType.ST_NULL: "无效",
            EnumSexType.ST_MALE: "男",
            EnumSexType.ST_FEMALE: "女",
            EnumSexType.ST_OTHER: "其他",
        }[val]


class EnumSettingLabelType(str, TransEnum):
    """EnumSettingLabelType."""  # noqa

    SLT_NULL = "SLT_NULL"  # 未设置
    SLT_ROUNDS = "SLT_ROUNDS"  # 轮次设置 - 配置是否重新执行一次全部文件
    SLT_GROUP_LIMIT = "SLT_GROUP_LIMIT"  # 文件分组数量

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.SLT_ROUNDS,
            cls.SLT_GROUP_LIMIT,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumSettingLabelType.SLT_NULL: "未设置",
            EnumSettingLabelType.SLT_ROUNDS: "轮次设置 - 配置是否重新执行一次全部文件",
            EnumSettingLabelType.SLT_GROUP_LIMIT: "文件分组数量",
        }[val]


class EnumProcessStatus(str, TransEnum):
    """EnumProcessStatus."""  # noqa

    PS_NULL = "PS_NULL"  # 未设置
    PS_WAITING = "PS_WAITING"  # 待处理
    PS_DOING = "PS_DOING"  # 处理中
    PS_PASSED = "PS_PASSED"  # 已处理
    PS_FAILED = "PS_FAILED"  # 已失败
    PS_CHECKED = "PS_CHECKED"  # 已确认

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.PS_WAITING,
            cls.PS_DOING,
            cls.PS_PASSED,
            cls.PS_FAILED,
            cls.PS_CHECKED,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumProcessStatus.PS_NULL: "未设置",
            EnumProcessStatus.PS_WAITING: "待处理",
            EnumProcessStatus.PS_DOING: "处理中",
            EnumProcessStatus.PS_PASSED: "已处理",
            EnumProcessStatus.PS_FAILED: "已失败",
            EnumProcessStatus.PS_CHECKED: "已确认",
        }[val]


class EnumReviewType(str, TransEnum):
    """EnumReviewType."""  # noqa

    RT_NULL = "RT_NULL"  # 未设置
    RT_DOING = "RT_DOING"  # 处理中
    RT_WAITING = "RT_WAITING"  # 待审核
    RT_PASSED = "RT_PASSED"  # 已处理
    RT_REJECT = "RT_REJECT"  # 已拒绝

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.RT_DOING,
            cls.RT_WAITING,
            cls.RT_PASSED,
            cls.RT_REJECT,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumReviewType.RT_NULL: "未设置",
            EnumReviewType.RT_DOING: "处理中",
            EnumReviewType.RT_WAITING: "待审核",
            EnumReviewType.RT_PASSED: "已处理",
            EnumReviewType.RT_REJECT: "已拒绝",
        }[val]


class EnumExportDatasetsType(str, TransEnum):
    """EnumExportDatasetsType."""  # noqa

    EX_NULL = "EX_NULL"  # 默认
    EX_TABLE = "EX_TABLE"  # 表格
    EX_DOCUMENT = "EX_DOCUMENT"  # 文档
    EX_CLASSIFICATION = "EX_CLASSIFICATION"  # 分类

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.EX_TABLE,
            cls.EX_DOCUMENT,
            cls.EX_CLASSIFICATION,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumExportDatasetsType.EX_NULL: "默认",
            EnumExportDatasetsType.EX_TABLE: "表格",
            EnumExportDatasetsType.EX_DOCUMENT: "文档",
            EnumExportDatasetsType.EX_CLASSIFICATION: "分类",
        }[val]


class EnumLabelFieldType(str, TransEnum):
    """EnumLabelFieldType."""  # noqa

    LFT_NULL = "LFT_NULL"  # 未设置
    LFT_STRING = "LFT_STRING"  # 字符串
    LFT_INT = "LFT_INT"  # 整型数
    LFT_FLOAT = "LFT_FLOAT"  # 浮点数
    LFT_DATE = "LFT_DATE"  # 日期
    LFT_DATETIME = "LFT_DATETIME"  # 时间
    LFT_ENUM = "LFT_ENUM"  # 枚举
    LFT_CUSTOM = "LFT_CUSTOM"  # 自定义

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.LFT_STRING,
            cls.LFT_INT,
            cls.LFT_FLOAT,
            cls.LFT_DATE,
            cls.LFT_DATETIME,
            cls.LFT_ENUM,
            cls.LFT_CUSTOM,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumLabelFieldType.LFT_NULL: "未设置",
            EnumLabelFieldType.LFT_STRING: "字符串",
            EnumLabelFieldType.LFT_INT: "整型数",
            EnumLabelFieldType.LFT_FLOAT: "浮点数",
            EnumLabelFieldType.LFT_DATE: "日期",
            EnumLabelFieldType.LFT_DATETIME: "时间",
            EnumLabelFieldType.LFT_ENUM: "枚举",
            EnumLabelFieldType.LFT_CUSTOM: "自定义",
        }[val]


class EnumLabelDisplayType(str, TransEnum):
    """EnumLabelDisplayType."""  # noqa

    LDT_NULL = "LDT_NULL"  # 未设置
    LDT_DATE_EU = "LDT_DATE_EU"  # EU日期类型(dd/mm/yyyy)
    LDT_DATE_ISO = "LDT_DATE_ISO"  # ISO日期类型(yyyy-mm-dd)
    LDT_DATE_US = "LDT_DATE_US"  # US日期类型(mm/dd/yyyy)
    LDT_DATE_CN = "LDT_DATE_CN"  # US日期类型(yyyy年mm月dd日)
    LDT_DATETIME_EU = "LDT_DATETIME_EU"  # EU时间类型(dd/mm/yyyy hh:MM:SS)
    LDT_DATETIME_ISO = "LDT_DATETIME_ISO"  # ISO时间类型(yyyy-mm-dd hh:MM:SS)
    LDT_DATETIME_US = "LDT_DATETIME_US"  # US时间类型(mm/dd/yyyy hh:MM:SS)
    LDT_DATETIME_CN = "LDT_DATETIME_CN"  # US日期类型(yyyy年mm月dd日 hh时MM分ss秒)
    LDT_STRING_UPPER_CASE = "LDT_STRING_UPPER_CASE"  # 全英文大写
    LDT_STRING_LOWER_CASE = "LDT_STRING_LOWER_CASE"  # 全英文小写
    LDT_STRING_TITLE_CASE = "LDT_STRING_TITLE_CASE"  # 首字母大写

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.LDT_DATE_EU,
            cls.LDT_DATE_ISO,
            cls.LDT_DATE_US,
            cls.LDT_DATE_CN,
            cls.LDT_DATETIME_EU,
            cls.LDT_DATETIME_ISO,
            cls.LDT_DATETIME_US,
            cls.LDT_DATETIME_CN,
            cls.LDT_STRING_UPPER_CASE,
            cls.LDT_STRING_LOWER_CASE,
            cls.LDT_STRING_TITLE_CASE,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumLabelDisplayType.LDT_NULL: "未设置",
            EnumLabelDisplayType.LDT_DATE_EU: "EU日期类型(dd/mm/yyyy)",
            EnumLabelDisplayType.LDT_DATE_ISO: "ISO日期类型(yyyy-mm-dd)",
            EnumLabelDisplayType.LDT_DATE_US: "US日期类型(mm/dd/yyyy)",
            EnumLabelDisplayType.LDT_DATE_CN: "US日期类型(yyyy年mm月dd日)",
            EnumLabelDisplayType.LDT_DATETIME_EU: "EU时间类型(dd/mm/yyyy hh:MM:SS)",
            EnumLabelDisplayType.LDT_DATETIME_ISO: "ISO时间类型(yyyy-mm-dd hh:MM:SS)",
            EnumLabelDisplayType.LDT_DATETIME_US: "US时间类型(mm/dd/yyyy hh:MM:SS)",
            EnumLabelDisplayType.LDT_DATETIME_CN: "US日期类型(yyyy年mm月dd日 hh时MM分ss秒)",
            EnumLabelDisplayType.LDT_STRING_UPPER_CASE: "全英文大写",
            EnumLabelDisplayType.LDT_STRING_LOWER_CASE: "全英文小写",
            EnumLabelDisplayType.LDT_STRING_TITLE_CASE: "首字母大写",
        }[val]


class EnumEsIndexType(str, TransEnum):
    """EnumEsIndexType."""  # noqa

    IDX_NULL = "IDX_NULL"  # 未设置
    IDX_VET = "IDX_VET"  # 兽医官签名

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.IDX_VET,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumEsIndexType.IDX_NULL: "未设置",
            EnumEsIndexType.IDX_VET: "兽医官签名",
        }[val]


class EnumLabelDateType(str, TransEnum):
    """EnumLabelDateType."""  # noqa

    LDDT_NULL = "LDDT_NULL"  # 未设置
    LDDT_DATE_EU = "LDDT_DATE_EU"  # EU日期类型(dd/mm/yyyy)
    LDDT_DATE_ISO = "LDDT_DATE_ISO"  # ISO日期类型(yyyy-mm-dd)
    LDDT_DATE_US = "LDDT_DATE_US"  # US日期类型(mm/dd/yyyy)
    LDDT_DATE_CN = "LDDT_DATE_CN"  # US日期类型(yyyy年mm月dd日)
    LDDT_DATETIME_EU = "LDDT_DATETIME_EU"  # EU时间类型(dd/mm/yyyy hh:MM:SS)
    LDDT_DATETIME_ISO = "LDDT_DATETIME_ISO"  # ISO时间类型(yyyy-mm-dd hh:MM:SS)
    LDDT_DATETIME_US = "LDDT_DATETIME_US"  # US时间类型(mm/dd/yyyy hh:MM:SS)
    LDDT_DATETIME_CN = "LDDT_DATETIME_CN"  # US日期类型(yyyy年mm月dd日 hh时MM分ss秒)

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.LDDT_DATE_EU,
            cls.LDDT_DATE_ISO,
            cls.LDDT_DATE_US,
            cls.LDDT_DATE_CN,
            cls.LDDT_DATETIME_EU,
            cls.LDDT_DATETIME_ISO,
            cls.LDDT_DATETIME_US,
            cls.LDDT_DATETIME_CN,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumLabelDateType.LDDT_NULL: "未设置",
            EnumLabelDateType.LDDT_DATE_EU: "EU日期类型(dd/mm/yyyy)",
            EnumLabelDateType.LDDT_DATE_ISO: "ISO日期类型(yyyy-mm-dd)",
            EnumLabelDateType.LDDT_DATE_US: "US日期类型(mm/dd/yyyy)",
            EnumLabelDateType.LDDT_DATE_CN: "US日期类型(yyyy年mm月dd日)",
            EnumLabelDateType.LDDT_DATETIME_EU: "EU时间类型(dd/mm/yyyy hh:MM:SS)",
            EnumLabelDateType.LDDT_DATETIME_ISO: "ISO时间类型(yyyy-mm-dd hh:MM:SS)",
            EnumLabelDateType.LDDT_DATETIME_US: "US时间类型(mm/dd/yyyy hh:MM:SS)",
            EnumLabelDateType.LDDT_DATETIME_CN: "US日期类型(yyyy年mm月dd日 hh时MM分ss秒)",
        }[val]


class EnumLabelPostChangeCaseType(str, TransEnum):
    """EnumLabelPostChangeCaseType."""  # noqa

    LPTCC_NULL = "LPTCC_NULL"  # 未设置
    LPTCC_UPPER_CASE = "LPTCC_UPPER_CASE"  # 全英文大写
    LPTCC_LOWER_CASE = "LPTCC_LOWER_CASE"  # 全英文小写
    LPTCC_TITLE_CASE = "LPTCC_TITLE_CASE"  # 首字母大写

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.LPTCC_UPPER_CASE,
            cls.LPTCC_LOWER_CASE,
            cls.LPTCC_TITLE_CASE,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumLabelPostChangeCaseType.LPTCC_NULL: "未设置",
            EnumLabelPostChangeCaseType.LPTCC_UPPER_CASE: "全英文大写",
            EnumLabelPostChangeCaseType.LPTCC_LOWER_CASE: "全英文小写",
            EnumLabelPostChangeCaseType.LPTCC_TITLE_CASE: "首字母大写",
        }[val]


class EnumLabelPostType(str, TransEnum):
    """EnumLabelPostType."""  # noqa

    LPT_NULL = "LPT_NULL"  # 未设置
    LPT_CHANGE_CASE = "LPT_CHANGE_CASE"  # 文本格式化
    LPT_CLOSEST_MATCH = "LPT_CLOSEST_MATCH"  # 选择性匹配
    LPT_REGIX = "LPT_REGIX"  # 文本内容匹配
    LPT_CONCATENATE = "LPT_CONCATENATE"  # 组合多个同类标签
    LPT_TO_ASCII = "LPT_TO_ASCII"  # 转换为ASCII格式
    LPT_REPLACE = "LPT_REPLACE"  # 字符串替换
    LPT_EXTRACT_DATE_FROM_TEXT = "LPT_EXTRACT_DATE_FROM_TEXT"  # 文本内提取日期
    LPT_REMOVE = "LPT_REMOVE"  # 移除特定文本

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.LPT_CHANGE_CASE,
            cls.LPT_CLOSEST_MATCH,
            cls.LPT_REGIX,
            cls.LPT_CONCATENATE,
            cls.LPT_TO_ASCII,
            cls.LPT_REPLACE,
            cls.LPT_EXTRACT_DATE_FROM_TEXT,
            cls.LPT_REMOVE,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumLabelPostType.LPT_NULL: "未设置",
            EnumLabelPostType.LPT_CHANGE_CASE: "文本格式化",
            EnumLabelPostType.LPT_CLOSEST_MATCH: "选择性匹配",
            EnumLabelPostType.LPT_REGIX: "文本内容匹配",
            EnumLabelPostType.LPT_CONCATENATE: "组合多个同类标签",
            EnumLabelPostType.LPT_TO_ASCII: "转换为ASCII格式",
            EnumLabelPostType.LPT_REPLACE: "字符串替换",
            EnumLabelPostType.LPT_EXTRACT_DATE_FROM_TEXT: "文本内提取日期",
            EnumLabelPostType.LPT_REMOVE: "移除特定文本",
        }[val]


class EnumFactoryType(str, TransEnum):
    """EnumFactoryType."""  # noqa

    FFT_NULL = "FFT_NULL"  # 未设置

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in []

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumFactoryType.FFT_NULL: "未设置",
        }[val]


class EnumReplaceLogType(str, TransEnum):
    """EnumReplaceLogType."""  # noqa

    RLT_NULL = "RLT_NULL"  # 未设置
    RLT_NEW = "RLT_NEW"  # 新增
    RLT_REPLACE = "RLT_REPLACE"  # 替换
    RLT_DELETE = "RLT_DELETE"  # 删除
    RLT_IGNORE = "RLT_IGNORE"  # 忽略

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.RLT_NEW,
            cls.RLT_REPLACE,
            cls.RLT_DELETE,
            cls.RLT_IGNORE,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumReplaceLogType.RLT_NULL: "未设置",
            EnumReplaceLogType.RLT_NEW: "新增",
            EnumReplaceLogType.RLT_REPLACE: "替换",
            EnumReplaceLogType.RLT_DELETE: "删除",
            EnumReplaceLogType.RLT_IGNORE: "忽略",
        }[val]


class EnumLangType(str, TransEnum):
    """EnumLangType."""  # noqa

    LANG_AUTO = "LANG_AUTO"  # 自动检测语言，并识别
    LANG_CHN_ENG = "LANG_CHN_ENG"  # 中英文混合
    LANG_ENG = "LANG_ENG"  # 英文
    LANG_JAP = "LANG_JAP"  # 日语
    LANG_KOR = "LANG_KOR"  # 韩语
    LANG_FRE = "LANG_FRE"  # 法语
    LANG_SPA = "LANG_SPA"  # 西班牙语
    LANG_POR = "LANG_POR"  # 葡萄牙语
    LANG_GER = "LANG_GER"  # 德语
    LANG_ITA = "LANG_ITA"  # 意大利语
    LANG_RUS = "LANG_RUS"  # 俄语
    LANG_DAN = "LANG_DAN"  # 丹麦语
    LANG_DUT = "LANG_DUT"  # 荷兰语
    LANG_MAL = "LANG_MAL"  # 马来语
    LANG_SWE = "LANG_SWE"  # 瑞典语
    LANG_IND = "LANG_IND"  # 印尼语
    LANG_POL = "LANG_POL"  # 波兰语
    LANG_ROM = "LANG_ROM"  # 罗马尼亚语
    LANG_TUR = "LANG_TUR"  # 土耳其语
    LANG_GRE = "LANG_GRE"  # 希腊语
    LANG_HUN = "LANG_HUN"  # 匈牙利语

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.LANG_CHN_ENG,
            cls.LANG_ENG,
            cls.LANG_JAP,
            cls.LANG_KOR,
            cls.LANG_FRE,
            cls.LANG_SPA,
            cls.LANG_POR,
            cls.LANG_GER,
            cls.LANG_ITA,
            cls.LANG_RUS,
            cls.LANG_DAN,
            cls.LANG_DUT,
            cls.LANG_MAL,
            cls.LANG_SWE,
            cls.LANG_IND,
            cls.LANG_POL,
            cls.LANG_ROM,
            cls.LANG_TUR,
            cls.LANG_GRE,
            cls.LANG_HUN,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumLangType.LANG_AUTO: "自动检测语言，并识别",
            EnumLangType.LANG_CHN_ENG: "中英文混合",
            EnumLangType.LANG_ENG: "英文",
            EnumLangType.LANG_JAP: "日语",
            EnumLangType.LANG_KOR: "韩语",
            EnumLangType.LANG_FRE: "法语",
            EnumLangType.LANG_SPA: "西班牙语",
            EnumLangType.LANG_POR: "葡萄牙语",
            EnumLangType.LANG_GER: "德语",
            EnumLangType.LANG_ITA: "意大利语",
            EnumLangType.LANG_RUS: "俄语",
            EnumLangType.LANG_DAN: "丹麦语",
            EnumLangType.LANG_DUT: "荷兰语",
            EnumLangType.LANG_MAL: "马来语",
            EnumLangType.LANG_SWE: "瑞典语",
            EnumLangType.LANG_IND: "印尼语",
            EnumLangType.LANG_POL: "波兰语",
            EnumLangType.LANG_ROM: "罗马尼亚语",
            EnumLangType.LANG_TUR: "土耳其语",
            EnumLangType.LANG_GRE: "希腊语",
            EnumLangType.LANG_HUN: "匈牙利语",
        }[val]


class EnumMachineLearningType(str, TransEnum):
    """EnumMachineLearningType."""  # noqa

    ML_IMAGE_CLASSIFICATION = "ML_IMAGE_CLASSIFICATION"  # 图片分类
    ML_OCR_KEY_INFORMATION_EXTRACTION = (
        "ML_OCR_KEY_INFORMATION_EXTRACTION"  # 关键信息提取
    )

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.ML_OCR_KEY_INFORMATION_EXTRACTION,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumMachineLearningType.ML_IMAGE_CLASSIFICATION: "图片分类",
            EnumMachineLearningType.ML_OCR_KEY_INFORMATION_EXTRACTION: "关键信息提取",
        }[val]


class EnumSamplingType(str, TransEnum):
    """EnumSamplingType."""  # noqa

    EST_SEQUENTIAL = "EST_SEQUENTIAL"  # 顺序运行
    EST_RANDOM = "EST_RANDOM"  # 随机运行

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.EST_RANDOM,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumSamplingType.EST_SEQUENTIAL: "顺序运行",
            EnumSamplingType.EST_RANDOM: "随机运行",
        }[val]


class EnumDataType(str, TransEnum):
    """EnumDataType."""  # noqa

    EST_IMAGE = "EST_IMAGE"  # 图片
    EST_TEXT = "EST_TEXT"  # 文本
    EST_VIDEO = "EST_VIDEO"  # 视频

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.EST_TEXT,
            cls.EST_VIDEO,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumDataType.EST_IMAGE: "图片",
            EnumDataType.EST_TEXT: "文本",
            EnumDataType.EST_VIDEO: "视频",
        }[val]


class EnumWebHookType(str, TransEnum):
    """EnumWebHookType."""  # noqa

    WHT_SAMPLE_READINESS = "WHT_SAMPLE_READINESS"  # 就绪状态通知
    WHT_SAMPLE_ANNOTATION_UPDATED = "WHT_SAMPLE_ANNOTATION_UPDATED"  # 样本标记变更

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.WHT_SAMPLE_ANNOTATION_UPDATED,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumWebHookType.WHT_SAMPLE_READINESS: "就绪状态通知",
            EnumWebHookType.WHT_SAMPLE_ANNOTATION_UPDATED: "样本标记变更",
        }[val]


class EnumCategaryType(str, TransEnum):
    """EnumCategaryType."""  # noqa

    ECT_SECTION = "ECT_SECTION"  # 段落
    ECT_FIELD = "ECT_FIELD"  # 字段
    ECT_TABLE = "ECT_TABLE"  # 表格

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.ECT_FIELD,
            cls.ECT_TABLE,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumCategaryType.ECT_SECTION: "段落",
            EnumCategaryType.ECT_FIELD: "字段",
            EnumCategaryType.ECT_TABLE: "表格",
        }[val]


class EnumSynchronizedStatus(str, TransEnum):
    """EnumSynchronizedStatus."""  # noqa

    SYNC_NULL = "SYNC_NULL"  # 未同步
    SYNC_PASSED = "SYNC_PASSED"  # 已同步

    @classmethod
    def is_vaild(cls, val):
        """Is vaild."""
        return val in [
            cls.SYNC_PASSED,
        ]

    @classmethod
    def is_invaild(cls, val):
        """Is invaild."""
        return not cls.is_vaild(val)

    @classmethod
    def get_trans(cls, val):
        """Get trans."""
        return {
            EnumSynchronizedStatus.SYNC_NULL: "未同步",
            EnumSynchronizedStatus.SYNC_PASSED: "已同步",
        }[val]
