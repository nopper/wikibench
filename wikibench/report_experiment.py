# encoding: utf8

import os
from itertools import izip_longest
from tabulate import tabulate
from optparse import OptionParser
from wikibench.evaluation import *
from wikibench.dataset import Dataset, Instance
from wikibench.metrics import Metrics
from wikibench.configurations import Configurations


class Reporter(object):
    def __init__(self):
        parser = OptionParser()
        parser.add_option("-c", "--conf", dest="configuration",
                          help="Configuration file in json format",
                          metavar="FILE", default="configurations.json")
        parser.add_option("-s", "--strong", dest="strong_match", default=False,
                          action="store_true", help="Use strong mention match")
        parser.add_option("-b", "--best", dest="best", default=None,
                          help="Optimize metrics looking for best threshold")
        parser.add_option("--threshold", dest="threshold", default=0.0,
                          type="float", help="Threshold instances")
        parser.add_option("--optimize", dest="optimize",
                          default="macro_f1",
                          help="Target attribute to optimize")
        parser.add_option("--tablefmt", dest="tablefmt",
                          default="simple",
                          help="Format for the tables")
        parser.add_option("--recap", dest="recap", default=False,
                          action="store_true",
                          help="Report metrics for each document")
        parser.add_option("--detailed", dest="detailed", default=False,
                          action="store_true",
                          help="Print a detailed report for every document")

        (options, args) = parser.parse_args()

        self.print_recap = options.recap
        self.print_report = options.detailed
        self.use_strong_match = options.strong_match
        self.best = options.best
        self.threshold = options.threshold
        self.optimize = options.optimize
        self.tablefmt = options.tablefmt
        self.conf = conf = Configurations(options.configuration)

        if self.threshold > 0.0 and self.best is None:
            print "You did specify a threshold without best."
            self.threshold = 0.0

        for experiment_name, experiment in conf.experiments.items():
            rows = [[
                u"Dataset",
                u"Annotator",
                u"Total",
                u"TP",
                u"TN",
                u"FP",
                u"FN",
                u"μP",
                u"μR",
                u"μF1",
                u"P",
                u"R",
                u"F1",
            ]]

            if self.best or self.threshold:
                rows[-1].insert(2, "Threshold")
                rows[-1].insert(2, "Attr")

            for dataset_name, dataset in conf.datasets.items():
                for annotator_name, annotator in conf.annotators.items():
                    result_directory = os.path.join(
                        experiment.file, dataset_name, annotator_name
                    )
                    results = Dataset.load_results(result_directory)
                    t, m = self.report_for(experiment,
                                           results, dataset.instances)

                    rows.append([
                        dataset_name,
                        annotator_name,
                        m.tp + m.fn,
                        m.tp,
                        m.tn,
                        m.fp,
                        m.fn,
                        m.precision(),
                        m.recall(),
                        m.f1(),
                        m.macro_precision(),
                        m.macro_recall(),
                        m.macro_f1()
                    ])

                    if self.best or self.threshold:
                        rows[-1].insert(2, t)
                        rows[-1].insert(2, self.best)

            print tabulate(rows, headers="firstrow",
                           floatfmt=".3f", tablefmt=self.tablefmt)

    def report_for(self, experiment, actual_instances, golden_instances):
        methname = "cmp_mentions_%s_%s" % (
            experiment.name,
            self.use_strong_match and "strong" or "weak"
        )
        print "Using", methname
        compare = globals()[methname]

        m = Metrics()
        threshold = 0.0

        if self.best is not None:
            if self.threshold > 0.0:
                threshold = self.threshold
                actual_instances = self.threshold_instances(
                    self.threshold, actual_instances, golden_instances
                )
            else:
                threshold, actual_instances = self.find_best_threshold(
                    experiment, actual_instances, golden_instances
                )

        for ginstance, ainstance in izip_longest(golden_instances, actual_instances):
            if not ginstance or not ainstance:
                m.push(Metrics(fn=len(ginstance.mentions)))
                continue

            assert ginstance.instance_id == ainstance.instance_id
            gm = ginstance.mentions
            am = ainstance.mentions

            result = compare(gm, am)

            if self.print_report:
                result.full_report(ginstance.instance_id)
            if self.print_recap:
                print "%20s\t%s" % (ginstance.instance_id, result.summary())

            m.push(result.as_metric())

        return (threshold, m)

    def find_best_threshold(self, experiment,
                            actual_instances, golden_instances):

        ranges = [1/128.0 * i for i in range(0, 129)]

        best = 0
        best_value = 0

        for threshold in ranges:
            filtered_instances = self.threshold_instances(
                threshold, actual_instances
            )

            metric = self.evaluate(
                experiment, golden_instances, filtered_instances
            )

            value = getattr(metric, self.optimize)()

            # print threshold, value

            if value >= best_value:
                best_value = value
                best = threshold

        print "Thr: %3f Value: %.3f" % (best, best_value)

        instances = self.threshold_instances(
            best, actual_instances
        )

        return (best, instances)

    def evaluate(self, experiment, golden_instances, actual_instances):
        methname = "cmp_mentions_%s_%s" % (
            experiment.name,
            self.use_strong_match and "strong" or "weak"
        )
        compare = globals()[methname]

        m = Metrics()
        iterable = izip_longest(golden_instances, actual_instances)

        for ginstance, ainstance in iterable:
            if not ainstance:
                m.push(Metrics(fn=len(ginstance.mentions)))
                continue

            assert ginstance.instance_id == ainstance.instance_id
            gm = ginstance.mentions
            am = ainstance.mentions

            result = compare(gm, am)

            if self.print_report:
                result.full_report(ginstance.instance_id)
            if self.print_recap:
                print "%20s\t%s" % (ginstance.instance_id, result.summary())

            m.push(result.as_metric())

        return m

    def threshold_instances(self, threshold, actual_instances):
        instances = []

        for ainstance in actual_instances:
            fmentions = filter(
                lambda x: getattr(x, self.best) >= threshold,
                ainstance.mentions
            )
            instances.append(
                Instance(ainstance.text, fmentions, ainstance.instance_id)
            )

        return instances


if __name__ == "__main__":
    Reporter()
