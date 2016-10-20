import numpy as np


dataType = ('fix', 'int', 'bool')


class FixFile:
    """Class defining a file format used in vhdl test benches.

    File format:
    ---------- header
    nsf <numColumns> <numSamples>
    <colName_1>,<colName_2>, .. <colName_numColumns>
    <colType_1>,<colType_2>, .. <colType_numColumns>
    <spl_1_0>,<spl_2_0>, .. <spl_numColumns_0>
    ..
    <spl1_numSamples-1>,<spl2_numSamples-1>, .. <splk_numSamples-1>
    """

    def __init__(self):
        self._column = 0
        self._sample = 0
        self._colStruct = {}
        self._orderedColName = list()

    # file operations

    def read(self, filePath: str=None):
        """Read fix formatted file.

        If a file is read, write method will through an exceptions.
        File path has to be a relative/absolute path plus file name (extension,
        if any, included).
        """
        return NotImplemented

    def write(self, filePath: str=None):
        """Write fix formatted file.

        If a file is written, read method will through an exceptions.
        File path has to be a relative/absolute path plus file name (extension,
        if any, included).
        """
        
        return NotImplemented

    # methods

    def add_column(self,
                   colName: str,
                   colType: str,
                   colValue):
        """Add data column to file descriptor.

        If NxM matrix, data shape will be turned into 1xW, with W = N*M.
        All coulmns must have the same number of elements,
        otherwise no column will be added to file descriptor.

        :param colType: data type, can assume only 'fix', 'int', 'bool'
        :param colValue: data to add
        :type colValue: nsf_fix.FixNum, int or bool
        """
        # check type validity
        if colType not in dataType:
            raise ValueError("_ERROR_: column type can assume only \
'fix', 'int', 'bool' string values")

        # check if data is already added
        if (colName, colType) in self._colStruct.keys():
            raise KeyError("_ERROR_: '", colName, "' was already added")

        data = np.reshape(colValue, -1)
        if self._column == 0 or len(data) == self._sample:
            self._column += 1
            self._sample = len(data)
            self._colStruct[(colName, colType)] = data
            self._orderedColName.append((colName, colType))
        else:
            raise Warning("_WARNING_: data column lenght must be exactly \
equal to previously added columns (%d). Column not added." % self._sample)

    def remove_column(self,
                      colName,
                      colType: dataType):
        del self._colStruct[(colName, colType)]
        self._orderedColName.remove((colName, colType))
        self._column -= 1
        if self._column == 0:
            self._sample = 0

    def get_header(self, complete=False):
        if complete:
            return self._orderedColName
        else:
            return [key[0] for key in self._orderedColName]
