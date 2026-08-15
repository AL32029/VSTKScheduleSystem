from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .filters import format_ru_date


class TemplateMessageRenderer:
    """Класс шаблонизатора сообщений"""

    def __init__(self, template_dir: str = "../templates"):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.filters["ru_date"] = format_ru_date

    def render(self, template_name: str, **kwargs) -> str:
        """Рендеринг сообщения"""
        try:
            template = self.env.get_template(f"{template_name}.txt")
            return template.render(**kwargs)
        except TemplateNotFound:
            return f"⚠️ Шаблон '{template_name}' не найден."
