import os
from itertools import izip_longest, chain
from wikibench.experiment import Experiment
from wikibench.evaluation import cmp_mentions_sa2w_weak


class SA2WFeExperiment(Experiment):
    def run(self, dataset, annotator, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = os.path.join(directory, '%s.svmlight' % dataset.name)

        with open(file_name, 'w') as output:
            for instance in dataset:
                amentions = annotator.spot(instance)
                gmentions = instance.mentions

                result = cmp_mentions_sa2w_weak(gmentions, amentions)

                values = chain(
                    izip_longest(result.correct, [], fillvalue='1'),
                    izip_longest(result.excess, [], fillvalue='-1')
                )

                for mention, label in values:
                    output.write("%s %s\n" % (
                        label, mention.spot_features_svmlight()
                    ))

__experiment__ = SA2WFeExperiment
