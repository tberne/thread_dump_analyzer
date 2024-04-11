from renderer.JsonFileRenderer import JsonFileRenderer
import pkgutil


class HtmlRenderer(JsonFileRenderer):
    def __init__(self, config):
        super().__init__(config)

    def render_string(self, renderer_data) -> str:
        json_string = super().render_string(renderer_data)
        html_template = pkgutil.get_data(__name__, "ThreadDumpAnalysis.html").decode("utf-8")
        return html_template.replace("__render_data__", json_string)