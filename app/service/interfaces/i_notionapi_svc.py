import abc

from notion_client import AsyncClient


class NotionAPIServiceInterface(abc.ABC):

    # @abc.abstractmethod
    # def connect_server(self):
    #     """
    #     Establish a connection to the Notion API Server and obtain an access session
    #     :return:
    #     """
    #     pass
    #
    # @abc.abstractmethod
    # def destroy_session(self):
    #     """
    #     Destroy the session
    #     :return:
    #     """
    #     pass

    @staticmethod
    def demo_property_Title(title_key, title_value):
        return {
            title_key: {
                "title": [
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

    @staticmethod
    def demo_property_Checkbox(key, value: bool = False):
        return {
            key: {
                "checkbox": value
            }
        }

    @staticmethod
    def demo_Text(content: str, link: dict = None, href: str = None, italic: bool = False,
                  bold: bool = False, strikethrough: bool = False,
                  underline: bool = False, code: bool = False, color: str = "default"):
        """
        返回一个文本结构
        详情富文本可以查看：https://developers.notion.com/reference/rich-text

        :param color: 文字的颜色，可能的值： "default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red",
            "gray_background", "brown_background", "orange_background", "yellow_background", "green_background",
            "blue_background", "purple_background", "pink_background", "red_background"
        :param code: 文字是否为代码风格
        :param italic: 文本是否为斜体。
        :param bold: 文本是否加粗
        :param underline: 文本是否带有下划线。
        :param strikethrough: 文本是否被划线
        :param href: Notion内部链接跳转
        :param link: 外部URL链接跳转
        :param content: 文本内容
        """
        return {
            "type": "text",
            "text": {
                "content": content,
                "link": link
            },
            "href": href,
            "annotations": {
                "italic": italic,
                "bold": bold,
                "color": color,
                "strikethrough": strikethrough,
                "underline": underline,
                "code": code
            }
        }

    @staticmethod
    def demo_block_Paragraph(text: list, children=None):
        """
        :param :
        :type :
        """
        if children:
            return {
                "type": "paragraph",
                "paragraph": {
                    "text": text,  # 引用的demo_text格式
                    "children": []  # 引用的demo_block_paragraph格式
                }
            }
        else:
            return {
                "type": "paragraph",
                "paragraph": {
                    "text": text
                }
            }

    @staticmethod
    def demo_block_EmbedUrl(image_url):
        """
        :param : image_url
        :type : string
        """
        return {
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": image_url
                }
            }
        }

    @staticmethod
    def demo_block_Image(image_url):
        """
        :param : image_url
        :type : string
        """
        return {
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": image_url
                }
            }
        }

    @staticmethod
    def demo_block_Code(content, language):
        """
        :param : content
        :type : string
        """
        return {
            "type": "code",
            "code": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": content
                    }
                }],
                "language": language
            }
        }

    @staticmethod
    def demo_block_HeadingX(X: str, content, link=None):
        """
        :param :
        :type :
        """
        if str(X) not in ["1", "2", "3"]:
            raise Exception("输入的X参数(%s)有问题，heading只有1,2,3三种格式" % X)
        return {
            "type": "heading_" + str(X),
            "heading_" + str(X): {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": content,
                        "link": link
                    }
                }]
            }
        }
