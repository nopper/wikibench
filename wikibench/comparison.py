import json
from texttable import Texttable
from wikibench.dataset import Dataset
from wikibench.utils import create_annotator, create_benchmark


class BenchmarkComparision(object):
    def __init__(self, benchmark):
        self.benchmark = benchmark
        self.datasets = []
        self.annotators = []
        self.metrics = []

        with open('comparison.json', 'r') as inputfile:
            conf = json.load(inputfile)

            for dataset in conf["datasets"]:
                self.add_dataset(Dataset.load(dataset))

            for annotator_conf in conf["annotators"]:
                annotator = create_annotator(str(annotator_conf["name"]))
                annotator.set_configuration(
                    {"wikisense": annotator_conf["configuration"]}
                )

                annotator.name = annotator_conf["alias"]
                self.add_annotator(annotator)

    def run(self):
        self.metrics = []

        for dataset in self.datasets:
            for annotator in self.annotators:
                self.benchmark.run(dataset, annotator)
                self.metrics.append(
                    (dataset, annotator, self.benchmark.metrics.clone())
                )
                self.benchmark.reset()

    def add_dataset(self, dataset):
        self.datasets.append(dataset)

    def add_annotator(self, annotator):
        self.annotators.append(annotator)

    def summary(self):
        table = Texttable(200)
        table.set_deco(Texttable.HEADER)
        table.set_cols_dtype(
            ['t',  # Dataset
             't',  # Method
             'f',  # F1 (micro)
             'f',  # Precision (micro)
             'f',  # Recall (micro)
             'f',  # F1 (macro)
             'f',  # Precision (macro)
             'f',  # Recall (macro)
             'i',  # TP
             'i',  # TN
             'i',  # FP
             'i']  # FN
        )

        table.header(['Dataset',
                      'Method',
                      'micro-F1',
                      'micro-P',
                      'micro-R',
                      'macro-F1',
                      'macro-P',
                      'macro-R',
                      'TP',
                      'TN',
                      'FP',
                      'FN'])

        for dataset, annotator, m in self.metrics:
            table.add_row([
                dataset.name,
                annotator.name,
                m.f1(),
                m.precision(),
                m.recall(),
                m.macro_f1(),
                m.macro_precision(),
                m.macro_recall(),
                m.tp,
                m.tn,
                m.fp,
                m.fn
            ])

        print "Performance on %s" % self.benchmark
        print table.draw()

if __name__ == "__main__":
    import sys
    benchmark = create_benchmark(sys.argv[1])
    benchmark.parse_arguments(sys.argv[2:])

    comp = BenchmarkComparision(benchmark)
    comp.run()
    comp.summary()
