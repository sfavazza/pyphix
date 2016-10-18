import numpy as np
from enum import Enum


class dataType(Enum):
    """Fix file column data type
    """
    fix = 0
    int = 1
    bool = 2


class FixFile:
    """Class defining a file format used in vhdl test benches.

    If file path is indicated, file descriptor will be initialized with data
    read from indicated file. Data can be read but not added.
    If not indicated data can be added and written to file using 'write'
    method.
    File path has to be a relative/absolute path plus file name (extension, if
    any, included).
    :file
    """

    def __init__(self, filePath: str=None):
        self._column = 0
        self._sample = 0
        self._colStruct = {}
        self._orderedColName = list()
        self.filePath = filePath

    # file operations

    def _read(self):
        return NotImplemented

    def write(self):
        return NotImplemented

    # methods

    def add_column(self,
                   colName: str,
                   colType: dataType,
                   colValue):
        """Add data column to file descriptor.

        If NxM matrix, data shape will be turned into 1xW, with W = N*M.
        All coulmns must have the same number of elements,
        otherwise no column will be added to file descriptor.

        :param colValue: data to add
        :type colValue: fix, int or bool
        """
        data = np.reshape(colValue, -1)
        if self._column == 0:
            self._colStruct[(colName, colType)] = data
            self._orderedColName.append((colName, colType))
        elif len(data) == self._column:
            self._colStruct[(colName, colType)] = data
            self._orderedColName.append((colName, colType))

    def remove_column(self,
                      colName,
                      colType: dataType):
        del self._colStruct[(colName, colType)]
        self._orderedColName.remove((colName, colType))

    def get_header(self, complete=False):
        if complete:
            return list(self._colStruct.keys())
        else:
            return [key[0] for key in self._colStruct.keys()]
