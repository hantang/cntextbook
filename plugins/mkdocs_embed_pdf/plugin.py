from urllib.parse import urlparse

from lxml.html import fromstring, tostring
from mkdocs.plugins import BasePlugin, get_plugin_logger

logger = get_plugin_logger("embed-pdf")


class EmbedPdfPlugin(BasePlugin):
    """
    Converts Markdown image tags with type="application/pdf"
    into <object> + <embed> for inline PDF display.
    """

    def on_page_content(self, html, page, config, files):
        if not html:
            return html
        site_url = config.get("site_url", "")
        root = ""
        if site_url.startswith("http"):
            root = urlparse(site_url).path.rstrip("/")
        logger.debug(f"site = {site_url}, root = {root}")

        content = fromstring(html)
        # 查找 <img type="application/pdf" ...>
        tags = content.xpath('//img[@type="application/pdf" and @src]')
        for tag in tags:
            pdf_src = tag.get("src")
            if not pdf_src:
                continue
            if root:
                pdf_path = f"{root}/{pdf_src}"
            else:
                pdf_path = pdf_src
            pdf_style = tag.get("style", "height:500px;width:100%")
            style_dict = dict(item.split(":", 1) for item in pdf_style.split(";") if item)
            style_dict = {k.strip(): v.strip() for k, v in style_dict.items()}

            height = style_dict.get("height", "500px")
            width = style_dict.get("width", "100%")
            alt_text = tag.get("alt", "")
            logger.debug(f"pdf = {pdf_src}")

            # 创建 <object> 包裹 <embed>
            object_tag = fromstring(f'''
            <object data="{pdf_path}" type="application/pdf" height="{height}" width="{width}">
                <embed src="{pdf_path}" type="application/pdf" style="{pdf_style}">
                    {alt_text}
                </embed>
            </object>
            ''')

            tag.addnext(object_tag)
            tag.getparent().remove(tag)

        return tostring(content, encoding="unicode")
