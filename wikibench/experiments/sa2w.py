from wikibench.experiment import Experiment


class SA2WExperiment(Experiment):
    def run(self, dataset, annotator, directory):
        not_cached = filter(lambda x: not x.has_been_processed(directory),
                            dataset)
        for instance in not_cached:
            mentions = annotator.annotate(instance)
            instance.save_mentions(directory, mentions)

__experiment__ = SA2WExperiment
