import sys

from musicau import analysis, tools

from musicau.analysis.actions import getFiguredBassAtOffset, makeMeasureAndBeatStringByMeasureMap

import music21

from music21 import interval
from music21.figuredBass import realizer


class CheckForDiminishedBass(analysis.AnalysisMethod):
    """
    Analysis method used as a tool to check for generation of diminished fifths over figures that are actually supposed to imply perfect fifths.
    """

    def analyze(self, filePath):
        # Retrieve score, measure map, and required parts for the analysis
        score, measureMap = tools.parsing.parsePieceByPath(filePath, True)
        bassPart = tools.parsing.getPartStreamFromScoreStream(score, 1)
        figuredBassPart = tools.parsing.getPartStreamFromScoreStream(score, 2)

        # Iterate over the bass notes to find problematic figures
        outResult = []
        iterBass = bassPart.recurse().notes
        for note in iterBass:
            # The problem is most common over leading tones: ignore any note that is not a leading tone
            if not note.name == note.getContextByClass('KeySignature').asKey().getLeadingTone().name:
                continue

            # Ignore certain figures and combinations of figures
            figure = getFiguredBassAtOffset(iterBass.currentHierarchyOffset(), figuredBassPart)
            if '_' in figure or ('4' in figure or '6' in figure or '2' in figure) and '5' not in figure:
                continue

            # Use music21 to automatically generate a solution to a given bass note with figure
            figuredLine = realizer.FiguredBassLine(note.getContextByClass('KeySignature').asKey(), note.getContextByClass('TimeSignature'))
            figuredLine.addElement(note, figure)
            realization = figuredLine.realize()

            # Check if there are no valid solutions
            # This usually happens with 9 in the figured bass and is considered to be a problem with music21
            if realization.getNumSolutions() == 0:
                print("WARNING: Figure could not be evaluated: '" + figure + "' in " + makeMeasureAndBeatStringByMeasureMap(note, measureMap))
                continue

            # Flatten the solution to a chord and find a diminished fifth within it
            solution = realization.generateRandomRealization().flatten()
            chord = music21.chord.Chord(solution.notes).closedPosition()
            for x in range(len(chord.notes)):
                for y in range(len(chord.notes)):
                    if x != y and interval.Interval(chord.notes[x], chord.notes[y]).simpleName == 'd5':  # Change this for detecting other intervals
                        outResult.append((makeMeasureAndBeatStringByMeasureMap(note, measureMap), figure))

        return outResult

    def getOutputHeader(self):
        return ["Position, Marking"]

    def createOutputEntry(self, resultData):
        return resultData


if __name__ == '__main__':
    corpusName = sys.argv[1] if len(sys.argv) > 1 else ""

    params = analysis.procedures.AnalysisProcedureParams(cataloguesToIgnore=["AP1832"])
    analysis.procedures.analyseCatalogueCorpus(corpusName, CheckForDiminishedBass(), True, "DiminishedFifthOverFiguredBass", params)
