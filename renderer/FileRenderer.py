from renderer.ConsoleRenderer import ConsoleRenderer


class FileRenderer(ConsoleRenderer):
    def __init__(self, config):
        super().__init__(config)

        # check if the renderer config is valid
        if not self.config.renderer_config or not "output_file" in self.config.renderer_config:
            raise ValueError("Output file is not defined in the config")

        self.__output_file = self.config.renderer_config["output_file"]

    @property
    def output_file(self):
        return self.__output_file

    def init_file_object(self):
        return open(self.output_file, 'w')

    def close_file_object(self, text_io):
        text_io.close()
