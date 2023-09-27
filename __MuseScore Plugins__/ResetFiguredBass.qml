import QtQuick 2.0
import MuseScore 3.0

MuseScore {
      menuPath: "Plugins.Reset Figured Bass"
      description: "Description goes here"
      version: "1.0"
      onRun: {
            var cursor = curScore.newCursor();
            cursor.rewind(Cursor.SCORE_START);
            cursor.staffIdx = 2;
            var canMove = true;
            while (canMove) {
                  if (cursor.element.type == Element.CHORD) {
                        for (var i = 0; i < cursor.element.lyrics.length; i++) {
                              removeElement(cursor.element.lyrics[i]);
                        }
                        for (var j = 0; j < cursor.segment.annotations.length; j++) {
                              if (cursor.segment.annotations[j].type == Element.FIGURED_BASS) {
                                    cursor.segment.annotations[j].visible = true;
                              }
                        }
                  }
                  canMove = cursor.next();
            }
            Qt.quit();
            }
      }
