import logging
import os
import json
import re
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('starting ...')

cite_patt = re.compile(
    (r'\{\{cite:([0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}'
     r'-[89AB][0-9A-F]{3}-[0-9A-F]{12})\}\}'),
    re.I
)

# load citation contexts
base_path = './unarXive-cs-sentences'
cit_fn = './unarXive-2020-cs_classified_bert_sort_top50k.csv'
citing_contexts = []
list_idx = 0
with open(cit_fn) as f:
    sep = '\u241E'
    for i, line in enumerate(f):
        if i == 0:
            continue  # skip header
        vals = line.split(sep)
        cited_arxiv_id = vals[6]
        cited_ppr_fn = cited_arxiv_id.replace('/', '') + '.txt'
        cited_ppr_fp = os.path.join(base_path, cited_ppr_fn)
        if not os.path.isfile(cited_ppr_fp):
            continue
        citing_contexts.append(
            {
                'list_idx': list_idx,
                'orig_df_id': vals[2],
                'cited_arxiv_id': cited_arxiv_id,
                'citing_arxiv_id': vals[8],
                'citing_context': vals[9]
            }
        )
        list_idx += 1


def get_existing_annotations_info():
    existing_annots_dict = dict()
    for fn in os.listdir('.'):
        fn_base, ext = os.path.splitext(fn)
        if ext == '.json':
            annotator_id = fn_base
            with open(fn) as f:
                annots_dict = json.load(f)
                for annot in annots_dict['annotations']:
                    idx = annot['citing_context_list_idx']
                    if idx not in existing_annots_dict:
                        existing_annots_dict[idx] = []
                    existing_annots_dict[idx].append(annotator_id)
    return existing_annots_dict


def get_annotations_count(annotator_id):
    annot_fn = annotator_id + '.json'
    if not os.path.isfile(annot_fn):
        return 0
    else:
        with open(annot_fn) as f:
            annotations_dict = json.load(f)
            return len(annotations_dict['annotations'])


def get_annotations_sentence_idxs(annotator_id, cited_arxiv_id):
    annot_fn = annotator_id + '.json'
    if not os.path.isfile(annot_fn):
        return []
    else:
        with open(annot_fn) as f:
            annotations_dict = json.load(f)
            sentence_idxs = []
            for annot in annotations_dict['annotations']:
                if annot['cited_arxiv_id'] == cited_arxiv_id:
                    # pick last in case of re-done annotations
                    sentence_idxs = annot['cited_sentence_idx_list']
    return sentence_idxs


def save_annotations(
    annotator_id,
    citing_contexts,
    citing_sentence_idx,
    cited_sentence_idx_list
):
    annot_fn = annotator_id + '.json'
    if os.path.isfile(annot_fn):
        with open(annot_fn) as f:
            annotations_dict = json.load(f)
    else:
        annotations_dict = {
            'annotator_id': annotator_id,
            'annotations': []
        }
    citing_context = citing_contexts[citing_sentence_idx]
    full_text_sentences = get_full_text_sentences(
        citing_context['cited_arxiv_id']
    )
    cited_sentences = [
        full_text_sentences[idx] for idx in
        cited_sentence_idx_list
    ]

    annotations_dict['annotations'].append({
        'citing_arxiv_id': citing_context['citing_arxiv_id'],
        'citing_context_list_idx': citing_context['list_idx'],
        'citing_context': citing_context['citing_context'],
        'cited_arxiv_id': citing_context['cited_arxiv_id'],
        'cited_sentence_idx_list': cited_sentence_idx_list,
        'cited_sentences': cited_sentences
    })
    with open(annot_fn, 'w') as f:
        json.dump(annotations_dict, f)


def get_full_text_sentences(arxiv_id):
    fpath_txt = os.path.join(base_path, arxiv_id) + '.txt'
    with open(fpath_txt) as f:
        full_text_lines = f.readlines()
    sentences = [
        l[6:-6].strip() for l in full_text_lines  # strip Bert tokens
    ]
    return sentences


@app.route('/')
def index():
    return render_template(
        'index.html',
    )


@app.route('/citing', methods=['GET', 'POST'])
def pick_citing_sentence():
    annotator_id = request.form.get('annotator_id')
    if annotator_id is None or len(annotator_id) == 0:
        annotator_id = request.args.get('annotator_id')
    if annotator_id is None or len(annotator_id) == 0:
        return redirect('/')
    # save annotations
    if '/cited' in request.headers.get('Referer', default=''):
        cited_sentence_idx_list = [
            int(idx) for idx in
            request.form.getlist('cited_sentences')
        ]
        citing_sentence_idx = request.form.get('citing_sentence', type=int)
        save_annotations(
            annotator_id,
            citing_contexts,
            citing_sentence_idx,
            cited_sentence_idx_list
        )

    page = request.form.get('page', type=int)
    if page is None:
        page = request.args.get('page', type=int)
    contexts_per_page = 25
    idx_start = page*contexts_per_page
    idx_end = idx_start + contexts_per_page
    annotated_num = get_annotations_count(annotator_id)
    existing_annots_dict = get_existing_annotations_info()

    return render_template(
        'pick_citing.html',
        annotator_id=annotator_id,
        annotated_num=annotated_num,
        page=page,
        page_contexts=citing_contexts[idx_start:idx_end],
        existing_annots_dict=existing_annots_dict
    )


@app.route('/cited')
def pick_cited_sentence():
    page = request.args.get('page', type=int)
    annotator_id = request.args.get('annotator_id')
    annotated_num = get_annotations_count(annotator_id)
    context_list_idx = request.args.get('list_idx', type=int)
    citing_context = citing_contexts[context_list_idx]
    full_text_sentences = get_full_text_sentences(
        citing_context['cited_arxiv_id']
    )

    annotated_sentence_idxs = get_annotations_sentence_idxs(
        annotator_id,
        citing_context['cited_arxiv_id']
    )

    return render_template(
        'pick_cited.html',
        annotated_num=annotated_num,
        return_page=page,
        citing_sentence=context_list_idx,
        annotator_id=annotator_id,
        citing_context=citing_context,
        full_text_sentences=full_text_sentences,
        annotated_sentence_idxs=annotated_sentence_idxs
    )
