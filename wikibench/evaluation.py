from itertools import izip_longest
from wikibench.metrics import Metrics


class Result(object):
    def __init__(self, metric, correct, error, missing, excess):
        self.metric = metric
        self.correct = correct
        self.error = error
        self.missing = missing
        self.excess = excess
        self.correct_title = None

    def as_metric(self):
        return self.metric

    def tp(self):
        return len(self.correct)

    def fp(self):
        return len(self.error) + len(self.excess)

    def fn(self):
        return len(self.missing)

    def recoverable(self, easy=False):
        c = len(self.missing)

        for a in self.missing:
            for b in self.correct:
                if easy and a.wid == b.wid and a.spot == b.spot:
                    c -= 1
                    break
                elif not easy and a.wid == b.wid:
                    c -= 1
                    break
        return c

    def total(self):
        return self.tp() + self.fn()

    def correct_avg(self):
        # Coherence
        if len(self.correct) == 0:
            return 0.0
        return sum(map(lambda x: x.score2, self.correct)) / len(self.correct)

    def error_avg(self):
        # Coherence
        if len(self.error) == 0:
            return 0.0
        return sum(map(lambda x: x.score2, self.error)) / len(self.error)

    def excess_avg(self):
        # Coherence
        if len(self.excess) == 0:
            return 0.0
        return sum(map(lambda x: x.score2, self.excess)) / len(self.excess)

    def summary(self):
        return "TOT: %3d TP: %3d FN: %3d FP: %3d P: %.3f R: %.3f F1: %.3f CorrectAvg: %f ErrorAvg: %f ExcessAvg: %3f" % (
            self.total(), self.tp(), self.fn(), self.fp(),
            self.precision(), self.recall(), self.f1(),
            self.correct_avg(), self.error_avg(), self.excess_avg()
        )

    def precision(self):
        denom = self.tp() + self.fp()

        if denom == 0:
            return 0.0
        else:
            return 1.0 * self.tp() / denom

    def recall(self):
        denom = self.tp() + self.fn()

        if denom == 0:
            return 0.0
        else:
            return 1.0 * self.tp() / denom

    def f1(self):
        p = self.precision()
        r = self.recall()

        if p + r == 0:
            return 0
        else:
            return 2 * p * r / (p + r)

    def full_report(self, docname):
        lbl_correct = izip_longest(self.correct, [], fillvalue='ok')
        lbl_error = izip_longest(self.error, [], fillvalue='error')
        lbl_missing = izip_longest(self.missing, [], fillvalue='missing')
        lbl_excess = izip_longest(self.excess, [], fillvalue='excess')

        all_lbls = []
        all_lbls.extend(list(lbl_correct))
        all_lbls.extend(list(lbl_error))
        all_lbls.extend(list(lbl_missing))
        all_lbls.extend(list(lbl_excess))

        all_lbls.sort(key=lambda x: (x[0].start, x[0].end))

        for instance, lbl in all_lbls:
            if lbl == 'error':
                title = instance.title + "!=" + instance.correct_title
            else:
                title = instance.title

            if lbl == 'missing':
                if filter(lambda x: x.wid == instance.wid and x.spot == instance.spot, self.correct):
                    lbl = 'easy-recover'
                elif filter(lambda x: x.wid == instance.wid, self.correct):
                    lbl = 'hard-recover'
                else:
                    lbl = 'missing'

            print "%s\t%s\t%d\t%d\t%s\t%s\t%s\t%.3f\t%.3f" % (
                docname, lbl, instance.start, instance.end, instance.wid,
                title, instance.spot, instance.score1, instance.score2
            )

        print "%s\t%s\t%d\t%d\t%d\t%.3f\t%.3f\t%.3f" % (
            docname, 'SUM', self.tp(), self.fn(), self.fp(),
            self.precision(), self.recall(), self.f1()
        )


def compare_mentions(xa, xb, is_valid,
                     use_strong_match=True, take_first=True, count_fp=True):
    correct = set()
    error = set()
    missing = set()
    excess = set()

    error_tag = {}

    tp = 0
    fp = 0
    fn = 0

    for gold in xa:
        if use_strong_match:
            candidates = filter(
                lambda x: (x.start, x.end) == (gold.start, gold.end),
                xb
            )
        else:
            candidates = filter(
                lambda x: x.overlaps(gold),
                xb
            )

        candidates = sorted(candidates,
                            key=lambda x: (x.start, x.end - x.start))

        found = False

        for result in candidates:
            if is_valid(result, gold):
                found = True
            else:
                error_tag[result] = error_tag.get(result, 0) + 1

        if not found:
            fn += 1
            missing.add(gold)
        else:
            tp += 1

    for result in xb:
        if use_strong_match:
            candidates = filter(
                lambda x: (x.start, x.end) == (result.start, result.end),
                xa
            )
        else:
            candidates = filter(
                lambda x: result.overlaps(x),
                xa
            )

        candidates = sorted(candidates,
                            key=lambda x: (x.start, x.end))

        found = False

        for gold in candidates:
            if is_valid(result, gold):
                found = True
                correct.add(result)

        if not found:
            if error_tag.get(result, 0) == 1:
                result.correct_title = candidates[0]
                error.add(result)

            if candidates or count_fp:
                fp += 1
                excess.add(result)

    def sortset(x):
        return sorted(x, key=lambda x: (x.start, x.end))

    excess = excess.difference(error)

    # r_tp = len(correct)
    r_fp = len(excess) + len(error)
    r_fn = len(missing)

    # if r_tp != tp:
    #     print "TP: %d != %d" % (r_tp, tp)
    assert r_fp == fp, "%d != %d" % (r_fp, fp)
    assert r_fn == fn, "%d != %d" % (r_fn, fn)

    m = Metrics(tp=tp, fp=fp, fn=fn)
    return Result(m, *map(sortset, (correct, error, missing, excess)))


def cmp_mentions_spot_weak(xa, xb):
    return compare_mentions(xa, xb,
                            is_valid=lambda x, y: True,
                            use_strong_match=False)


def cmp_mentions_spot_strong(xa, xb):
    return compare_mentions(xa, xb,
                            is_valid=lambda x, y: True,
                            use_strong_match=True)


def cmp_mentions_sa2w_weak(xa, xb):
    return compare_mentions(
        xa, xb,
        is_valid=lambda x, y: x.wid == y.wid or x.title == y.title,
        use_strong_match=False
    )


def cmp_mentions_sa2w_strong(xa, xb):
    return compare_mentions(
        xa, xb,
        is_valid=lambda x, y: x.wid == y.wid or x.title == y.title,
        use_strong_match=True
    )


def cmp_mentions_d2w_weak(xa, xb):
    return compare_mentions(
        xa, xb,
        is_valid=lambda x, y: x.wid == y.wid or x.title == y.title,
        use_strong_match=False,
        count_fp=False
    )


def cmp_mentions_d2w_strong(xa, xb):
    return compare_mentions(
        xa, xb,
        is_valid=lambda x, y: x.wid == y.wid or x.title == y.title,
        use_strong_match=True,
        count_fp=False
    )
