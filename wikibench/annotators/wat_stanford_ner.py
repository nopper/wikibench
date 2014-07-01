import json
import requests
import logging
from wikibench.dataset import Mention
from wikibench.annotator import Annotator


class WATStanfordNERD(Annotator):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url', 'http://wikisense.mkapp.it')
        self.spot_url = self.url + '/nlp'
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
        return "WATStanfordNERD(%s)" % arguments

    def get_params(self):
        return dict(self.params)

    def spot(self, instance, **kwargs):
        params = self.get_params()
        data = json.dumps({'text': instance.text})

        headers = {'Content-type': 'application/json'}

        data = requests.post(self.spot_url,
                             params=params,
                             data=data,
                             headers=headers).json()

        mentions = []
        for spot in data:
            if spot['ner'] in ('PERSON', 'ORGANIZATION', 'LOCATION'):
                mentions.append(
                    Mention(spot['token'], spot['start'], spot['end'], '', -1)
                )

        return mentions


__annotator__ = WATStanfordNERD
