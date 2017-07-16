import ast
import numpy as np

import nsf_fix as fi
import nsf_fix_util as fu

dataType = {'float': '%s',
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

    NOTE: data written in the file can be used as stimuli in the test benches
    only if data channels are synchronous.
    Otherwise separate files should be used.
    """

    def __init__(self):
        self._column = 0
        self._sample = 0
        self._colStruct = dict()
        self._orderedColName = list()

    # file operations

    def read(self, filePath: str=None):
        """Read fix formatted file.

        If a file is read, write method will through an exceptions.
        File path has to be a relative/absolute path plus file name (extension,
        if any, included).
        """
        with open(filePath, mode='r', encoding='utf-8') as f:
            # identify file type
            header = f.readline().split(' ')
            if header[0] != 'nsf':
                raise ValueError("_ERROR_: file '", filePath,
                                 "' is not valid nsf fix format file.")

            # info on data
            self._column = int(header[1])
            self._sample = int(header[2])
            # column names and types
            lineContent = f.readline()[:-1].replace(' ', ',')
            colName = ast.literal_eval('[' + lineContent + ']')
            lineContent = f.readline()[:-1].replace(' ', ',')
            colType = ast.literal_eval('[' + lineContent + ']')
            self._orderedColName = [(colName[i], colType[i])
                                    if type(colType[i]) is not tuple else
                                    (colName[i], 'fix')
                                    for i in range(0, self._column)]
            # data extraction
            fileContent = f.read()[:-1].replace('\n', '],[')
            rawData = ast.literal_eval('[[' +
                                       fileContent.replace(' ', ',') +
                                       ']]')
            shapedData = np.array(rawData).T
            # store into file descriptor (use default fimath)
            self._colStruct = {self._orderedColName[k]:
                               fi.FixNum(
                                   shapedData[k] * 2**(-colType[k][2]),
                                   fu.FixFmt(colType[k][0],
                                             colType[k][1],
                                             colType[k][2]))
                               if self._orderedColName[k][1] == 'fix' else
                               shapedData[k] > 0
                               if self._orderedColName[k][1] == 'bool' else
                               shapedData[k]
                               for k in range(0, self._column)}

    def write(self, filePath: str=None):
        """Write fix formatted file.

        If a file is written, read method will through an exceptions.
        File path has to be a relative/absolute path plus file name (extension,
        if any, included).
        """
        with open(filePath, mode='wb') as f:
            # global info
            strToWrite = "nsf {} {}".format(self._column, self._sample)
            f.write(strToWrite.encode('ascii'))
            f.write(b'\n')
            # column names and type (write them as literal string with apices)
            strToWrite = ' '.join(["'" + x[0] + "'"
                                   for x in self._orderedColName])
            f.write(strToWrite.encode('ascii'))
            f.write(b'\n')
            strToWrite = ' '.join(["'" + x[1] + "'" if x[1] != 'fix' else
                                   str(self._colStruct[x].fmt.tuple())
                                   .replace(' ', '')
                                   for x in self._orderedColName])
            # remove spaces
            # strToWrite = strToWrite.replace(' ', '')
            f.write(strToWrite.encode('ascii'))
            f.write(b'\n')
            # prepare data to be written into file
            dataToWrite = np.array([self._colStruct[x] if x[1] != 'fix' else
                                    [str(fixHex) for fixHex in
                                     self._colStruct[x].hex()]
                                    for x in self._orderedColName])
            # write data
            for line in dataToWrite.T:
                strToWrite = str(line)[2:-2].replace("' '", ' ') + '\n'
                f.write(strToWrite.encode('ascii'))

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
            # always convert to np.array
            if colType != 'fix':
                self._colStruct[(colName, colType)] = np.array([x for x in
                                                                colValue])
            else:
                self._colStruct[(colName, colType)] = colValue

            self._orderedColName.append((colName, colType))
            # allows to continue applying methods in sequence
            return self
        else:
            raise Warning("_WARNING_: data column lenght must be exactly \
equal to previously added columns (%d). Column not added." % self._sample)

    def get_column(self, colName: str):
        """Get data column by name.
        """
        return self._colStruct[self._get_col_by_name(colName)]

    def remove_column(self,
                      colName):
        """Remove column data by name.
        """
        del self._colStruct[self._get_col_by_name(colName)]
        self._orderedColName.remove(self._get_col_by_name(colName))
        self._column -= 1
        if self._column == 0:
            self._sample = 0
        # allows to continue applying methods in sequence
        return self

    def get_header(self, complete=False):
        """Get data header.

        If complete switch is 'True', a series of tuple will be returned in the
        form (colName, colType). Otherwise the list of column names is returned
        """
        if self._orderedColName == []:
            raise Warning('_WARNING_: file object is empty.')
        elif complete:
            return self._orderedColName
        else:
            return self._get_col_names()

    # private methods

    def _get_col_names(self):
        """Extract only column names without data type.
        """
        return [key[0] for key in self._orderedColName]

    def _get_col_by_name(self, colName):
        colNameTypeTuple = self._get_col_names().index(colName)
        return self._orderedColName[colNameTypeTuple]

    def _convert_str2data(self, colParams, colData):
        """Convert read string data.

        Each data column is converted according to the column type.
        If not valid type is found an Error exception is thrown.
        """
        if colParams[1] == 'float':
            return self._str2float(colData)
        elif colParams[1] == 'int':
            return self._str2int(colData)
        elif colParams[1] == 'bool':
            return self._str2int(colData)
        else:
            return self._str2fix(colParams, colParams)

    def _str2float(self, colData):
        return np.array([float(x) for x in colData])

    def _str2fix(self, colParams, colData):
        intData = np.array([int(x) for x in colData])
        # verify tuple format
        try:
            signed, intBits, fracBits = colParams[1]
            print("ciao io sono un apix ' ")
        except ValueError:
            print("_ERROR_: current column data isn't of fix type")

        fmt = fu.FixFmt(signed, fracBits, colParams)
        return fi.FixNum(intData*2**(-fracBits), fmt)

    def _str2int(self, colData):
        return np.array([int(x) for x in colData])

    def _str2bool(self, colData):
        return np.array([x != '0' for x in colData])
