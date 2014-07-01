# What is wikibench?

Wikibench is a set of simple and self-contained python modules that are used for assessing the performance of entity annotators.

## What can I test?

Wikibench is organized in so called experiments, that are python scripts that describes how a test must be conducted. At the current moment the system supports three experiments:

  - *Spotting*: that measures the coverage of the spotter module of a given annotator.
  - *D2W*: that measures the disambiguation capability of a given annotator.
  - *SA2W*: that measures the full spotting and disambiguation pipeline of a given annotator.

All the experiments support the notion of *strong* and *weak* mention annotation match, as defined in [*A framework for benchmarking entity-annotation systems*](http://dl.acm.org/citation.cfm?id=2488411)

## What annotators are supported?

We support three annotators:

  - [TagME](http://tagme.di.unipi.it/)
  - [Wat](http://github.com/nopper/wat)
  - [AIDA](https://www.mpi-inf.mpg.de/departments/databases-and-information-systems/research/yago-naga/)

Of course you can easily write your own annotator backend. It is just a matter of minutes. You can take a look at the `annotators/` directory.

## How can I run the experiments?

Wikibench uses a simple JSON file to describe what experiments the specified annotator(s) must execute on the specified dataset(s). Here's a simple example:

    $ cat experiments/simple.json
    {
      "datasets": [
        {"name": "erd", "file": "datasets/tsv/erd"}
      ],
      "annotators": [
        {
          "name": "tagme",
          "alias": "tagme",
          "configuration": {
            "key": "*YOURKEYEXPERIMENT*"
          }
        }
      ],
      "experiments": [
        {"name": "sa2w", "file": "results/sa2w_erd"}
      ]
    }

In this example we are expressing the intention to test `TagME` against the `ERD` dataset, using the `SA2W` experiment. At this point you can simply run the experiment with:

    $ python wikibench/run_experiment.py -c experiments/simple.json
    
You can see the results of the experiment using the `report_experiment.py` script:

    $ python wikibench/report_experiment.py --best score1 -c experiments/simple.json
    Using cmp_mentions_sa2w_weak
    Thr: 0.242188 Value: 0.455
    Dataset    Annotator    Attr      Threshold    Total    TP    TN    FP    FN     μP     μR    μF1      P      R     F1
    ---------  -----------  ------  -----------  -------  ----  ----  ----  ----  -----  -----  -----  -----  -----  -----
    erd        tagme        score1        0.242     1160   575     0   644   585  0.472  0.496  0.483  0.481  0.513  0.455
    

## What dataset formats are supported?

Wikibench supports three different datasets format, namely:

  - TSV: a tab separated row containing:
    - `start`: Start offset (character offset) of the mention
    - `end`: End offset (character offset) of the mention
    - `wid`: Wikipedia ID of the entity
    - `title`: Title of the Wikipedia entity
    - `spot`: The mention text
    - `score1`: Confidence score
    - `score2`: Auxiliary confidence score (optional)
  - XML
  - PKL

In general the TSV format is the preferred one since it can be easily interpreted by humans.

