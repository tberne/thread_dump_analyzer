from renderer.JsonFileRenderer import JsonFileRenderer

class HtmlRenderer(JsonFileRenderer):
    def __init__(self, config):
        super().__init__(config)

    def render_string(self, renderer_data) -> str:
        json_string = super().render_string(renderer_data)
        with open("renderer/ThreadDumpAnalysis.html", "r") as file:
            html_template = file.read()
            return html_template.replace("__render_data__", json_string)