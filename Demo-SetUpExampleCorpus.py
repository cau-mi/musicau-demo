from music21 import corpus
import os.path


def main():
    newCorpus = corpus.corpora.LocalCorpus("MusiCAU.Demo")

    if newCorpus.existsInSettings:
        for directory in newCorpus.directoryPaths:
            newCorpus.removePath(directory)

    newCorpus.addPath(os.path.dirname(os.path.abspath(__file__)) + "\\__Example Corpus__\\")
    newCorpus.cacheMetadata(useMultiprocessing=False, verbose=True)
    newCorpus.save()


if __name__ == '__main__':
    main()
