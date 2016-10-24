import numpy as np
import nsf_fix as fi

dataType = {'float': '%f',
            'fix': '%d',
            'int': '%d',
            'bool': '%d'}


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
        with open(filePath, mode='w', encoding='utf-8') as f:
            # global info
            f.write("nsf {} {}".format(self._column, self._sample))
            f.write('\n')
            # column names and type
            f.write(';'.join([x[0] for x in self._orderedColName]))
            f.write('\n')
            f.write(';'.join([x[1] if x[1] != 'fix' else
                              str(self._colStruct[x].fmt)
                              for x in self._orderedColName]))
            f.write('\n')
        # prepare data to be written into file
        dataToWrite = np.array([self._colStruct[x] if x[1] != 'fix' else
                                self._colStruct[x].int()
                                for x in self._orderedColName])
        # create format list
        fmtList = [dataType[x[1]] for x in self._orderedColName]
        # write data
        with open(filePath, mode='ab') as f:
            np.savetxt(f, dataToWrite.T, fmt=fmtList, delimiter=';')

    # methods

    def add_column(self,
                   colName: str,
                   colType: str,
                   colValue):
        """Add data column to file descriptor.

        Data must be provided in 1xN or Nx1 format
        All coulmns must have the same number of elements,
        otherwise no column will be added to file descriptor.

        :param colType: data type, can assume only 'fix', 'int', 'bool'
        :param colValue: data to add
        :type colValue: nsf_fix.FixNum, int or bool
        """
        # check type validity
        if colType not in dataType.keys():
            raise ValueError("_ERROR_: column type can assume only \
'fix', 'int', 'bool' string values")

        # check if data is already added
        if colName in self._get_col_names():
            raise KeyError("_ERROR_: '", colName, "' was already added")

        # check data dimension
        if colType == 'fix':
            if len(colValue.shape) != 1:
                raise ValueError("_ERROR_: data shape must be 1xN or Nx1.")
        elif len(np.array(colValue).shape) != 1:
            raise ValueError("_ERROR_: data shape must be 1xN or Nx1.")

        # check samples number
        if self._column == 0 or len(colValue) == self._sample:
            self._column += 1
            self._sample = len(colValue)
            self._colStruct[(colName, colType)] = colValue  # data
            self._orderedColName.append((colName, colType))
        else:
            raise Warning("_WARNING_: data column lenght must be exactly \
equal to previously added columns (%d). Column not added." % self._sample)

    def get_column(self, colName: str):
        """Get data column by name.
        """
        return self._colStruct[self._get_col_by_name(colName)]
        # return NotImplemented

    def remove_column(self,
                      colName):
        """Remove column data by name.
        """
        del self._colStruct[self._get_col_by_name(colName)]
        self._orderedColName.remove(self._get_col_by_name(colName))
        self._column -= 1
        if self._column == 0:
            self._sample = 0

    def get_header(self, complete=False):
        """Get data header.

        If complete switch is 'True', a series of tuple will be returned in the
        form (colName, colType). Otherwise the list of column names is returned
        """
        if complete:
            return self._orderedColName
        else:
            return self._get_col_names()

    def _get_col_names(self):
        """Extract only column names without data type.
        """
        return [key[0] for key in self._orderedColName]

    def _get_col_by_name(self, colName):
        colNameTypeTuple = self._get_col_names().index(colName)
        return self._orderedColName[colNameTypeTuple]
