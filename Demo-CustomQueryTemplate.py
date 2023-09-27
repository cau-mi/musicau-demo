import sys

from musicau import analysis, tools


class CustomQuery(analysis.AnalysisMethod):
    """
    Template for a custom analysis query.
    """

    def analyze(self, filePath):
        # Retrieve score, measure map, and required parts for the analysis
        # Comment out any parts you do not need
        score, measureMap = tools.parsing.parsePieceByPath(filePath, True)
        melodyPart = tools.parsing.getPartStreamFromScoreStream(score, 0)
        bassPart = tools.parsing.getPartStreamFromScoreStream(score, 1)
        figuredBassPart = tools.parsing.getPartStreamFromScoreStream(score, 2)

        # Initialize the result output
        outResult = []

        ########################################################################
        # Do your analysis here with our available features as well as music21 #
        ########################################################################

        return outResult

    def getOutputHeader(self):
        # Remove or add any columns you may need
        return ["Column 1", "Column 2", "Column 3"]

    def createOutputEntry(self, resultData):
        # Remove or add any columns you may need
        return [resultData[0], resultData[1], resultData[2]]


if __name__ == '__main__':
    corpusName = sys.argv[1] if len(sys.argv) > 1 else ""

    params = analysis.procedures.AnalysisProcedureParams(cataloguesToIgnore=[""]) # Add ignored catalogues here
    analysis.procedures.analyseCatalogueCorpus(corpusName, CustomQuery(), True, "CustomQuery", params)
