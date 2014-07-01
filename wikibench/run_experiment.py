import os
from optparse import OptionParser
from wikibench.configurations import Configurations


def main():
    parser = OptionParser()
    parser.add_option("-c", "--conf", dest="configuration",
                      help="Configuration file in json format", metavar="FILE",
                      default="configurations.json")

    (options, args) = parser.parse_args()

    conf = Configurations(options.configuration)

    for experiment_name, experiment in conf.experiments.items():
        for dataset_name, dataset in conf.datasets.items():
            for annotator_name, annotator in conf.annotators.items():
                output_directory = os.path.join(
                    experiment.file,
                    dataset_name,
                    annotator_name
                )

                print "Running %s on %s using %s" % (
                    experiment_name, dataset_name, annotator_name
                )

                experiment.run(dataset, annotator, output_directory)

if __name__ == "__main__":
    main()
