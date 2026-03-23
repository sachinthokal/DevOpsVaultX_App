from django import template
import markdown2
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown_to_html')
def markdown_to_html(text):
    """
    Converts Markdown text to HTML with specific extras for DevOps documentation.
    Ensures code blocks and headings are rendered correctly for the Copy UI.
    """
    if not text:
        return ""

    # Professional Markdown extras:
    # - fenced-code-blocks: Required for multi-line code blocks and copy logic.
    # - code-friendly: Ensures underscores in DevOps scripts don't break formatting.
    # - cuddled-lists: Improves spacing between text and lists/code.
    # - metadata: REMOVED to prevent the first H1 line from disappearing.
    extras = [
        "fenced-code-blocks",
        "tables",
        "task_list",
        "code-friendly",
        "cuddled-lists", 
        "header-ids",
        "strike",
        "breaks",
        "underline",
        "spoiler"
    ]

    # Convert markdown to safe HTML
    html_content = markdown2.markdown(text, extras=extras)
    
    # mark_safe prevents Django from escaping the generated HTML tags
    return mark_safe(html_content)