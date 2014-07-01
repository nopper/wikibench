class Metrics(object):
    def __init__(self, fp=0, fn=0, tp=0, tn=0):
        # Just as recap:
        # FP: non c'e' ma la becco
        # FN: c'e' e non la becco
        # TP: c'e' e la becco
        # TN: non c'e' e non la becco

        self.fp = fp
        self.fn = fn
        self.tp = tp
        self.tn = tn
        self.metrics = []

    def clone(self):
        m = Metrics(fp=self.fp, fn=self.fn, tp=self.tp, tn=self.tn)
        m.metrics = map(
            lambda x: Metrics(fp=x.fp, fn=x.fn, tp=x.tp, tn=x.tn),
            self.metrics
        )
        return m

    def precision(self, k=1):
        denom = self.tp + self.fp

        if denom == 0:
            return 0.0
        else:
            return 1.0 * self.tp / denom

    def recall(self, k=1):
        denom = self.tp + self.fn

        if denom == 0:
            return 0.0
        else:
            return 1.0 * self.tp / denom

    def f1(self):
        p = self.precision()
        r = self.recall()

        if p + r == 0:
            return 0
        else:
            return 2 * p * r / (p + r)

    def has_macro(self):
        return len(self.metrics) > 0

    def macro_f1(self):
        if not self.metrics:
            return 0
        f1_sum = sum(map(lambda x: x.f1(), self.metrics))
        return float(f1_sum) / len(self.metrics)

    def macro_precision(self):
        if not self.metrics:
            return 0
        precision_sum = sum(map(lambda x: x.precision(), self.metrics))
        return float(precision_sum) / len(self.metrics)

    def macro_recall(self):
        if not self.metrics:
            return 0
        recall_sum = sum(map(lambda x: x.recall(), self.metrics))
        return float(recall_sum) / len(self.metrics)

    def push(self, other):
        self.fp += other.fp
        self.fn += other.fn
        self.tp += other.tp
        self.tn += other.tn
        self.metrics.append(other)
