import logging
from optparse import OptionParser
from wikibench.metrics import Metrics

FORMAT = '%(levelname)s - %(name)s - %(message)s'
logging.basicConfig(format=FORMAT)


class Benchmark(object):
    def __init__(self, loglevel=logging.INFO):
        self.metrics = Metrics()
        self.name = self.__class__.__name__
        self.log = logging.getLogger(self.name)
        self.log.setLevel(loglevel)

        self.parser = OptionParser("%s" % self.name)
        self.parser.add_option("-s", "--slice", dest="slice", default="",
                               help="Slice the input dataset")
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true", default=False,
                               help="Produce more messages")
        # self.parser.add_option("--shuffle", dest="shuffle",
        #                        action="store_true", default=False,
        #                        help="Shuffle dataset")

        self.opt_slice = []
        self.opt_verbose = []
        # self.opt_shuffle = False

        self.reset()

    def parse_arguments(self, arguments):
        (option, unparsed_args) = self.parser.parse_args(arguments)
        self.parse_options(option)
        return unparsed_args

    def parse_options(self, option):
        self.opt_verbose = option.verbose
        self.opt_slice = map(int, filter(lambda x: x, option.slice.split(':')))
        # self.opt_shuffle = option.shuffle

        if self.opt_verbose:
            self.log.setLevel(logging.DEBUG)

    def reset(self):
        self.metrics = Metrics()

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)

    def run(self, dataset, annotator):
        self.log.info("Running %s using %s on %s" % (self, annotator, dataset))

        results = []

        # Apply optional slicing if requested
        if self.opt_slice:
            start = self.opt_slice[0]
            end = len(dataset)

            if len(self.opt_slice) > 1:
                end = min(end, self.opt_slice[1])

            dataset = dataset[start:end]

        for instance in dataset:
            try:
                result = self.run_instance(annotator, instance)
                results.append(result)
            except Exception, exc:
                message = "Error processing instance %d (%s)" % (
                    instance.instance_id, instance.text
                )

                self.log.error(message)
                self.log.exception(exc)

        self.interpret_results(annotator, results)

    def run_instance(self, annotator, instance):
        raise NotImplemented

    def interpret_results(self, annotator, results):
        pass

    def summary(self):
        count_msg = "[TOT: %d TP: %d TN: %d FP: %d FN: %d]" % (
            self.metrics.tp + self.metrics.fn,
            self.metrics.tp, self.metrics.tn, self.metrics.fp, self.metrics.fn
        )

        micro_msg = "[micro P: %.3f R: %.3f F1: %.3f]" % (
            self.metrics.precision(), self.metrics.recall(), self.metrics.f1()
        )

        if self.metrics.has_macro():
            macro_msg = " [macro P: %.3f R: %.3f F1: %.3f]" % (
                self.metrics.macro_precision(),
                self.metrics.macro_recall(),
                self.metrics.macro_f1()
            )
        else:
            macro_msg = ""

        self.log.info("%s %s%s" % (count_msg, micro_msg, macro_msg))

if __name__ == "__main__":
    import sys
    from wikibench.dataset import Dataset
    from wikibench.utils import create_annotator, create_benchmark

    benchmark_name, annotator_name, dataset = sys.argv[1:4]

    dataset = Dataset.load(dataset)
    annotator = create_annotator(annotator_name)
    benchmark = create_benchmark(benchmark_name)

    benchmark.parse_arguments(sys.argv[4:])
    benchmark.run(dataset, annotator)
    benchmark.summary()
