from math import log
from typing import Sequence, Any

from jina.executors.evaluators.rank import BaseRankingEvaluator

class NDCGEvaluator(BaseRankingEvaluator):
    """
    :class:`NDCGEvaluator` evaluates normalized discounted cumulative gain for information retrieval.
    """

    @property
    def metric(self):
        return f'nDCG@{self.eval_at}'

    def evaluate(
            self,
            actual: Sequence[Any],
            desired: Sequence[Any],
            use_traditional_formula=False,
            *args, **kwargs
    ) -> float:
        """"
        :param actual: the scores predicted by the search system.
        :param desired: the expected score given by user as groundtruth.
        :param use_traditional_formula: if use traditional formula.
            The new formula places stronger emphasis on retrieving relevant documents.
            For detailed information, please check https://en.wikipedia.org/wiki/Discounted_cumulative_gain
        :return the evaluation metric value for the request document.
        """
        actual_at_k = actual[:self.eval_at]
        desired_at_k = desired[:self.eval_at]
        if len(actual) < 2:
            raise ValueError(f'Expecting gains with minimal length of 2, {len(actual)} received.')
        dcg  = self._compute_dcg(gains=actual_at_k, use_traditional_formula=use_traditional_formula)
        idcg = self._compute_idcg(gains=desired_at_k, use_traditional_formula=use_traditional_formula)
        return 0.0 if idcg == 0.0 else dcg/idcg

    def _compute_dcg(self, gains, use_traditional_formula):
        """Compute discounted cumulative gain."""
        ret = 0.0
        if use_traditional_formula:
            for score, position in zip(gains[1:], range(2, len(gains) + 1)):
                ret += score/log(position, 2)
            return gains[0] + ret
        for score, position in zip(gains, range(1, len(gains) + 1)):
            ret += (pow(2, score) - 1)/log(position + 1, 2)
        return ret

    def _compute_idcg(self, gains, use_traditional_formula):
        """Compute ideal discounted cumulative gain."""
        sorted_gains = sorted(gains, reverse=True)
        return self._compute_dcg(sorted_gains, use_traditional_formula)