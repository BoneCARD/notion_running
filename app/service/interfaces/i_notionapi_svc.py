import abc

from notion_client import AsyncClient


class NotionAPIServiceInterface(abc.ABC):

    @staticmethod
    def demo_property_text(_type, title_key, title_value):
        """

        :param _type: title、rich_text
        :param title_key:
        :param title_value:
        :return:
        """
        return {
            title_key: {
                _type: [
                    {
                        "text": {
                            "content": title_value
                        }
                    }
                ]
            }
        }

    @staticmethod
    def demo_property_URL(key, value):
        return {
            key: {
                "url": value
            }
        }

    # @staticmethod
    # def demo_property_select(key, value):
    #     return {
    #         key: {
    #             "url": value
    #         }
    #     }

    @staticmethod
    def demo_property_Checkbox(key, value: bool = False):
        return {
            key: {
                "checkbox": value
            }
        }

    @staticmethod
    def demo_property_normal(key, value, _type):
        return {
            key: {
                _type: value
            }
        }

    @staticmethod
    def demo_simple_block(_type: str):
        """
        :param _type:
        最简单的block类型，都是结构类型，不需要输入任何信息：
            "divider", "table_of_contents", "breadcrumb"
        """
        return {
            "type": _type,
            _type: {},
        }

    @staticmethod
    def demo_external(url: str):
        """
        返回一个外文引用的文本结构，不同与block结构，文本结构只能算block的内嵌结构
        用于调用url链接的网络资源信息

        :param url:
        """
        return {
            "type": "external",
            "external": {"url": url}
        }

    @staticmethod
    def demo_link(url: str):
        """
        :param url:
        """
        return {
            "type": "url",
            "url": url
        }

    @staticmethod
    def demo_external_block(_type: str, _url: str):
        """
        :param _type:
        引用外部网络资源的类型block的类型，当前支持的类型：
            "embed", "image", "video", "file", "pdf", "bookmark"
        :param _url: 外部引用资源的链接
        """
        return {
            "type": _type,
            _type: NotionAPIServiceInterface.demo_external(_url),
        }

    @staticmethod
    def demo_Text(content: str, link: str = None, href: str = None, italic: bool = False,
                  bold: bool = False, strikethrough: bool = False,
                  underline: bool = False, code: bool = False, color: str = "default", **kwargs):
        """
        返回一个文本结构，不同与block结构，文本结构只能算block的内嵌结构
        详情富文本可以查看：https://developers.notion.com/reference/rich-text

        :param color:
        文字的颜色，可选值： "default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red",
            "gray_background", "brown_background", "orange_background", "yellow_background", "green_background",
            "blue_background", "purple_background", "pink_background", "red_background"
        :param code: 文字是否为代码风格
        :param italic: 文本是否为斜体
        :param bold: 文本是否加粗
        :param underline: 文本是否带有下划线
        :param strikethrough: 文本是否被划线
        :param href: Notion内部链接跳转
        :param link: 外部URL链接跳转
        :param content: 文本内容;由于单个text的content最大长度为2000，超长时需要做分片，代码参考：
                _block_texts = [NotionAPIServiceInterface.demo_Text(code_t[_:_+2000]) for _ in range(0, len(code_t), 2000)]
        """
        if link:
            link = NotionAPIServiceInterface.demo_link(link)
        # TODO 修改返回的类型为列表，对超过2000的content自动进行分片
        return {
            "type": "text",
            "text": {"content": content, "link": link},
            "href": href,
            "annotations": {
                "italic": italic, "bold": bold, "color": color, "strikethrough": strikethrough, "underline": underline, "code": code
            }
        }

    block_type = ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "to_do", "toggle",
                  "child_page", "child_database",
                  "embed", "image", "video", "file", "pdf",
                  "bookmark", "callout", "quote", "equation", "divider", "table_of_contents", "column", "column_list",
                  "link_preview"]

    @staticmethod
    def demo_text_block(_type: str, text: list, children: list = None, language="plain text"):
        """
        :param _type:
        当前支持的文本block类型：
            "paragraph", 文章段落，最常用记录文章内容的block
            "heading_1", "heading_2", "heading_3", 文章标题，目前只支持三种
            "bulleted_list_item", "numbered_list_item", 无序和有序两种排列方式
            "to_do", todo模块
            "toggle", 切换模块，将子模块切换收缩显示
        :param text: 引用的demo_text格式构成的列表
        :param children: block数据结构的列表，作为子block更新
            "heading_1", "heading_2", "heading_3", "code" 四种类型没有子block结构
        :param language: 仅在类型为code时有用
        """
        support_type = ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "to_do", "toggle", "code"]
        if _type not in support_type:
            raise Exception("不支持%s该类型的文本block， 当前支持的类型有： " % _type, support_type)
        _demo = {"type": _type, _type: {"text": text}}
        if children is not None and _type not in ["heading_1", "heading_2", "heading_3", "code"]:
            _demo[_type].update(dict(children=children))
        if _type == "code":
            _demo[_type].update(dict(language=language))
        return _demo
