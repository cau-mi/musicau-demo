import musicau

from musicau.analysis import AnalysisResult, AnalysisMethod
from musicau.tools import parsing

import music21

from datetime import datetime
import os.path
import csv


class AnalysisProcedureParams:
    """
    Class to hold additional parameters for the analysis procedure.
    """
    def __init__(self, bOutputFileSpecifiers: bool = True, cataloguesToIgnore: list[str] = []):
        """
        @param bOutputFileSpecifiers: Whether to output a column containing the file specifiers in the CSV output.
        @param cataloguesToIgnore: List of catalogues to ignore by string name
        """
        self.bOutputFileSpecifiers: bool = bOutputFileSpecifiers
        self.cataloguesToIgnore: list[str] = cataloguesToIgnore


def analyseCatalogueCorpus(corpusName: str,
                           analysisMethod: AnalysisMethod,
                           bShouldDoOutput: bool = False,
                           outputFileName: str = "",
                           params: AnalysisProcedureParams = AnalysisProcedureParams()) \
        -> tuple[dict[str, str], dict[str, dict[str, AnalysisResult]]]:
    """
    Performs an analysis on a given music21 LocalCorpus using a given AnalysisMethod object.
    @param corpusName: Name of the LocalCorpus to analyse. If blank, the default corpus name will be used.
    @param analysisMethod: The AnalysisMethod object to be used for performing analysis on the pieces.
    @param bShouldDoOutput: Whether to output the results to a CSV file.
    @param outputFileName: The base name for the CSV file output.
    @param params: Additional procedure parameters as an AnalysisProcedureParams object.
    @return: A tuple containing a map matching catalogue IDs to composer names, and a map matching catalogue IDs to a map of piece numbers to
    AnalysisResults.
    """
    if not isinstance(analysisMethod, AnalysisMethod) or analysisMethod.__class__ == AnalysisMethod:
        raise Exception("The given analysis method argument is not a subclass of AnalysisMethod.")

    if corpusName == "":
        print("WARNING: Using default corpus...")
        corpusName = musicau.DEFAULT_CORPUS_NAME
    corpus = music21.corpus.corpora.LocalCorpus(corpusName)
    if not corpus.existsInSettings:
        raise Exception("The given corpus does not exist: " + corpusName)

    musicau.tools.corpusManagement.refreshCorpus(corpusName, bVerbose=True)

    outCatalogues: dict[str, str] = {}
    metadataFiles = corpus.search('_META', 'sourcePath')
    if len(metadataFiles) == 0:
        raise Exception("The given corpus contains no catalogues.")
    else:
        for metaFile in metadataFiles:
            composerName = metaFile.metadata.composer
            catalogueId = parsing.getCatalogueId(parsing.getFileNameFromMetadata(metaFile))

            if catalogueId in params.cataloguesToIgnore:
                continue

            outCatalogues[catalogueId] = composerName
            print("Found catalogue: " + composerName + " (" + catalogueId + ")")

    outResults: dict[str, dict] = {}
    for catalogue in list(outCatalogues):
        outResults[catalogue]: dict[str, AnalysisResult] = {}

        currentCatalogue = corpus.search(catalogue, 'sourcePath')
        for piece in currentCatalogue:
            if "_META" in str(piece.sourcePath) or ".expanded." in str(piece.sourcePath):
                continue
            analysisResult = analysisMethod.analyze(piece.sourcePath)
            pieceNumber = parsing.getPieceNumber(parsing.getFileNameFromMetadata(piece))
            fileSpecifiers = parsing.getSpecifiers(parsing.getFileNameFromMetadata(piece))
            outResults[catalogue][pieceNumber] = AnalysisResult(piece.sourcePath, catalogue, pieceNumber, fileSpecifiers, analysisResult)
            print(outCatalogues[catalogue] + " (" + catalogue + ")" + ", No. " + pieceNumber + " (" + fileSpecifiers + "): " + str(analysisResult))

    if not bShouldDoOutput:
        return outCatalogues, outResults

    print("Analysis complete - exporting to file.")

    if outputFileName == "":
        print("WARNING: The given output file name is empty, using generic name instead.")
        outputFileName = "generic_" + analysisMethod.__class__.__name__

    outputTimestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    for catalogue in list(outCatalogues):
        try:
            fileName = os.path.splitext(outputFileName)[0] + "_" + outputTimestamp + "_" + catalogue + ".csv"
            file = open(fileName, 'w')
        except OSError:
            print("WARNING: Unable to create CSV file with specified name, returning results in code instead.")
            return outCatalogues, outResults

        csvWriter = csv.writer(file)

        csvWriter.writerow((["ID", "Specifiers"] if params.bOutputFileSpecifiers else ["ID"]) + analysisMethod.getOutputHeader())

        for pieceNumber in list(outResults[catalogue]):
            result = outResults[catalogue][pieceNumber]
            line = ([pieceNumber, result.fileSpecifiers] if params.bOutputFileSpecifiers else [pieceNumber]) + analysisMethod.createOutputEntry(
                result.resultData)
            csvWriter.writerow(line)

        file.close()

    print("Export complete.")
    return outCatalogues, outResults
