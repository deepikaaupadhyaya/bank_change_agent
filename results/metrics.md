# Metrics (40 simulated cases; 32 Genuine / 8 Fraud)

## bayesian_cost_sensitive (n=40)
- Confusion: TP=8 FP=6 TN=26 FN=0
- Accuracy=0.85 Precision=0.571 Recall=1.0 F1=0.727
- False positives=6 False negatives=0
- Human-review rate=0.350 (verify=8, escalate=6)
- Total decision cost=$4,200 (fraud loss=$0, avg=$105/case)
- Calibration ECE=0.038; bins=[{'bin': [0.0, 0.2], 'n': 31, 'mean_pred': 0.006, 'empirical_rate': 0.0}, {'bin': [0.2, 0.5], 'n': 3, 'mean_pred': 0.346, 'empirical_rate': 0.667}, {'bin': [0.5, 0.8], 'n': 1, 'mean_pred': 0.78, 'empirical_rate': 1.0}, {'bin': [0.8, 1.01], 'n': 5, 'mean_pred': 0.966, 'empirical_rate': 1.0}]

## rule_checklist (n=40)
- Confusion: TP=8 FP=13 TN=19 FN=0
- Accuracy=0.675 Precision=0.381 Recall=1.0 F1=0.552
- False positives=13 False negatives=0
- Human-review rate=0.525 (verify=12, escalate=9)
- Total decision cost=$6,300 (fraud loss=$0, avg=$158/case)
- Calibration ECE=0.205; bins=[{'bin': [0.0, 0.2], 'n': 19, 'mean_pred': 0.113, 'empirical_rate': 0.0}, {'bin': [0.2, 0.5], 'n': 12, 'mean_pred': 0.34, 'empirical_rate': 0.0}, {'bin': [0.5, 0.8], 'n': 7, 'mean_pred': 0.599, 'empirical_rate': 0.857}, {'bin': [0.8, 1.01], 'n': 2, 'mean_pred': 0.92, 'empirical_rate': 1.0}]

## baseline_spf (n=40)
- Confusion: TP=1 FP=1 TN=31 FN=7
- Accuracy=0.8 Precision=0.5 Recall=0.125 F1=0.2
- False positives=1 False negatives=7
- Human-review rate=0.050 (verify=2, escalate=0)
- Total decision cost=$143,374 (fraud loss=$143,074, avg=$3,584/case)
- Calibration ECE=0.127; bins=[{'bin': [0.0, 0.2], 'n': 38, 'mean_pred': 0.05, 'empirical_rate': 0.184}, {'bin': [0.2, 0.5], 'n': 0, 'mean_pred': None, 'empirical_rate': None}, {'bin': [0.5, 0.8], 'n': 2, 'mean_pred': 0.5, 'empirical_rate': 0.5}, {'bin': [0.8, 1.01], 'n': 0, 'mean_pred': None, 'empirical_rate': None}]

## always_approve (n=40)
- Confusion: TP=0 FP=0 TN=32 FN=8
- Accuracy=0.8 Precision=0.0 Recall=0.0 F1=0.0
- False positives=0 False negatives=8
- Human-review rate=0.000 (verify=0, escalate=0)
- Total decision cost=$150,736 (fraud loss=$150,736, avg=$3,768/case)
- Calibration ECE=0.1; bins=[{'bin': [0.0, 0.2], 'n': 40, 'mean_pred': 0.1, 'empirical_rate': 0.2}, {'bin': [0.2, 0.5], 'n': 0, 'mean_pred': None, 'empirical_rate': None}, {'bin': [0.5, 0.8], 'n': 0, 'mean_pred': None, 'empirical_rate': None}, {'bin': [0.8, 1.01], 'n': 0, 'mean_pred': None, 'empirical_rate': None}]

## always_verify (n=40)
- Confusion: TP=8 FP=32 TN=0 FN=0
- Accuracy=0.2 Precision=0.2 Recall=1.0 F1=0.333
- False positives=32 False negatives=0
- Human-review rate=1.000 (verify=40, escalate=0)
- Total decision cost=$6,000 (fraud loss=$0, avg=$150/case)
- Calibration ECE=0.3; bins=[{'bin': [0.0, 0.2], 'n': 0, 'mean_pred': None, 'empirical_rate': None}, {'bin': [0.2, 0.5], 'n': 0, 'mean_pred': None, 'empirical_rate': None}, {'bin': [0.5, 0.8], 'n': 40, 'mean_pred': 0.5, 'empirical_rate': 0.2}, {'bin': [0.8, 1.01], 'n': 0, 'mean_pred': None, 'empirical_rate': None}]
