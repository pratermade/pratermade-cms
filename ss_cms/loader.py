
from django.template.loaders.filesystem import Loader as BaseLoader
from website.models import Settings


class Loader(BaseLoader):

    def get_dirs(self):
        if Settings.objects.filter().exists():
            theme = Settings.objects.all()[0].theme
            self.dirs = []
            for d in self.engine.dirs:
                self.dirs.append("{}/{}".format(d, theme))
                self.dirs.append(d)

        return self.dirs if self.dirs is not None else self.engine.dirs