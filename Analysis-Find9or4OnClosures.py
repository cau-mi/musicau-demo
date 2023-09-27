import sys

from musicau import analysis, tools

from musicau.analysis.actions import makeMeasureAndBeatStringByMeasureMap, getFiguredBassAtOffset

import music21


class Find9or4(analysis.AnalysisMethod):
    """
    Analysis method to find figures of 9 or 4 on closures or on the note before a closure.
    """

    def analyze(self, filePath):
        # Retrieve score, measure map, and required parts for the analysis
        score, measureMap = tools.parsing.parsePieceByPath(filePath, True)
        melodyPart = tools.parsing.getPartStreamFromScoreStream(score, 0)
        figuredBassPart = tools.parsing.getPartStreamFromScoreStream(score, 2)

        # Get notes with fermatas
        bHasFermata = lambda n: \
            True if (hasattr(n, 'expressions') and n.expressions and any(isinstance(e, music21.expressions.Fermata) for e in n.expressions)) else False
        notesWithFermata = melodyPart.recurse().addFilter(bHasFermata)

        # Iterate over the notes with fermatas and determine the figured bass underneath them (including on previous notes in certain cases)
        outResult = []
        for note in notesWithFermata:
            figure = getFiguredBassAtOffset(notesWithFermata.currentHierarchyOffset(), figuredBassPart)
            if "9" in figure or "4" in figure:
                outResult.append((makeMeasureAndBeatStringByMeasureMap(note, measureMap), figure, False))
            elif note.previous('Note').pitch == note.pitch:
                figure = getFiguredBassAtOffset(note.previous('Note').activeSite.offset + note.previous('Note').offset, figuredBassPart)
                if "9" in figure or "4" in figure:
                    outResult.append((makeMeasureAndBeatStringByMeasureMap(note, measureMap), figure, True))

        return outResult

    def getOutputHeader(self):
        return ["Position, Marking, Detected with preceding melody note?"]


if __name__ == '__main__':
    corpusName = sys.argv[1] if len(sys.argv) > 1 else ""

    params = analysis.procedures.AnalysisProcedureParams(cataloguesToIgnore=["AP1832"])
    analysis.procedures.analyseCatalogueCorpus(corpusName, Find9or4(), True, "9or4OnClosure", params)
