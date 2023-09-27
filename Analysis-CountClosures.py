import sys

from musicau import analysis, tools

import music21


class CountClosures(analysis.AnalysisMethod):
    """
    The simplest of our analysis methods to count the amount of closures in a piece.
    """

    def analyze(self, filePath):
        # Retrieve score, measure map, and required parts for the analysis
        score, measureMap = tools.parsing.parsePieceByPath(filePath, False)
        melodyPart = tools.parsing.getPartStreamFromScoreStream(score, 0)

        # Create a filter that checks if the current element possesses an expression of type Fermata.
        bHasFermata = lambda n: \
            True if (hasattr(n, 'expressions') and n.expressions and any(isinstance(e, music21.expressions.Fermata) for e in n.expressions)) else False

        # Apply filters to the streams to receive just the notes that have fermatas.
        notesWithFermata = melodyPart.recurse().addFilter(bHasFermata)

        # Return the length of the list of notes with a fermata.
        return [len(notesWithFermata)]

    def getOutputHeader(self):
        return ["# of closures"]


if __name__ == '__main__':
    corpusName = sys.argv[1] if len(sys.argv) > 1 else ""

    params = analysis.procedures.AnalysisProcedureParams(cataloguesToIgnore=["AP1832"])
    analysis.procedures.analyseCatalogueCorpus(corpusName, CountClosures(), True, "ClosureCount", params)
