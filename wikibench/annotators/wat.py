import json
import requests
import logging
from wikibench.dataset import Mention
from wikibench.annotator import Annotator

FORMAT = '%(levelname)s - %(name)s - %(message)s'
logging.basicConfig(format=FORMAT)


class WATMention(Mention):
    def __init__(self, **kwargs):
        # In case of spot title and id are not defined
        super(WATMention, self).__init__(
            kwargs.pop('spot'),
            kwargs.pop('start'),
            kwargs.pop('end'),
            kwargs.pop('title', None),
            kwargs.pop('id', 0),
            kwargs.pop('entities', [])
        )

        self.length = self.end - self.start
        self.numTokens = kwargs.pop('numTokens', 1)
        self.linkProb = kwargs.pop('linkProb', 0.0)
        self.anchorFrequency = kwargs.pop('anchorFrequency', 0)
        self.numLinks = kwargs.pop('numLinks', 0)
        self.boostedLinks = kwargs.pop('boostedLinks', 0)
        self.ambiguity = kwargs.pop('ambiguity', 0)
        self.idf = kwargs.pop('idf', 0.0)
        self.collectionProb = kwargs.pop('collectionProb', 0.0)
        self.documentProb = kwargs.pop('documentProb', 0.0)
        self.gamma1 = kwargs.pop('gamma1', 0.0)
        self.gamma2 = kwargs.pop('gamma2', 0.0)
        self.clarity = kwargs.pop('clarity', 0.0)
        self.mutualDependency = kwargs.pop('mutualDependency', 0.0)

        self.pageRank = kwargs.pop('pageRank', 0.0)
        self.pageHits = kwargs.pop('pageHits', 0.0)
        self.hub = kwargs.pop('hub', 0.0)
        self.authority = kwargs.pop('authority', 0.0)
        self.clustering = kwargs.pop('clustering', 0.0)
        self.eigenVector = kwargs.pop('eigenVector', 0.0)
        self.inDegree = kwargs.pop('inDegree', 0.0)
        self.outDegree = kwargs.pop('outDegree', 0.0)
        self.synonymy = kwargs.pop('synonymy', 0.0)
        self.commonness = kwargs.pop('commonness', 0.0)

        self.rho = kwargs.pop('rho', 0.0)
        self.localCoherence = kwargs.pop('localCoherence', 0.0)
        self.globalCoherence = kwargs.pop('globalCoherence', 0.0)
        self.contributions = kwargs.pop('contributions', 0.0)
        self.contributionRatio = kwargs.pop('contributionRatio', 0.0)

        self.pointsTo = kwargs.pop('pointsTo', 0)
        self.pointedBy = kwargs.pop('pointedBy', 0)

        self.modelScore = kwargs.pop('modelScore', -1)
        self.ranking = kwargs.pop('ranking', [])
        self.spotFeatures = kwargs.pop('spotFeatures', '')
        self.annotationFeatures = kwargs.pop('annotationFeatures', '')

    def get_spot_features(self):
        spot_letters = ''.join(filter(lambda x: x.isalpha(), self.spot))
        spot_letters_space = ''.join(filter(
            lambda x: x.isalpha() or x == ' ',
            self.spot
        ))

        if spot_letters.isupper():
            allupper = 1.0
        else:
            allupper = 0.0

        if len(spot_letters) > 2 and \
           spot_letters[0].isupper() and spot_letters[1].islower():
            capitalize = 1.0
        else:
            capitalize = 0.0

        words = filter(lambda x: x, spot_letters_space.split(' '))
        num_cap_words = sum(map(lambda x: x[0].isupper() and 1 or 0, words))
        ratio_cap_words = num_cap_words * 1.0 / self.numTokens

        return [
            allupper,
            capitalize,
            num_cap_words,
            ratio_cap_words,
            self.length,
            self.numTokens,
            self.length * 1.0 / self.numTokens,
            self.linkProb,
            self.numLinks * 1.0 / self.boostedLinks,
            self.ambiguity * 1.0 / self.numLinks,
            self.documentProb,
            self.mutualDependency
        ]

    def get_mention_features(self):
        auth = (self.pointsTo + 1) * 1.0 / max(self.pointsTo + 1, self.pointedBy + 1)
        hub = (self.pointedBy + 1) * 1.0 / max(self.pointedBy + 1, self.pointsTo + 1)

        if self.title.replace("_", " ").lower() == self.spot.lower():
            match_title = 1.0
        else:
            match_title = 0.0

        features = []#self.get_spot_features()
        features.extend([
            match_title,
            self.commonness * 1.0 / max(self.commonness, self.linkProb),
            self.commonness * 1.0 / self.ambiguity,
            self.globalCoherence,
            self.commonness,
            self.contributionRatio,
            auth,
            hub,
            (self.commonness + self.globalCoherence + self.contributionRatio + self.linkProb) / 4.0,
            match_title
        ])

        return features

    def spot_features_svmlight(self):
        return self.spotFeatures
        # return ' '.join(map(
        #     lambda x: "%d:%g" % (x[0] + 1, x[1]),
        #     enumerate(self.get_spot_features()))
        # )

    def mention_features_svmlight(self):
        return self.annotationFeatures
        # return ' '.join(map(
        #     lambda x: "%d:%g" % (x[0] + 1, x[1]),
        #     enumerate(self.get_mention_features()))
        # )

    def is_disambiguated(self):
        return self.title is not None and self.id != 0

    def __str__(self):
        return "WATMention(spot=%s, start=%d, end=%d, title=%s, wid=%d, linkProb=%f, anchorFrequency=%d, numLinks=%d, ambiguity=%d, rho=%f, globalCoherence=%f, pageRank=%f, pageHits=%f, pointsTo=%d, pointedBy=%d, modelScore=%f)" % \
                (self.spot, self.start, self.end, repr(self.title), self.wid,
                 self.linkProb, self.anchorFrequency, self.numLinks,
                 self.ambiguity, self.rho, self.globalCoherence,
                 self.pageRank, self.pageHits,
                 self.pointsTo, self.pointedBy, self.modelScore)

    def clone(self):
        return WATMention(
            self.spot,
            self.start,
            self.end,
            self.title,
            self.wid,
            self.entities,
            self.linkProb,
            self.anchorFrequency,
            self.numLinks,
            self.ambiguity,
            self.rho,
            self.coherence,
            self.pageRank,
            self.pageHits,
            self.pointsTo,
            self.pointedBy,
            self.modelScore
        )


class WATAnnotator(Annotator):
    SPOT_ATTRIBUTES_RANGE = (
        ('linkProb', 0.0, 1.0, 0.01),
        ('idf', 0.0, 1.0, 0.01),
        ('gamma1', 0.0, 1.0, 0.01),
        ('gamma2', 0.0, 1.0, 0.01),
        ('collectionProb', 0.0, 0.1, 0.001),
    )

    ANNOTATION_ATTRIBUTES_RANGE = (
        ('rho', 0.0, 1.0, 0.001),
        ('localCoherence', 0.0, 1.0, 0.01),
        ('globalCoherence', 0.0, 1.0, 0.01),
    )

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url', 'http://wikisense.mkapp.it')
        # self.url = kwargs.pop('url', 'http://localhost:9000')
        self.spot_url = self.url + '/tag/spot'
        self.disambiguate_url = self.url + '/tag/disambiguate'
        self.annotate_url = self.url + '/tag/tag'
        self.is_disambiguation_url = self.url + '/wiki/disambiguation'
        self.redirect_url = self.url + '/wiki/redirect'
        self.title_url = self.url + '/wiki/title'
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
        return "WATAnnotator(%s)" % arguments

    def get_params(self):
        return dict(self.params)

    def spot(self, instance, include_entities=False, **kwargs):
        """
        @param instance instance to spot
        @param include_entities will return a list of possible candidate
                                entities for the given spot
        @return a list of WATMention
        """
        params = self.get_params()
        params.update(kwargs)
        params['includeEntities'] = str(include_entities).lower()

        data = json.dumps({'text': instance.text})

        headers = {'Content-type': 'application/json'}

        data = requests.post(self.spot_url,
                             params=params,
                             data=data,
                             headers=headers).json()

        mentions = [WATMention(**spot) for spot in data['spots']]

        for m in mentions:
            m.score1 = m.linkProb

        return mentions

    def annotate(self, instance):
        data = json.dumps({'text': instance.text})
        headers = {'Content-type': 'application/json'}
        data = requests.post(self.annotate_url,
                             params=self.get_params(),
                             data=data,
                             headers=headers).json()

        print data['time']

        mentions = [WATMention(**spot) for spot in data['annotations']]

        for m in mentions:
            m.score1 = m.rho
            m.score2 = m.linkProb

        return mentions

    def disambiguate(self, instance):
        data = json.dumps({
            'text': instance.text,
            'spans': map(lambda x: {
                'start': x.start,
                'end': x.end
            }, instance.mentions)
        })

        headers = {'Content-type': 'application/json'}

        r = requests.post(self.disambiguate_url,
                          params=self.get_params(),
                          data=data,
                          headers=headers)

        print r.url

        try:
            data = r.json()
        except Exception, exc:
            #self.log.error("Error parsing %s" % r.text)
            self.log.exception(exc)
            self.log.error("Returning empty set")
            return []

        mentions = [WATMention(**spot) for spot in data['annotations']]

        for m in mentions:
            m.score1 = m.rho
            m.score2 = m.linkProb

        return mentions

    def resolve_redirect(self, wid):
        return requests.get(self.redirect_url + '/%d' % wid).json()

    def get_title(self, wid):
        return requests.get(self.title_url + '/%d' % wid)\
                       .json().replace("_", " ")

    def is_disambiguation(self, wid):
        return requests.get(self.is_disambiguation_url + '/%d' % wid).json()

    def reshape(self, dataset):
        """
        Reshape the dataset possibly resolving redirect issues. We transform
        the dataset in place.
        """

        for instance in dataset:
            instance.mentions = filter(
                lambda x: not self.is_disambiguation(x.wid),
                instance.mentions
            )

            for mention in instance:
                new_wid = self.resolve_redirect(mention.wid)

                if new_wid != mention.wid:
                    mention.wid = new_wid
                    mention.title = self.get_title(mention.wid)

        return dataset

__annotator__ = WATAnnotator

if __name__ == "__main__":
    import sys
    from wikibench.dataset import Instance
    wikisense = WATAnnotator()
    instance = Instance(sys.argv[1], [])

    mentions = wikisense.annotate(instance)
    print wikisense.pretty_print(instance, mentions)
