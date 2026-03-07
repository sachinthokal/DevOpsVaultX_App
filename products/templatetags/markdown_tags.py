from django import template
import markdown2

register = template.Library()

@register.filter(name='markdown_to_html')
def markdown_to_html(text):
    if not text:
        return ""
    # 'strikethrough' extra add kelyachi khatri kara
    return markdown2.markdown(text, extras=["strikethrough", "fenced-code-blocks", "tables"])