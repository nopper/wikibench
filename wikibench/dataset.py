import os
import re
import codecs
import cPickle as pickle
from xml.dom import minidom


class Dataset(object):
    def __init__(self, name, instances=[]):
        self.name = name
        self.instances = instances

    def __len__(self):
        return len(self.instances)

    def __getitem__(self, key):
        return Dataset(self.name, [self.instances[key]])

    def __iter__(self):
        return iter(self.instances)

    def __str__(self):
        return "%s dataset with %d instances" % (self.name, len(self.instances))

    def __repr__(self):
        return str(self)

    @staticmethod
    def save(dataset, filename):
        with open(filename, 'w') as outputfile:
            pickle.dump(dataset, outputfile)

    @staticmethod
    def load(filename):
        with open(filename, 'r') as inputfile:
            return pickle.load(inputfile)

    @staticmethod
    def save_tsv(dataset, directory):
        doc_path = os.path.join(directory, 'documents')

        if not os.path.exists(doc_path):
            os.makedirs(doc_path)

        for instance in dataset.instances:
            doc_file = os.path.join(doc_path, "%07d.txt" % instance.instance_id)

            with codecs.open(doc_file, 'w', 'utf8') as outputfile:
                outputfile.write(instance.text)

            instance.save_mentions(directory)

    @staticmethod
    def load_results(directory):
        instances = []
        ann_path = os.path.join(directory, 'annotations')

        if not os.path.exists(ann_path):
            print "WARN: not annotations in %s returning empty set" % ann_path
            return []

        for filename in sorted(os.listdir(ann_path)):
            instance_id = int(filename.replace('.tsv', ''))
            ann_file = os.path.join(ann_path, "%07d.tsv" % instance_id)

            mentions = []
            with codecs.open(ann_file, 'r', 'utf8') as inputfile:
                for line in inputfile:
                    start, end, wid, title, \
                        spot, score1, score2 = line.strip().split('\t')

                    mention = Mention(
                        spot, int(start), int(end), title, int(wid),
                        score1=float(score1), score2=float(score2))
                    mentions.append(mention)

            instances.append(Instance("", mentions, instance_id))

        return instances

    @staticmethod
    def load_tsv(directory):
        instances = []
        doc_path = os.path.join(directory, 'documents')
        ann_path = os.path.join(directory, 'annotations')

        for filename in sorted(os.listdir(doc_path)):
            instance_id = int(filename.replace('.txt', ''))
            doc_file = os.path.join(doc_path, "%07d.txt" % instance_id)
            ann_file = os.path.join(ann_path, "%07d.tsv" % instance_id)
            text = codecs.open(doc_file, 'r', 'utf8').read()

            mentions = []
            with codecs.open(ann_file, 'r', 'utf8') as inputfile:
                for line in inputfile:
                    start, end, wid, title, \
                        spot, score1, score2 = line.strip().split('\t')

                    mentions.append(
                        Mention(spot, int(start), int(end), title, int(wid),
                                score1=float(score1), score2=float(score2))
                    )

            instances.append(Instance(text, mentions, instance_id))

        return Dataset(os.path.basename(directory), instances)

    @staticmethod
    def save_xml(dataset, filename):
        import codecs
        from xml.dom.minidom import Document

        doc = Document()
        ds = doc.createElement('dataset')
        ds.attributes['name'] = dataset.name
        doc.appendChild(ds)

        for instance in dataset.instances:
            instance_el = doc.createElement('instance')
            last = 0
            text = instance.text

            # if not isinstance(text, unicode):
            #     text = text.decode('latin1', 'ignore')

            for m in instance.mentions:
                instance_el.appendChild(
                    doc.createTextNode(text[last:m.start])
                )

                ann = doc.createElement('annotation')
                ann.attributes['wid'] = str(m.wid)
                ann.attributes['title'] = m.title
                ann.appendChild(
                    doc.createTextNode(text[m.start:m.end])
                )
                instance_el.appendChild(ann)

                last = m.end

            instance_el.appendChild(doc.createTextNode(text[last:]))
            ds.appendChild(instance_el)

        with codecs.open(filename, 'w', 'utf8') as output:
            doc.writexml(output)


class Mention(object):
    def __init__(self, spot, start, end, title, wid,
                 entities=[], score1=1.0, score2=1.0):
        """
        @param spot the spot delimited by this mention
        @param start the start index of this mention
        @param end the end index of this mention
        @param title the title of the entity that this mention refers to
        @param wid the WID of the entity that this mention refers to
        @param entities a list of possible WID this mention may refer to
        @param score1 the score associated to this mention in case of ranking
        @param score2 the score associated to this mention in case of ranking
        """
        self.spot = spot
        self.start = start
        self.end = end
        self.title = title
        self.wid = wid
        self.entities = entities
        self.score1 = score1
        self.score2 = score2

    def find_matching(self, possible_mentions, strong_match=True):
        """
        Find a possible matching mention from a list of mentions
        @return an element of possible_mentions or None
        """
        if strong_match:
            matches = self.matches
        else:
            matches = lambda x: self.overlaps(x) > 0

        for dst in possible_mentions:
            if matches(dst):
                return dst

    def contains(self, wid):
        return wid in self.entities

    def matches(self, other):
        return self.start == other.start and self.end == other.end

    def overlaps(self, other):
        return max(0, min(self.end, other.end) - max(self.start, other.start))

    def is_valid(self):
        return self.title and self.wid

    def tsv_entry(self):
        spot = self.spot.replace('\n', '').replace('\r', '').replace('\t', '')
        return "%d\t%d\t%d\t%s\t%s\t%.3f\t%.3f\n" % (
            self.start, self.end, self.wid, self.title,
            spot, self.score1, self.score2
        )

    def __len__(self):
        return self.end - self.start

    def __unicode__(self):
        return "Mention(spot=%s, start=%d, end=%d, title=%s, wid=%d, score1=%.3f, score2=%.3f)" % \
                (self.spot, self.start, self.end, self.title, self.wid, self.score1, self.score2)

    def __repr__(self):
        return unicode(self).encode('utf8')


class Instance(object):
    def __init__(self, text, mentions, instance_id=0):
        self.text = text
        self.mentions = mentions
        self.instance_id = instance_id

    def __len__(self):
        return len(self.mentions)

    def __iter__(self):
        return iter(self.mentions)

    def __str__(self):
        return "Instance(%s, %s)" % (repr(self.text), repr(self.mentions))

    def pretty_print(self):
        output = ""
        prev = 0

        for mention in self.mentions:
            output += self.text[prev:mention.start]
            output += "["
            output += mention.spot
            output += "](%s)" % mention.title
            prev = mention.end

        output += self.text[prev:]
        return output

    def get_mapping(self):
        return dict(map(lambda m: (m.wid, m), self.mentions))

    @staticmethod
    def normalize_spot(text):
        #text = str(text)
        return re.sub("\s+", " ", text).strip()

    @staticmethod
    def fromDOM(instance_element, instance_id=0):
        text = ""
        mentions = []

        for node in instance_element.childNodes:
            if node.nodeType == node.TEXT_NODE:
                text += node.data
            elif node.tagName == "annotation":
                start = len(text)
                mention_text = Instance.normalize_spot(node.firstChild.data)
                text += mention_text
                end = len(text)

                if node.attributes.get('rank_0_id', None) is not None:
                    for i in xrange(len(node.attributes) / 3):
                        try:
                            title = node.getAttribute("rank_%d_title" % i)
                            wid = int(node.getAttribute("rank_%d_id" % i))
                            score = float(node.getAttribute("rank_%d_score" % i))

                            mentions.append(
                                Mention(mention_text, start, end, title, wid, score=score)
                            )
                        except:
                            import sys
                            print >>sys.stderr, "Malformed instance", node.attributes.keys()

                else:
                    title = node.getAttribute("title")
                    wid = int(node.getAttribute("wid"))
                    mentions.append(
                        Mention(mention_text, start, end, title, wid)
                    )

        return Instance(text, mentions, instance_id)

    def has_been_processed(self, directory):
        ann_path = os.path.join(directory, 'annotations')
        ann_file = os.path.join(ann_path, "%07d.tsv" % self.instance_id)

        return os.path.exists(ann_file)

    def save_mentions(self, directory, mentions=[]):
        if not mentions:
            mentions = self.mentions

        ann_path = os.path.join(directory, 'annotations')
        ann_file = os.path.join(ann_path, "%07d.tsv" % self.instance_id)

        if not os.path.exists(ann_path):
            os.makedirs(ann_path)

        with codecs.open(ann_file, 'w', 'utf8') as outputfile:
            for m in mentions:
                outputfile.write(m.tsv_entry())


class AIDADataset(Dataset):
    @staticmethod
    def read(filename):
        doc = minidom.parse(filename)
        dataset = doc.getElementsByTagName("dataset")[0]
        iterator = enumerate(dataset.getElementsByTagName("instance"))

        return Dataset(dataset.getAttribute("name"), [
            Instance.fromDOM(instance, instance_id)
            for instance_id, instance in iterator
        ])

if __name__ == "__main__":
    import sys
    dataset_file, instance = sys.argv[1:]
    dataset = Dataset.load(sys.argv[1])

    print dataset
    print dataset.instances[int(instance)].pretty_print()
