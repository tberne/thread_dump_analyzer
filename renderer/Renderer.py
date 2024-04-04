from renderer.RenderData import RenderData
from threaddump.Config import Config


class Renderer:
    def __init__(self, config: Config):
        self.__config = config

    @property
    def config(self):
        return self.__config

    def render(self, renderer_data: RenderData):
        raise NotImplementedError("Render method is not implemented")

    def check_render_data(self, renderer_data: RenderData):
        if renderer_data is None:
            raise ValueError("Renderer data is None")

        if not isinstance(renderer_data, RenderData):
            raise ValueError("Renderer data is not a RenderData instance")
