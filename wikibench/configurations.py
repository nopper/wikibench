import json
from collections import OrderedDict
from wikibench.dataset import Dataset
from wikibench.utils import create_annotator, create_experiment


class Configurations(object):
    def __init__(self, conf_file='configurations.json'):
        self.annotators = OrderedDict()
        self.datasets = OrderedDict()
        self.experiments = OrderedDict()

        with open(conf_file, 'r') as inputfile:
            conf = json.load(inputfile)

            # Load annotators
            for annotator_conf in conf["annotators"]:
                nickname = annotator_conf["alias"]
                module_name = annotator_conf["name"]
                annotator = create_annotator(str(module_name))
                annotator.set_configuration(annotator_conf["configuration"])

                self.annotators[nickname] = annotator

            # Load datasets
            for dataset_conf in conf["datasets"]:
                self.datasets[dataset_conf["name"]] = \
                    Dataset.load_tsv(dataset_conf["file"])

            # Load experiments
            for exp_conf in conf["experiments"]:
                self.experiments[exp_conf["name"]] = \
                    create_experiment(str(exp_conf["name"]), exp_conf)
