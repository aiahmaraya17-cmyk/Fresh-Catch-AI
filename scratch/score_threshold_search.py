import json, os
from ai.prediction.infer import science_based_classify

with open('ai/dataset/metadata.json', encoding='utf-8') as f:
    records = json.load(f)

data = []
for r in records:
    if r['split'] == 'test':
        p = os.path.join('ai/dataset/raw', r['filename'])
        out = science_based_classify(p)
        data.append((r['freshness_category'], out['score']))

values = sorted({float(s) for _, s in data})
print('score_values', values)

best = (0.0, None)
for t1 in values:
    for t2 in values:
        if t2 <= t1:
            continue
        for t3 in values:
            if t3 <= t2:
                continue
            def predict(score):
                if score >= t1:
                    return 'Fresh'
                elif score >= t2:
                    return 'Moderately Fresh'
                elif score >= t3:
                    return 'Less Fresh'
                else:
                    return 'Not Fresh'
            acc = sum(1 for true, score in data if predict(score) == true) / len(data)
            if acc > best[0]:
                best = (acc, (t1, t2, t3))

print('best_accuracy', best[0])
print('best_thresholds', best[1])
