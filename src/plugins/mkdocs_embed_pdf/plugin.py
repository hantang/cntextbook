from urllib.parse import urlparse

from lxml.html import fromstring, tostring
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.config import config_options

logger = get_plugin_logger("embed-pdf")


def split_to_dict(data):
    style_dict = dict(item.split(":", 1) for item in data.split(";") if item if ":" in item)
    style_dict = {k.strip(): v.strip() for k, v in style_dict.items()}
    return style_dict


class EmbedPdfPlugin(BasePlugin):
    """
    Converts Markdown image tags with type="application/pdf"
    into <object> + <embed> for inline PDF display.
    """

    config_scheme = (
        ("mode", config_options.Type(str, default="auto")),
        ("height", config_options.Type(str, default="500px")),
        ("width", config_options.Type(str, default="100%")),
    )

    def _create_path(self, mode, root, pdf_path):
        if mode == "auto":
            if pdf_path.startswith("/"):
                return pdf_path
            else:
                pdf_path = pdf_path.lstrip("/")
                return f"{root}/{pdf_path}"
        elif mode == "absolute":
            if pdf_path.startswith("/"):
                return pdf_path
            else:
                return f"/{pdf_path}"
        elif mode == "relative":
            if pdf_path.startswith("/"):
                return pdf_path.lstrip("/")
            return pdf_path
        return pdf_path

    def on_page_content(self, html, page, config, files):
        if not html:
            return html
        site_url = config.get("site_url", "")
        root = ""
        if site_url.startswith("http"):
            root = urlparse(site_url).path.rstrip("/")
        if not root.startswith("/"):
            root = f"/{root}"

        mode = self.config["mode"]
        default_height = self.config["height"]
        default_width = self.config["width"]

        # logger.debug(f"site = {site_url}, root = {root}, mode = {mode}, {default_height} x {default_width}")
        content = fromstring(html)
        # 查找 <img type="application/pdf" ...>
        tags = content.xpath('//img[@type="application/pdf" and @src]')
        # logger.debug(f"tags = {len(tags)}")
        for tag in tags:
            pdf_src = tag.get("src", "")
            logger.debug(f"pdf_src = {pdf_src} {pdf_src.lower().endswith('.pdf')}")
            if not (pdf_src and pdf_src.lower().endswith(".pdf")):
                continue
            pdf_path = self._create_path(mode, root, pdf_src)
            style_dict = split_to_dict(tag.get("style", ""))

            height = style_dict.get("height", default_height)
            width = style_dict.get("width", default_width)
            alt_text = tag.get("alt", pdf_src.split("/")[-1])
            # logger.debug(f"pdf = {pdf_src}")

            # 创建 <object> 包裹 <embed>
            object_str = f"""
            <object data="{pdf_path}" type="application/pdf" height="{height}" width="{width}">
                <embed src="{pdf_path}" type="application/pdf" height="{height}" width="{width}">
                    <p>您的浏览器不支持 PDF 预览（{alt_text}），请<a href="{pdf_path}">下载文件</a>。</p>
                </embed>
            </object>
            """

            object_tag = fromstring(object_str)
            tag.addnext(object_tag)
            tag.getparent().remove(tag)

        return tostring(content, encoding="unicode")
