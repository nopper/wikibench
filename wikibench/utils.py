import os


def instantiate_class(package, module, attribute, *args, **kwargs):
    mod = __import__(package, fromlist=[module])
    mod = getattr(mod, module)
    kls = getattr(mod, attribute)
    return kls(*args, **kwargs)


def create_benchmark(module):
    return instantiate_class('wikibench.benchmarks', module, '__benchmark__')


def create_experiment(module, *args, **kwargs):
    return instantiate_class(
        'wikibench.experiments', module, '__experiment__', *args, **kwargs)


def create_annotator(module, *args, **kwargs):
    annotator = instantiate_class(
        'wikibench.annotators', module, '__annotator__', *args, **kwargs)

    conf_file = '%s.json' % module

    if os.path.exists(conf_file):
        annotator.load_configuration_from(conf_file)

    return annotator
