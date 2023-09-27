import sys

from musicau import analysis, tools

from musicau.analysis.actions import getFiguredBassAtOffset, getOffsetOfElement

import music21

from datetime import datetime
import os.path
import csv


class FigureCount(analysis.AnalysisMethod):
    """
    Analysis method to perform a count and comparison of the amount of figures within the figured bass on notes near closures vs. other notes.
    """

    def analyze(self, filePath):
        # Retrieve score, measure map, and required parts for the analysis
        score, measureMap = tools.parsing.parsePieceByPath(filePath, True)
        melodyPart = tools.parsing.getPartStreamFromScoreStream(score, 0)
        figuredBassPart = tools.parsing.getPartStreamFromScoreStream(score, 2)

        melodyNotes = melodyPart.recurse().notes

        # Get positions of closures
        bHasFermata = lambda n: \
            True if (hasattr(n, 'expressions') and n.expressions and any(isinstance(e, music21.expressions.Fermata) for e in n.expressions)) else False
        fermataOffsets = list(map(lambda n: getOffsetOfElement(n), melodyNotes.addFilter(bHasFermata)))

        # Figure out which note value (length) is the predominant one
        noteValueMap = {}
        for note in melodyNotes:
            if note.duration.quarterLength not in noteValueMap:
                noteValueMap[note.duration.quarterLength] = 1
            else:
                noteValueMap[note.duration.quarterLength] += 1
        mainNoteValue = max(noteValueMap, key=noteValueMap.get)

        # Filter out any notes that do not align with the predominant note value
        notesToProcess = []
        for note in melodyNotes:
            if not note.offset % mainNoteValue == 0.0:
                continue
            notesToProcess.append(getOffsetOfElement(note))

        # For figured bass marking, find out how many figures are placed in the figured bass beneath it
        fbMarkingToOffsetMap = {}
        for marking in figuredBassPart.recurse().notes:
            offset = getOffsetOfElement(marking)
            fig = getFiguredBassAtOffset(offset, figuredBassPart)
            if fig != '':
                fbMarkingToOffsetMap[offset] = len(fig.split(","))
            else:
                fbMarkingToOffsetMap[offset] = 0

        # Process results depending on whether a signature is close to a fermata or not
        resultsFermata = []
        resultsOther = []
        for i in range(len(notesToProcess) - 2):
            # Sum up all signatures within the span between the first and last note in the given group of three
            specificResult = 0
            fbOffset = notesToProcess[i]
            while fbOffset <= notesToProcess[i + 2]:
                if fbOffset in fbMarkingToOffsetMap:
                    specificResult += fbMarkingToOffsetMap[fbOffset]
                else:
                    print("WARNING: offset", fbOffset, "not in marking map!")
                fbOffset += 0.25

            # Only if there is a fermata on the last note of a group do we attribute the result to the fermata result list
            if notesToProcess[i + 2] in fermataOffsets:
                resultsFermata.append(specificResult)
            else:
                resultsOther.append(specificResult)

        # Calculate average amount of figures
        averageFermata = sum(resultsFermata) / len(resultsFermata) if len(resultsFermata) > 0 else 0
        averageOther = sum(resultsOther) / len(resultsOther) if len(resultsOther) > 0 else 0
        outResult = [len(resultsFermata), len(resultsOther), averageFermata, averageOther]
        return outResult

    def getOutputHeader(self):
        return ["Total on Fermata",
                "Total on Non-Fermata",
                "Average on Fermata",
                "Average on Non-Fermata"]

    def createOutputEntry(self, resultData):
        return [resultData[0], resultData[1], resultData[2], resultData[3]]


if __name__ == '__main__':
    corpusName = sys.argv[1] if len(sys.argv) > 1 else ""

    outputName = "FigureCount"
    params = analysis.procedures.AnalysisProcedureParams(cataloguesToIgnore=["AP1832"])
    catalogues, results = analysis.procedures.analyseCatalogueCorpus(corpusName, FigureCount(), True, outputName, params)

    # Here we demonstrate how the results can be processed further by calculating values across the entire catalogues
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    fileName = os.path.splitext(outputName)[0] + "_" + timestamp + "_AllCatalogues.csv"
    file = open(fileName, 'w')
    csvWriter = csv.writer(file)

    header = ["Catalogue"] + FigureCount().getOutputHeader()
    csvWriter.writerow(header)

    for catalogue in catalogues.keys():
        totalCountFermata = 0
        totalCountOther = 0
        totalAverageFermata = 0
        totalAverageOther = 0
        for pieceId in results[catalogue].keys():
            totalCountFermata += results[catalogue][pieceId].resultData[0]
            totalCountOther += results[catalogue][pieceId].resultData[1]
            totalAverageFermata += results[catalogue][pieceId].resultData[2]
            totalAverageOther += results[catalogue][pieceId].resultData[3]

        totalAverageFermata = totalAverageFermata / len(results[catalogue].keys())
        totalAverageOther = totalAverageOther / len(results[catalogue].keys())

        line = [catalogue, totalCountFermata, totalCountOther, totalAverageFermata, totalAverageOther]
        csvWriter.writerow(line)

    file.close()
