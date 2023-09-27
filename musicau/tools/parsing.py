import music21

from music21 import converter
from music21.metadata.bundles import MetadataEntry
from music21.repeat import ExpanderException

import glob
import hashlib
import os.path


def parsePieceByPath(sourcePath: os.path, bShouldExpandRepeats: bool) -> tuple[music21.stream.Score, dict[float, str]]:
    """
    Parses a piece into a usable music21 Score stream and a corresponding measure map.
    @param sourcePath: Path to the MusicXML file to parse.
    @param bShouldExpandRepeats: Whether repeats in the piece should be rolled out. The parser will store pre-expanded files after expanding repeats or
    if the source file has changed to optimize future processing times.
    @return: Tuple containing the music21 Score stream and a measure map if parsed correctly, otherwise both will be None.
    """
    if not os.path.isfile(sourcePath):
        return None, None

    if bShouldExpandRepeats:
        with open(sourcePath, "r") as f:
            sourceFileChecksum = hashlib.md5(f.read().encode()).hexdigest()[:12]

        pathToPreExpandedScore = os.path.split(sourcePath)[0] + "\\" + getFileNameFromPath(sourcePath) + ".expanded." + sourceFileChecksum + ".cmxl"
        if os.path.isfile(pathToPreExpandedScore):
            outStream = converter.parse(pathToPreExpandedScore, format="xml")
        else:
            try:
                for outdatedExpandedScore in glob.glob(os.path.split(sourcePath)[0] + "\\" + getFileNameFromPath(sourcePath) + ".expanded.*"):
                    os.remove(outdatedExpandedScore)

                outStream = converter.parse(sourcePath).expandRepeats()
                outStream.write('musicxml', fp=pathToPreExpandedScore)
            except ExpanderException:
                print("WARNING: Score part contains repeat that cannot be expanded - check file. " + str(sourcePath))
                outStream = converter.parse(sourcePath)
    else:
        outStream = converter.parse(sourcePath)
    outMeasureMap = makeMeasureMapFromStream(outStream.parts[0])
    return outStream, outMeasureMap


def getPartStreamFromScoreStream(scoreStream: music21.stream.Score, partIndex: int) -> music21.stream.Part:
    """
    Retrieves a part stream from a score stream.
    @param scoreStream: The source score stream.
    @param partIndex: Index of the path to retrieve.
    @return: The music21 Part stream.
    @raise: IndexError if index out of range
    """
    if len(scoreStream.parts) < partIndex:
        raise IndexError
    outPart = scoreStream.parts[partIndex]
    return outPart


def makeMeasureMapFromStream(stream: music21.stream.Stream) -> dict[float, str]:
    """
    Generates a measure map from a given stream.
    @param stream: The source stream.
    @return: The generated measure map.
    """
    outMeasureMap = {}
    usedMeasureNames = {}
    for i, measure in enumerate(stream.getElementsByClass('Measure')):
        targetMeasureName = measure.measureNumberWithSuffix()
        if targetMeasureName not in list(usedMeasureNames):
            outMeasureMap[measure.offset] = targetMeasureName
            usedMeasureNames[targetMeasureName] = 1
        else:
            outMeasureMap[measure.offset] = targetMeasureName + " (" + str(usedMeasureNames[targetMeasureName]) + ")"
            usedMeasureNames[targetMeasureName] = usedMeasureNames[targetMeasureName] + 1
    return outMeasureMap


def getFileNameFromMetadata(metadataEntry: MetadataEntry) -> str:
    """
    Retrieves the file name from a music21 MetadataEntry.
    @param metadataEntry: The music21 MetadataEntry.
    @return: The file name.
    """
    return str.split(os.path.splitext(os.path.basename(metadataEntry.metadata.sourcePath))[0], ".")[0]


def getFileNameFromPath(filePath: os.path) -> str:
    """
    Retrieves the file name from a file path.
    @param filePath: The file path.
    @return: The file name.
    """
    return os.path.splitext(os.path.basename(filePath))[0]


def getCatalogueId(fileName: str) -> str:
    """
    Extracts the catalogue ID from the file name.
    @param fileName: The file name.
    @return: The catalogue ID.
    """
    return str.split(str.split(fileName, "_")[0], "-")[0]


def getPieceNumber(fileName: str) -> str:
    """
    Extracts the piece number from the file name.
    @param fileName: The file name.
    @return: The piece number.
    """
    return str.split(str.split(fileName, "_")[0], "-")[1]


def getSpecifiers(fileName: str) -> str:
    """
    Extracts the additional specifiers from the file name.
    @param fileName: The file name.
    @return: The specifiers.
    """
    return str.split(fileName, "_")[1] if len(str.split(fileName, "_")) > 1 else ""
