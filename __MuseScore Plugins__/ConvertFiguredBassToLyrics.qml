import QtQuick 2.0
import MuseScore 3.0

MuseScore {
      menuPath: "Plugins.Convert Figured Bass to Lyrics"
      description: "Adds a third staff with 16th notes to add lyrics to for figured bass."
      version: "1.0"
      onRun: {
            var cursor = curScore.newCursor();            
            cursor.rewind(Cursor.SCORE_START);
            if (cursor.score.nstaves < 3) {
                  cursor.score.appendPart(0);
            }
            cursor.staffIdx = 2;
            cursor.setDuration(1, 16);
            var canMove = true;
            var ticks = 0;
            while (canMove) {
                  cursor.rewindToTick(ticks);
                  cursor.addNote(64);
                  ticks = ticks + division / 4;
                  canMove = ticks < curScore.lastSegment.tick;
            }
            
            cursor.rewind(Cursor.SCORE_START);
            cursor.staffIdx = 2;
            canMove = true;
            var lyr = undefined;
            while (canMove) {
                  if (cursor.element.type == Element.CHORD) {                        
                        for (var j = 0; j < cursor.segment.annotations.length; j++) {
                              lyr = newElement(Element.LYRICS);
                              if (cursor.segment.annotations[j].type == Element.FIGURED_BASS && cursor.segment.annotations[j].visible == true) {
                                    lyr.text = cursor.segment.annotations[j].text.replace('\n', ',');
                                    lyr.text = lyr.text.replace('\n', ',');
                                    lyr.text = lyr.text.replace('\n', ',');
                                    cursor.add(lyr);
                                    cursor.segment.annotations[j].visible = false;
                              }
                        }
                  }
                  canMove = cursor.next();
            }
            Qt.quit();
            }
      }

