class Experiment(object):
    def __init__(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            setattr(self, k, v)

    def run(self, dataset, annotator, directory):
        pass
