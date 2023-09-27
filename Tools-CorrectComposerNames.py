import sys

import musicau.tools.corpusManagement
import musicau.tools.parsing

from music21 import converter
from music21.corpus.corpora import LocalCorpus


def checkComposerNames(corpusName: str, bShouldCorrect: bool = True):
    """
    Tool function to check for mismatches in composer name between the catalogue metadata and the individual piece metadata.
    @param corpusName: Name of the music21 LocalCorpus to perform this operation on.
    @param bShouldCorrect: Whether this function should also automatically correct any mismatches (default: True).
    """

    # Check if given corpus name is valid
    if corpusName is None or corpusName == "":
        print("WARNING: Using default corpus...")
        corpusName = musicau.DEFAULT_CORPUS_NAME
    corpus = LocalCorpus(corpusName)
    if not corpus.existsInSettings:
        raise Exception("The given corpus does not exist.")

    # Reparse corpus to generate required temporary files
    musicau.tools.corpusManagement.refreshCorpus(corpusName, bVerbose=True)

    # Check for "META" files to identify catalogues in the corpus
    # This is where we store what the intended name of the composer is supposed to be for each catalogue
    catalogues: dict[str, str] = {}
    metadataFiles = corpus.search('_META', 'sourcePath')
    if len(metadataFiles) == 0:
        raise Exception("The given corpus contains no catalogues.")
    else:
        for metaFile in metadataFiles:
            composerName = metaFile.metadata.composer
            catalogueId = musicau.tools.parsing.getCatalogueId(musicau.tools.parsing.getFileNameFromMetadata(metaFile))
            catalogues[catalogueId] = composerName
            print("Found catalogue: " + catalogues[catalogueId])

    # Iterate through catalogues and their pieces to check for mismatches
    for catalogue in list(catalogues):
        currentCatalogue = corpus.search(catalogue, 'sourcePath')
        for piece in currentCatalogue:
            # Don't parse META pieces or .expanded. pieces
            if "_META" in str(piece.sourcePath) or ".expanded." in str(piece.sourcePath):
                continue

            # Check if composer in piece metadata matches composer in catalogue metadata
            if piece.metadata.composer != catalogues[catalogue]:
                pieceNumber = musicau.tools.parsing.getPieceNumber(musicau.tools.parsing.getFileNameFromMetadata(piece))
                print(catalogues[catalogue] + ", No.", pieceNumber, "doesn't match intended composer name. Name is:", str(piece.metadata.composer))

                # If we should correct, overwrite the XML with the corrected version
                if bShouldCorrect:
                    outStream = converter.parse(piece.sourcePath, format="xml")
                    outStream.metadata.composer = catalogues[catalogue]
                    outStream.write('musicxml', fp=piece.sourcePath)


if __name__ == '__main__':
    corpusName = sys.argv[1] if len(sys.argv) > 1 else ""
    checkComposerNames(corpusName)
