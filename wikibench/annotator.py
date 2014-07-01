import json
from wikibench.evaluation import *


class Annotator(object):
    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)

    def annotate(self, instance):
        raise NotImplementedError("Implementation not provided")

    def disambiguate(self, instance):
        raise NotImplementedError("Implementation not provided")

    def spot(self, instance):
        raise NotImplementedError("Implementation not provided")

    def load_configuration_from(self, conf_file):
        with open(conf_file, 'r') as inputfile:
            self.set_configuration(json.load(inputfile))

    def set_configuration(self, configuration):
        pass

    def pretty_print(self, instance, mentions):
        output = ""
        prev = 0

        def label(mention):
            overlapping = filter(lambda x: x.overlaps(mention), instance)

            if not overlapping:
                return "NO"

            if any(filter(lambda x: x.wid == mention.wid, overlapping)):
                return "ok"
            else:
                return " != %s" % (overlapping[0].title)

        for mention in mentions:
            output += instance.text[prev:mention.start]
            output += "["
            output += mention.spot
            output += "](%s %s)" % (mention.title, label(mention))
            prev = mention.end

        output += instance.text[prev:]
        return output
