import csv
import sys
from datetime import datetime

from musicau import analysis, tools

from musicau.analysis.actions import makeMeasureAndBeatStringByMeasureMap

import music21

import numpy
import cv2

import os.path


class IntegerPitchEncoding40:
    """
    Utility class for representation of musical pitches as an integer between 0 and 40. Useful for quick, mathematical transposition.
    """
    baseValue = 40
    noteToBaseValueMap = {"C": 2, "D": 8, "E": 14, "F": 19, "G": 25, "A": 31, "B": 37}
    baseValueToNoteMap = {
        0: "C--",
        1: "C-",
        2: "C",
        3: "C#",
        4: "C##",
        5: "INVALID5",
        6: "D--",
        7: "D-",
        8: "D",
        9: "D#",
        10: "D##",
        11: "INVALID11",
        12: "E--",
        13: "E-",
        14: "E",
        15: "E#",
        16: "E##",
        17: "F--",
        18: "F-",
        19: "F",
        20: "F#",
        21: "F##",
        22: "INVALID22",
        23: "G--",
        24: "G-",
        25: "G",
        26: "G#",
        27: "G##",
        28: "INVALID28",
        29: "A--",
        30: "A-",
        31: "A",
        32: "A#",
        33: "A##",
        34: "INVALID34",
        35: "B--",
        36: "B-",
        37: "B",
        38: "B#",
        39: "B##",
    }

    @staticmethod
    def encodeMusic21Pitch(pitch: music21.pitch.Pitch) -> int:
        """
        Encodes a given music21 Pitch to an integer according to the underlying encoding.
        @param pitch: The music21 Pitch to encode to an integer.
        @return: The value of the pitch in the integer encoding.
        """
        # return IntegerPitchEncoding40.noteToBaseValueMap[pitch.name[:1]] + int(pitch.alter) + pitch.octave * IntegerPitchEncoding40.baseValue
        return IntegerPitchEncoding40.noteToBaseValueMap[pitch.name[:1]] + int(pitch.alter) + 4 * IntegerPitchEncoding40.baseValue

    @staticmethod
    def decodeToMusic21Pitch(pitchValue: int) -> music21.pitch.Pitch:
        """
        Decodes a given integer to a music21 Pitch.
        @param pitchValue: The integer to decode.
        @return: The value as a music21 Pitch.
        """
        v = IntegerPitchEncoding40.baseValueToNoteMap[pitchValue % IntegerPitchEncoding40.baseValue] + str(pitchValue // IntegerPitchEncoding40.baseValue)
        return music21.pitch.Pitch(v)


def transposeIntPitchToNoAlterations(note: int, sourceKey: music21.key.Key) -> int:
    """
    Utility function to transpose a note in integer encoding around the circle of fifths to no sharps or flats.
    @param note: The pitch in integer encoding.
    @param sourceKey: The key signature the pitch is set in.
    @return: The pitch in integer encoding transposed to no alterations.
    """
    return note + 23 * -sourceKey.sharps + 40 * (sourceKey.sharps // 2)


def npHistogramToCV(npHistogram):
    """
    Utility function to convert a numpy histogram to a cv2 compatible histogram.
    @param npHistogram: The numpy histogram.
    @return: The numpy histogram for cv2.
    """
    counts, bin_edges = npHistogram
    return counts.ravel().astype('float32')


class PhraseDetector(analysis.AnalysisMethod):
    """
    Analysis method used as a tool to locate a particular phrase inside the contents of a corpus.
    """

    def __init__(self,
                 pathToSourcePhrase: os.path,
                 countDiffThreshold: float,
                 histogramThreshold: float,
                 sequenceThreshold: float):
        """
        This class has a few custom parameters to demonstrate how we can tweak the way an analysis is performed.
        @param pathToSourcePhrase: Path to the file containing the source phrase.
        @param countDiffThreshold: Threshold for the counting difference evaluation.
        @param histogramThreshold: Threshold for the pitch histogram evaluation.
        @param sequenceThreshold: Threshold for the sequence equality evaluation.
        """
        super().__init__()
        self.sourceFilePath: os.path = pathToSourcePhrase
        self.__sourcePhrase = self.__retrieveAndTransposePhrases(pathToSourcePhrase, 1)["1, 1.0"]  # Pre-process the source phrase into source pitches once
        self.countDiffThreshold: float = countDiffThreshold
        self.histogramThreshold: float = histogramThreshold
        self.sequenceThreshold: float = sequenceThreshold

    @staticmethod
    def __retrieveAndTransposePhrases(filePath: os.path, maxSearch: int = 0):
        """
        Utility to retrieve and transpose all phrases from a given file path.
        @param filePath: Path to the file to retrieve the phrases from.
        @param maxSearch: The maximum amount of phrases to retrieve.
        @return: A dictionary of phrases as transposed music21 pitches with measure-beat strings as keys.
        """
        score, measureMap = tools.parsing.parsePieceByPath(filePath, False)
        melodyPart = tools.parsing.getPartStreamFromScoreStream(score, 0)

        bHasFermata = lambda n: \
            True if (hasattr(n, 'expressions') and n.expressions and any(isinstance(e, music21.expressions.Fermata) for e in n.expressions)) else False
        melodyFermatas = melodyPart.recurse().notes

        notePhraseMap = {}
        noteValueMap = {}
        phraseNumber = "1, 1.0"
        keySignature = None
        for note in melodyFermatas:
            if keySignature is None:
                keySignature = note.getContextByClass('KeySignature').asKey()
            if note.duration.quarterLength not in noteValueMap:
                noteValueMap[note.duration.quarterLength] = 0

            noteValueMap[note.duration.quarterLength] += 1

            if phraseNumber not in notePhraseMap:
                notePhraseMap[phraseNumber] = []

            if maxSearch == 0 or len(notePhraseMap.keys()) <= maxSearch:
                notePhraseMap[phraseNumber].append(note)

            if bHasFermata(note):
                phraseNumber = makeMeasureAndBeatStringByMeasureMap(note.next('Note') if note.next('Note') is not None else note, measureMap)

        mainNoteValue = max(noteValueMap, key=noteValueMap.get)

        transposedPhrases = {}
        for phrase in notePhraseMap:
            for note in notePhraseMap[phrase]:
                if not note.offset % mainNoteValue == 0.0:
                    continue

                encodedNote = IntegerPitchEncoding40.encodeMusic21Pitch(note.pitch)

                if phrase not in transposedPhrases:
                    transposedPhrases[phrase] = []

                transposedPhrases[phrase].append(IntegerPitchEncoding40.decodeToMusic21Pitch(transposeIntPitchToNoAlterations(encodedNote, keySignature)))

        return transposedPhrases

    def __performDetection(self, targetPhrase: list[music21.pitch.Pitch]):
        # Initialize the results
        detectionResult = {"isMatch": 0, "countDiff": 0, "pitchHistogram": 0, "sequenceEquality": 0}

        # Perform calculation of the count differential
        comp_CountDiff = max(len(self.__sourcePhrase), len(targetPhrase)) / min(len(self.__sourcePhrase), len(targetPhrase)) - 1

        detectionResult["countDiff"] = comp_CountDiff
        if comp_CountDiff > self.countDiffThreshold:
            return detectionResult

        # Perform calculation of the pitch histograms
        encodedSourcePitches = list(map(lambda x: IntegerPitchEncoding40.encodeMusic21Pitch(x), self.__sourcePhrase))
        encodedTargetPitches = list(map(lambda x: IntegerPitchEncoding40.encodeMusic21Pitch(x), targetPhrase))

        shorterPhraseLength = min(len(self.__sourcePhrase), len(targetPhrase))

        sourcePitchHistogram = npHistogramToCV(numpy.histogram(encodedSourcePitches[:shorterPhraseLength], bins=499, range=(0, 499)))
        targetPitchHistogram = npHistogramToCV(numpy.histogram(encodedTargetPitches[:shorterPhraseLength], bins=499, range=(0, 499)))

        detectionResult["pitchHistogram"] = 1 - cv2.compareHist(sourcePitchHistogram, targetPitchHistogram, cv2.HISTCMP_BHATTACHARYYA)

        # Perform calculation of the sequence equality
        sourcePitchNames = list(map(lambda x: x.name, self.__sourcePhrase))
        targetPitchNames = list(map(lambda x: x.name, targetPhrase))

        comp_SeqEqualityCount = 0
        for k in range(shorterPhraseLength):
            if sourcePitchNames[k] == targetPitchNames[k]:
                comp_SeqEqualityCount += 1

        detectionResult["sequenceEquality"] = comp_SeqEqualityCount / shorterPhraseLength

        # Determine whether it is a match based on given thresholds
        bIsMatch = detectionResult["pitchHistogram"] >= self.histogramThreshold and detectionResult["sequenceEquality"] >= self.sequenceThreshold
        detectionResult["isMatch"] = 1 if bIsMatch else 0

        return detectionResult

    def analyze(self, filePath: os.path):
        # Retrieve the transposed phrases for the target
        targetPhrases = self.__retrieveAndTransposePhrases(filePath)

        outMatches = None
        outDetectionResults = {}

        for phrase in targetPhrases:
            outDetectionResults[phrase] = self.__performDetection(targetPhrases[phrase])
            if outDetectionResults[phrase]['isMatch'] == 1:
                outMatches = [phrase] if outMatches is None else outMatches + [phrase]

        return [outMatches, outDetectionResults]

    def getOutputHeader(self):
        return ["Phrase Matches", "Detection Results per Phrase"]


if __name__ == '__main__':
    corpusName = sys.argv[1] if len(sys.argv) > 1 else ""

    # The path to the file containing the phrase we would like to detect
    pathToPhrase = ""
    while not os.path.isfile(pathToPhrase):
        pathToPhrase = input("Path to file containing phrase to detect (or 'q' to exit): ")
        if pathToPhrase == "q":
            exit()

    outputName = "PhraseDetection"
    params = analysis.procedures.AnalysisProcedureParams(cataloguesToIgnore=["AP1832"])
    catalogues, results = analysis.procedures.analyseCatalogueCorpus(corpusName, PhraseDetector(pathToPhrase, 0.25, 0.5, 0.7), True, outputName, params)

    # Here we demonstrate how the results can be processed further by calculating values across the entire catalogues
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    fileName = os.path.splitext(outputName)[0] + "_" + timestamp + "_AllMatches.csv"
    file = open(fileName, 'w')
    csvWriter = csv.writer(file)

    header = ["Catalogue and Piece ID", "Matches", "Detailed Results"]
    csvWriter.writerow(header)

    for catalogue in catalogues.keys():
        for pieceId in results[catalogue].keys():
            if results[catalogue][pieceId].resultData[0] is not None:
                resultData = results[catalogue][pieceId].resultData
                line = [catalogue + ", " + pieceId, resultData[0], resultData[1]]
                csvWriter.writerow(line)

    file.close()
