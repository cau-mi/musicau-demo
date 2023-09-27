from music21 import corpus, environment


def refreshCorpora(bVerbose: bool = False):
    """
    Refreshes all music21 local corpora.
    @param bVerbose: Whether to print verbose debug information.
    """
    localCorpora = list(environment.UserSettings()["localCorporaSettings"].keys())
    for localCorpus in localCorpora:
        if bVerbose:
            print("Refreshing metadata for " + localCorpus + "...")
        corpus.corpora.LocalCorpus(localCorpus).cacheMetadata(useMultiprocessing=False, verbose=bVerbose)
        corpus.corpora.LocalCorpus(localCorpus).save()


def refreshCorpus(corpusName: str, bVerbose: bool = False) -> bool:
    """
    Refreshes a music21 LocalCorpus of the given name, if it exists.
    @param corpusName: Name of the corpus.
    @param bVerbose: Whether to print verbose debug information.
    @return: True if refreshed, False if corpus was not found.
    """
    if corpusName not in list(environment.UserSettings()["localCorporaSettings"].keys()):
        return False
    if bVerbose:
        print("Refreshing metadata for " + corpusName + "...")
    corpus.corpora.LocalCorpus(corpusName).cacheMetadata(useMultiprocessing=False, verbose=bVerbose)
    corpus.corpora.LocalCorpus(corpusName).save()
    return True
