'''
MusiCAU analyis module. Provides the backbone for automated analysis.
'''

import os.path


class AnalysisMethod:
    """
    Abstract class that defines the framework of how analysis methods are to be constructed and interacted with.
    """
    def __init__(self):
        pass

    def analyze(self, filePath: os.path) -> list[any]:
        """
        Method that is called by the analysis procedure to perform the analysis.
        @param filePath: Path to the MusicXML file to analyse.
        @return: List containing the results of the analysis. This list is likely different for every analysis method.
        """
        return []

    def getOutputHeader(self) -> list[str]:
        """
        Method to receive the header for the CSV output.
        @return: List of strings, one entry per column in the header.
        """
        return ["Result Data"]

    def createOutputEntry(self, resultData: list[any]) -> list[any]:
        """
        Method to generate a row for the CSV output based on given results.
        @param resultData: The result data from the AnalysisResult of a given piece.
        @return: List, one entry per column in the row.
        """
        return resultData


class AnalysisResult:
    """
    Contains the results of an analysis as well as additional data for an individual piece.
    """
    def __init__(self,
                 filePath: os.path = None,
                 catalogueID: str = "",
                 pieceNumber: str = "",
                 fileSpecifiers: str = "",
                 resultData: list[any] = None):
        """

        @param filePath: Path to the analysed MusicXML file.
        @param catalogueID: ID of the parent catalogue (i.e. 'KI1803').
        @param pieceNumber: ID of the piece within the catalogue.
        @param fileSpecifiers: Additional specifiers on the  file (such as 'SID082').
        @param resultData: Data from the actual analysis of the piece.
        """
        self.filePath: os.path = filePath
        self.catalogueID: str = catalogueID
        self.pieceNumber: str = pieceNumber
        self.fileSpecifiers: str = fileSpecifiers
        self.resultData: list[any] = resultData


__all__ = [
    'actions',
    'procedures',
]


from musicau.analysis import *
