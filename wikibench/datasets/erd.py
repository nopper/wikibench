import os
import sys
import codecs
import requests
from itertools import groupby
from wikibench.dataset import *


class ERDConvert(object):
    def __init__(self, goldenfile):
        self.golden = self.read_file(goldenfile)

    def get_wid(self, mid):
        return requests.get(
            'http://wikisense.mkapp.it/wiki/freebase/id/' + mid).json()

    def get_title(self, wid):
        title = requests.get(
            'http://wikisense.mkapp.it/wiki/title/' + str(wid)).json()
        if not title:
            return ''
        return title

    def export_dataset(self, results, output):
        instances = []

        for docid, (docname, mentions) in enumerate(self.golden):
            text = codecs.open(
                os.path.join(results, docname + ".txt"),
                'r',
                'utf8'
            ).read()

            filtered = []
            prevend = 0

            for m in mentions:
                cum = 0
                offsets = []
                for c in text:
                    offsets.append(cum)
                    cum += len(c.encode('utf8'))


                m.start = offsets[m.start]
                m.end = m.start + len(m.spot)#offsets[min(m.end, len(offsets) - 1)]

                shiftback = min(10, max(0, m.start + 1 - prevend))

                while shiftback >= 0 and text[m.start:m.end] != m.spot:
                    m.start -= 1
                    m.end -= 1
                    shiftback -= 1

                if text[m.start:m.end] != m.spot:
                    print docid, type(text), type(m.spot), text[m.start:m.end], '==', m.spot, docname
                else:
                    filtered.append(m)
                    prevend = m.end

            instance = Instance(text, filtered, docid)
            instances.append(instance)

        dataset = Dataset('ERD', instances)
        Dataset.save_tsv(dataset, output)

    def read_file(self, filename):
        if not os.path.exists(filename):
            return [(None, [])]

        def iterate_golden():
            for line in codecs.open(filename, 'r', 'utf8'):
                text_id, left, right, fid, title, mention, score1, score2 = line.strip().split('\t')
                wid = self.get_wid('m.' + fid[3:])
                title = self.get_title(wid)
                yield text_id, mention, int(left), int(right), title, wid

        results = []

        for docid, items in groupby(iterate_golden(), key=lambda x: x[0]):
            instances = [Mention(*x[1:]) for x in items]
            results.append((docid, instances))

        if not results:
            return [(None, [])]

        return results

conv = ERDConvert(sys.argv[1])
conv.export_dataset(sys.argv[2], sys.argv[3])
