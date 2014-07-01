from wikibench.dataset import AIDADataset, Dataset
from wikibench.utils import create_annotator


def reshape_dataset(annotator, src_file_name, output):
    """
    Reshape dataset once and for all
    """
    print "Reading dataset from %s" % src_file_name
    needs_reshape = True

    if src_file_name.endswith(".pkl"):
        dataset = Dataset.load(src_file_name)
        needs_reshape = False
    else:
        dataset = AIDADataset.read(src_file_name)

    print "Dataset loaded: %s" % dataset

    if needs_reshape:
        print "Reshaping dataset using %s" % annotator
        annotator.reshape(dataset)

    if output.endswith(".pkl"):
        Dataset.save(dataset, output)
    elif output.endswith(".xml"):
        Dataset.save_xml(dataset, output)
    else:
        Dataset.save_tsv(dataset, output)

    print "Dataset successfully saved in %s" % output

if __name__ == "__main__":
    import sys
    annotator_name, src_file_name, dst_file_name = sys.argv[1:]
    annotator = create_annotator(annotator_name)
    reshape_dataset(annotator, src_file_name, dst_file_name)
