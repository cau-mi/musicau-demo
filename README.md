# musicau-demo

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

The musicau-demo contains a demonstration of programs and code created for the purposes of allowing flexible and fast automated musical analysis of large sets of MusicXML-encoded music, specifically two-part settings from the mid-19th century, containing melody, bass and figured bass.

The programs and code are written in [Python 3.10](https://www.python.org/) and can be run by anyone with a Python 3.10 installation which also has the neccesary third-party modules installed (more information below). The primary module for performing the musical analysis of an individual piece of music is [music21](https://github.com/cuthbertLab/music21).

The repository contains an example corpus for use with the provided code derived from transcriptions of *Choralbücher*, which are printed music collections for congregational singing in Schleswig-Holstein churches up to the mid-19th century. The original transcriptions can be found in our [transcription repository](https://github.com/cau-mi/musicau-transcriptions). The example corpus has been altered from the original transcriptions to contain an additional, automatically generated stave which holds information for our software to correctly interpret the figured bass embedded in the transcriptions. See "Information regarding additional figured bass stave" or our project documentation below for more information.

This is a demonstration of the code that was created for the project up to this point and serves mainly as an indication of what we eventually want to make possible at a wider scale. For more detailed information on the future goals of this project, as well as its current capabilities, check out our project overview and documentation (link coming soon).

## Features

- Automatic analysis of large corpora of MusicXML-encoded music (524 pieces in example corpus)
- Output of analysis results in CSV format and return in code for further processing
- Prespecified methods and classes to create new queries quickly
- Ability to analyse figured bass elements and sequences
  - MuseScore plugin for automatically generating required figured bass stave
- Automatic generation and caching of files with expanded repeats to increase future query speeds
  - Self-validation and regeneration of cached files when source files change
 
## Requirements / Dependancies

The demo requires [Python 3.10 or higher](https://www.python.org/) to be installed on the user's machine. The code was developed and tested on a Windows 10 system and is predicted to work on other systems, such as Unix-based systems, without compromise, but this has not been thoroughly tested and as such, issues may arise. Please contact us in case this happens so we can address these problems.

The demo also requires the following modules to be installed:

| Module | Purpose |
| --- | --- |
| [music21](https://github.com/cuthbertLab/music21) | Primary module for musical analysis |
| [numpy](https://numpy.org/) | Histogram evaluation (phrase detection tool only)  |
| [opencv-python](https://github.com/opencv/opencv-python) | Histogram evaluation (phrase detection tool only) |

## Using the demonstration

Assuming all above requirements are met, the contents of this repository can be downloaded and (if necessary) extracted into any location on the user's machine. To make use of the example corpus, users must run the `Demo-SetUpExampleCorpus.py` file which will automatically set up the example corpus for use by the provided analysis queries and tools.

The available queries and tools are:

| File | Tool |
| --- | --- |
| `Tools-CheckForDiminishedOverFiguredBass.py` | Check for tritones over certain note-figured bass combinations |
| `Tools-CorrectComposerNames.py` | Correct composer names in piece metadata |
| `Tools-PhraseDetection.py` | Detect a given phrase in other pieces within the corpus |
| `Analysis-CountClosures.py` | Count the number of closures in each piece |

| File | Query |
| --- | --- |
| `Analysis-PhrygianClosures.py` | Find all Phrygian cadences |
| `Analysis-789Search.py` | Find sequences of 7-9-8 in the figured bass |
| `Analysis-FigureCount.py` | Find average amount of figures per figured bass marking on closures vs. otherwise |
| `Analysis-Find9or4OnClosures.py` | Find 9 or 4 in figured bass markings on closures |

The repository also contains `Demo-CustomQueryTemplate.py` as a template to be used by developers to implement their own queries. Please refer to the documentation for more detailed information on terms, creating custom queries or corpora, and more detailed notes for developers (link coming soon).

## Information regarding additional figured bass stave

The analysis of figured bass currently works with a detour, since music21 can only interpret the figured bass if it is encoded as lyrics. The trouble is that some figures in a figured bass may not align to a specific note but rather be located between two notes. Because lyric elements are tied to a note in MusicXML, this means these offset figures cannot be correctly represented as a lyric element and will therefore become lost in translation to music21.

To fix this, MusiCAU contains a plugin for MuseScore that converts the notated figured bass into lyrics and links those to a third stave with continuous sixteenth notes. This plugin is non-destructive. The plugin for MuseScore is currently only compatible with version 3.6.2 of MuseScore while the MuseScore development team works on overhauling the plugin system in version 4. The plugin is also included in this demonstration.

## Context and future development goals

Please refer to the documentation (link coming soon).

## Credits

MusiCAU was developed at the Musicological Institute at Kiel University. For further information on the people involved see CONTRIBUTORS.txt.
The code was developed between October 2021 and September 2023.
