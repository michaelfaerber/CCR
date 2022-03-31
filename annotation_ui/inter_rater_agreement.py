import os
import json
from sklearn.metrics import cohen_kappa_score

with open('annotations_merged.json') as f:
    all_annots_dict = json.load(f)

full_text_base_bath = './unarXive-cs-sentences/'

all_annotation_labels = []
num_annotations = len(all_annots_dict)
for context_id, single_context_annot_dict in all_annots_dict.items():
    # get all annotator’s annotations for one citation context
    annotator_ids = []
    annotation_dicts = []
    for annotator_id, annotator_dict in single_context_annot_dict.items():
        annotator_ids.append(annotator_id)
        annotation_dicts.append(annotator_dict)
        all_annotation_labels.append([])
    cited_arxiv_id = single_context_annot_dict[
        annotator_ids[0]
    ]['cited_arxiv_id']

    # determine number of labels in cited doc (=number of sentences)
    cited_arxiv_fn = cited_arxiv_id.replace('/', '') + '.txt'
    cited_arxiv_path = os.path.join(
        full_text_base_bath,
        cited_arxiv_fn
    )
    with open(cited_arxiv_path) as f:
        cited_doc_lines = f.readlines()

    # create labels (all zeros with 1s placed where annotations were made)
    for i, annotation_dict in enumerate(annotation_dicts):
        labels = [0]*len(cited_doc_lines)
        for idx in annotation_dict['cited_sentence_idx_list']:
            labels[idx] = 1
        all_annotation_labels[i].extend(labels)

# calculate inter-rater agreement
kappa = cohen_kappa_score(
    all_annotation_labels[0],
    all_annotation_labels[1]
)

print(
    (
     f'Cohen’s kappa: {kappa:.2f} '
     f'(based on {len(all_annotation_labels[0])} annotations '
     f'from {num_annotations} citation contexts)'
    )
)
