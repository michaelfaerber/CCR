import json

annot_records = dict()
for uid in ['tsa', 'syu']:
    with open(uid + '.json') as f:
        annot_records[uid] = json.load(f)

annots_merged = dict()
for uid, annot_record in annot_records.items():
    for annot in annot_record['annotations']:
        context_id = '{}+{}'.format(
            annot['citing_arxiv_id'],
            annot['citing_context_list_idx']
        )
        if context_id not in annots_merged:
            annots_merged[context_id] = dict()
        annots_merged[context_id][uid] = annot

annots_both = dict()
for key, annot_dict in annots_merged.items():
    if len(annot_dict.keys()) == 2:
        annots_both[key] = annot_dict

with open('annotations_merged.json', 'w') as f:
    json.dump(annots_both, f)
