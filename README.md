# Claim-based Citation Recommendation

Citation recommendation refers to the task of recommending appropriate citations for a text passage within a document. Although dozens of approaches to citation recommendation have been proposed, they actually do not consider the semantics of the claims to be backed up. In this proposed shared task, we propose the task which given an input claim consists of finding the text passages in other documents that match with the input claim. We will provide a novel dataset consisting of scientific publications' fulltexts. The task and the approaches to be developed will pave the way toward a new generation of citation recommendation, and will promote research concerning natural language processing (e.g., claim extraction), knowledge representation (e.g., claim-centric knowledge graphs), and machine learning.

<img align="middle" src="data_example.png" alt="data example" width="400"/>

## Experiments

We implemented basic experiments based on 20 annotated citation context. 

Approach: 
1. Extracting the representation of citation context and all the cited sentences from a pre-trained language model, e.g.: BERT, DistilBERT, RoBERTa. 
2. Calculating the cosine similatiry between citation context and cited sentences.
3. Based on manual inspection, defining a threshold for the
    cosine similarity (we defined 0.90), above which a sentence will be predicted as
    positive.
   
4. Calculating Prec/Rec/F1 based on the binary predicted labels and
    our ground truth.
   
The code can be found [here](/experiments/calculate_cosine_similarity.ipynb).

### Data
Data used in the experiments:

[Annotation agreement of 20 citation context](/experiments/data/annotations_agreement_20.json)

[Cited papers](/experiments/data/cited_papers_20.json)

Cosine similarity between citation context and cited sentences by:
+ [BERT](/experiments/data/context_and_score_bert.json)

+ [DistilBERT](/experiments/data/context_and_score_distilbert.json)

+ [RoBERTa](/experiments/data/context_and_score_roberta.json)

+ [BERT: pretrained with 20 cited papers](/experiments/data/context_and_score_bert_pre-trained.json)

### Results
The preliminary results of the experiments:

.csv: The cosine similarity of citation context and each cited sentences (ranked by cosine similarity).

.png: The Prec/Rec/F1 based on the binary predicted labels and
    our ground truth.

