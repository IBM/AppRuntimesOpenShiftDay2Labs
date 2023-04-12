# https://www.mkdocs.org/dev-guide/plugins/#events
import re

def on_post_page(output, **kwargs):
    return re.sub(r'(?s)Built with.*Read the Docs</a>.', '', output)
