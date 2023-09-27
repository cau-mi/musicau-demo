import sys

from musicau import analysis, tools

from musicau.analysis.actions import getFiguredBassAtOffset, getOffsetOfElement

import music21


class FiguredBass798(analysis.AnalysisMethod):
    """
    Analysis method to find sequences of 7 - 9 - 8 in figured bass markings.
    The results will contain any result in which a 7 is found, meaning the filtering for 9 and 8 is done manually.
    """

    def analyze(self, filePath):
        # Retrieve score, measure map, and required parts for the analysis
        score, measureMap = tools.parsing.parsePieceByPath(filePath, True)
        melodyPart = tools.parsing.getPartStreamFromScoreStream(score, 0)
        bassPart = tools.parsing.getPartStreamFromScoreStream(score, 1)
        figuredBassPart = tools.parsing.getPartStreamFromScoreStream(score, 2)

        # Get positions of closures
        bHasFermata = lambda n: \
            True if (hasattr(n, 'expressions') and n.expressions and any(isinstance(e, music21.expressions.Fermata) for e in n.expressions)) else False
        melodyFermatas = melodyPart.recurse().notes.addFilter(bHasFermata)
        fermataPositions = list(map(lambda n: getOffsetOfElement(n), melodyFermatas))

        # Iterate over the bass part to check for specific pitch and figure sequences
        bassIterator = bassPart.flatten().notes
        figuredBassIterator = figuredBassPart.flatten().notes
        outResult = []
        for note in bassIterator:
            previousNote = note.previous('Note')
            if previousNote is None or music21.interval.Interval(previousNote, note).semitones != 1:
                continue

            previousFigure = getFiguredBassAtOffset(previousNote.offset, figuredBassPart)
            if "7" not in previousFigure:
                continue

            if note.next('Note') is not None and note.next('Note').offset in fermataPositions:
                locationOfFermata = "3"
            else:
                locationOfFermata = "2" if note.offset in fermataPositions else "N/A"

            nextFigure = "N/A"
            for figure in figuredBassIterator:
                if figure.offset > note.offset and hasattr(figure, 'lyric') and figure.lyric is not None:
                    nextFigure = figure.lyric
                    break

            currentFigure = getFiguredBassAtOffset(note.offset, figuredBassPart)

            measure = analysis.actions.makeMeasureAndBeatStringByMeasureMap(note, measureMap)
            outResult.append((measure, previousFigure, currentFigure, nextFigure, locationOfFermata))

        return outResult

    def getOutputHeader(self):
        return ["(Position, Marking 1, Marking 2, Marking 3, Fermata on 2 / 3?) 1", "... 2", "... 3", "... 4", "... 5", "... 6"]


if __name__ == '__main__':
    corpusName = sys.argv[1] if len(sys.argv) > 1 else ""

    params = analysis.procedures.AnalysisProcedureParams(cataloguesToIgnore=["AP1832"])
    analysis.procedures.analyseCatalogueCorpus(corpusName, FiguredBass798(), True, "798Search", params)
