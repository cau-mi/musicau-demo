import sys

from musicau import analysis, tools

from musicau.analysis.actions import testConditionAtOffset, getOffsetOfElement

import music21

from music21 import interval


class FindPhrygianClosures(analysis.AnalysisMethod):
    """
    Analysis method to find phrygian closures.
    """

    def analyze(self, filePath):
        # Retrieve score, measure map, and required parts for the analysis
        score, measureMap = tools.parsing.parsePieceByPath(filePath, True)
        melodyPart = tools.parsing.getPartStreamFromScoreStream(score, 0)
        bassPart = tools.parsing.getPartStreamFromScoreStream(score, 1)

        # Get positions of closures
        bHasFermata = lambda n: \
            True if (hasattr(n, 'expressions') and n.expressions and any(isinstance(e, music21.expressions.Fermata) for e in n.expressions)) else False
        melodyFermatas = melodyPart.recurse().notes.addFilter(bHasFermata)
        fermataPositions = list(map(lambda n: getOffsetOfElement(n), melodyFermatas))

        bHasHalfStep = lambda n: \
            getOffsetOfElement(n) in fermataPositions and n.previous('Note') is not None and interval.Interval(n.previous('Note'), n).semitones == -1

        bHasCorrespondingWholeStep = lambda offset, part: \
            testConditionAtOffset(offset, part, lambda n: n.previous('Note') is not None and interval.Interval(n.previous('Note'), n).semitones == 2)

        bassHalfSteps = bassPart.recurse().notes.addFilter(bHasHalfStep)

        # Iterate over the notes found to have half step for additional data (like whether there is a corresponding whole step in the melody part)
        outResult = [len(bassHalfSteps),
                     list(map(lambda n:
                              [analysis.actions.makeMeasureAndBeatStringByMeasureMap(n, measureMap),
                               bHasCorrespondingWholeStep(getOffsetOfElement(n), melodyPart)], bassHalfSteps))]
        return outResult

    def getOutputHeader(self):
        return ["# of closures", "List of all closures (Position, Whole Step in Melody?)"]

    def createOutputEntry(self, resultData):
        return [resultData[0], resultData[1]]


if __name__ == '__main__':
    corpusName = sys.argv[1] if len(sys.argv) > 1 else ""

    params = analysis.procedures.AnalysisProcedureParams(cataloguesToIgnore=["AP1832"])
    analysis.procedures.analyseCatalogueCorpus(corpusName, FindPhrygianClosures(), True, "PhrygianClosures", params)
