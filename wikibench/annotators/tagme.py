import requests
import logging
from wikibench.dataset import Mention
from wikibench.annotator import Annotator


class TagMEAnnotator(Annotator):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url', 'http://tagme.di.unipi.it')
        self.annotate_url = self.url + '/tag'
        self.params = kwargs
        self.log = logging.getLogger(self.__class__.__name__)

    def set_configuration(self, configuration):
        self.params.update(configuration)

    def __str__(self):
        arguments = ','.join(
            map(
                lambda x: str(x[0]) + '=' + str(x[1]),
                sorted(self.get_params().items())
            )
        )
        return "TagME(%s)" % arguments

    def get_params(self):
        return dict(self.params)

    def annotate(self, instance):
        data = self.get_params()
        data['text'] = instance.text
        data = requests.post(self.annotate_url,
                             params=self.get_params(),
                             data=data).json()

        print data['time']

        mentions = []

        for ann in data['annotations']:
            mentions.append(
                Mention(ann['spot'], ann['start'], ann['end'],
                        ann.get('title', ''),
                        ann['id'], score1=float(ann['rho']))
            )

        return mentions


__annotator__ = TagMEAnnotator
