import music21

from typing import Callable


def testConditionAtOffset(offset: float,
                          partStream: music21.stream.Part,
                          condition: Callable[[music21.note.Note], bool]) -> bool:
    """
    Tests a condition at a given offset.
    @param offset: The offset at which to test the condition.
    @param partStream: The music21 Part stream to test against.
    @param condition: The condition to test for as a Callable (pass in a function or lambda):
    @return: The result of the evaluation.
    """
    streamIterator = partStream.recurse().notes
    for note in streamIterator:
        if streamIterator.currentHierarchyOffset() == offset and condition(note):
            return True
    return False


def runFunctionAtOffset(offset: float,
                        partStream: music21.stream.Part,
                        condition: Callable[[music21.note.Note], bool],
                        function: Callable[[music21.note.Note], any]) -> any:
    """
    Runs a function at a given offset if the condition evaluates as True.
    @param offset: The offset at which to test the condition.
    @param partStream: The music21 Part stream to test against.
    @param condition: The condition to test for as a Callable (pass in a function or lambda):
    @param function:  The function to run as a Callable (pass in a function or lambda):
    @return: The result of the evaluation, or None if the condition was never met.
    """
    streamIterator = partStream.recurse().notes
    for note in streamIterator:
        if streamIterator.currentHierarchyOffset() == offset and condition(note):
            return function(note)
    return None


def getFiguredBassAtOffset(offset: float, figuredBassPart: music21.stream.Part) -> str:
    """
    Retrieves the figure in the figured bass at a given offset.
    @param offset: The offset at which to retrieve the figure from the figured bass part.
    @param figuredBassPart: The music21 Part stream containing the figured bass information as lyrics.
    @return: The figure at the offset.
    """
    figure = runFunctionAtOffset(offset, figuredBassPart, lambda x: hasattr(x, 'lyric') and x.lyric is not None, lambda x: x.lyric)
    return '' if figure is None else figure.replace("h", "n")


def getFiguredBassFromNote(note: music21.note.Note) -> str:
    """
    Retrieves the figure from the figured bass on the given note. The note must be part of the figured bass part to retrieve the figure.
    @param note: The note from which to retrieve the figure.
    @return: The figure at the note.
    """
    return note.lyric.replace("h", "n") if hasattr(note, 'lyric') and note.lyric is not None else ''


def getOffsetOfElement(element: music21.base.Music21Object) -> float:
    """
    Retrieves the offset of an element in the stream from the beginning of the stream.
    @param element: The element of which to get the offset.
    @return: The offset.
    """
    return element.getContextByClass('Measure').offset + element.offset


def makeMeasureAndBeatStringByMeasureMap(note: music21.note.Note, measureMap: dict[float, str]) -> str:
    """
    Makes a string containing the measure and beat of a note based on the given measure map.
    @param note: The music21 Note to generate this string for.
    @param measureMap: The measure map to use.
    @return: String in the format '[measure], [beat]'
    """
    return str(measureMap[note.getContextByClass('Measure').offset]) + ", " + str(note.beat)
