import requests
import logging
from wikibench.dataset import Mention
from wikibench.annotator import Annotator
from wikibench.wikiapi import get_wid_from_title


class AIDAAnnotator(Annotator):
    def __init__(self, *args, **kwargs):
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
        return "AIDAAnnotator(%s)" % arguments

    def get_params(self):
        return dict(self.params)

    def disambiguate(self, instance):
        output = ""
        prev = 0

        for mention in instance.mentions:
            output += instance.text[prev:mention.start]
            output += "[[%s]]" % mention.spot
            prev = mention.end

        output += instance.text[prev:]
        params = self.get_params()
        url = params.pop('url')
        params['text'] = output

        r = requests.post(url, data=params)
        data = r.json()

        mentions = []

        for ann in filter(lambda x: 'bestEntity' in x, data['mentions']):
            spot = ann['name']
            start = ann['offset']
            end = start + ann['length']
            title = ann['bestEntity']['name'].decode('unicode-escape')
            wid = get_wid_from_title(title)
            score1 = float(ann['bestEntity']['disambiguationScore'])
            mentions.append(
                Mention(spot, start, end, title, wid, score1=score1)
            )

        return mentions

    def annotate(self, instance):
        data = self.get_params()
        url = data.pop('url')
        data['text'] = instance.text
        data = requests.post(url,
                             params=self.get_params(),
                             data=data).json()

        mentions = []

        for ann in filter(lambda x: 'bestEntity' in x, data['mentions']):
            spot = ann['name']
            start = ann['offset']
            end = start + ann['length']
            title = ann['bestEntity']['name'].decode('unicode-escape')
            wid = get_wid_from_title(title)
            score1 = float(ann['bestEntity']['disambiguationScore'])
            mentions.append(
                Mention(spot, start, end, title, wid, score1=score1)
            )

        return mentions


__annotator__ = AIDAAnnotator
