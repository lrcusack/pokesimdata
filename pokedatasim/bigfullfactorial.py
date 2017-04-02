from loggable import Loggable
import numpy as np


class BigFullFactorial(Loggable):
    """Class to define a full factorial experimental design with too many cases for storing them as a data frame"""

    def __init__(self, levels):
        self.levels = levels
        ncases = np.prod(levels)
        self.idxrange = range(ncases)
        self.dbg('levels: ' + str(levels) + ' -- number of cases: ' + str(ncases))

    def get_case_from_index(self, idx):
        """Method for defining cases based on an index
        like a de-hash function"""
        if idx not in self.idxrange:
            return None
        remainder = idx
        case = []
        for i in range(len(self.levels)):
            divisor = np.prod(self.levels[i:]) / self.levels[i]
            case.append(int(remainder // divisor))
            remainder %= divisor
        self.dbg('index: ' + str(idx) + ' -- case: ' + str(case))
        return case

    def get_index_from_case(self, case):
        """Method for defining an index for a given case
        like a hash function"""
        result_idx = 0
        for idx in range(len(case)):
            if case[idx] not in range(self.levels[idx]):
                return None
            result_idx += case[idx] * np.prod(self.levels[idx:]) / self.levels[idx]
        result_idx = int(result_idx)
        self.dbg('case: ' + str(case) + ' -- index: ' + str(result_idx))
        return result_idx
