import QtQuick 2.9
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2 // FileDialogs
import QtQuick.Window 2.3
import Qt.labs.folderlistmodel 2.2
import Qt.labs.settings 1.0
import QtQml 2.8
import MuseScore 3.0
import FileIO 3.0

MuseScore {
    version: "1.0"
    requiresScore: false
    description: qsTr("This plugin converts figured bass in multiple files into lyrics on a special staff.")
    pluginType: "dialog"

    MessageDialog {
        id: versionError
        visible: false
        title: qsTr("Unsupported MuseScore Version")
        text: qsTr("This plugin needs MuseScore 3")
        onAccepted: {
            batchConvert.parent.Window.window.close();
            Qt.quit();
        }
    }

    Settings {
        id: mscorePathsSettings
        category: "application/paths"
        property var myScores
    }

    onRun: {
        // check MuseScore version
        if (mscoreMajorVersion < 3) { // we should really never get here, but fail at the imports above already
            batchConvert.visible = false
            versionError.open()
        }
        else
            batchConvert.visible = true // needed for unknown reasons
    }

    //Window {
    id: batchConvert

    // `width` and `height` allegedly are not valid property names, works regardless and seems needed?!
    width: mainRow.childrenRect.width
    height: mainRow.childrenRect.height

    RowLayout {
        id: mainRow
        GroupBox {
            id: inFormats
            title: " " + qsTr("Input Formats") + " "
            Layout.alignment: Qt.AlignTop | Qt.AlignLeft
            //flat: true // no effect?!
            //checkable: true // no effect?!
            property var extensions: new Array
            Column {
                  spacing: 1
                  CheckBox {
                            id: fuck
                            text: "fuuuuck"
                  }
            } // Column
        } // inFormats
        ColumnLayout {
            Layout.alignment: Qt.AlignTop | Qt.AlignRight
            RowLayout {
                Label {
                    text: " ===> "
                    Layout.fillWidth: true // left align (?!)
                }
                GroupBox {
                    id: outFormats
                    title: " " + qsTr("Output Formats") + " "
                    property var extensions: new Array
                    Column {
                        spacing: 1
                        CheckBox {
                            id: fuck2
                            text: "fuuuuck"
                        }
                    } //Column
                } //outFormats
            } // RowLayout
            CheckBox {
                id: traverseSubdirs
                text: qsTr("Process\nSubdirectories")
            } // traverseSubdirs
            CheckBox {
                id: differentExportPath
                // Only allow different export path if not traversing subdirs.
                // Would be better disabled than invisible, but couldn't find the way to change to disabled color,
                // and having the same enabled and disabled is very confusing.
                visible: !traverseSubdirs.checked
                text: qsTr("Different Export\nPath")
            } // differentExportPath
            GroupBox {
                id: cancelOk
                Layout.alignment: Qt.AlignBottom | Qt.AlignRight
                Row {
                    Button {
                        id: ok
                        text: /*qsTr("Ok")*/ qsTranslate("QPlatformTheme", "OK")
                        //isDefault: true // needs more work
                        onClicked: {
                            if (collectInOutFormats())
                                sourceFolderDialog.open()
                        } // onClicked
                    } // ok
                    Button {
                        id: cancel
                        text: /*qsTr("Cancel")*/ qsTranslate("QPlatformTheme", "Cancel")
                        onClicked: {
                            batchConvert.parent.Window.window.close();
                            Qt.quit();
                        }
                    } // Cancel
                } // Row
            } // cancelOk
        } // ColumnLayout
    } // RowLayout
    //} // Window
    // remember settings
    Settings {
        id: settings
        category: "BatchConvertPlugin"
        // other options
        property alias travers: traverseSubdirs.checked
        property alias diffEPath: differentExportPath.checked  // different export path
        property alias iPath: mscorePathsSettings.myScores // import path
        property alias ePath: mscorePathsSettings.myScores // export path
    }

    FileDialog {
        id: sourceFolderDialog
        title: traverseSubdirs.checked ?
                   qsTr("Select Sources Startfolder"):
                   qsTr("Select Sources Folder")
        selectFolder: true
        folder: "file:///" + settings.ipath // transform to URL

        onAccepted: {
            if (differentExportPath.checked && !traverseSubdirs.checked)
                targetFolderDialog.open(); // work we be called from within the target folder dialog
            else
                work()
        }
        onRejected: {
            console.log("No source folder selected")
            batchConvert.parent.Window.window.close();
        }

        Component.onDestruction: {
            settings.ipath = sourceFolderDialog.folder
        }
    } // sourceFolderDialog
    
    FileDialog {
        id: targetFolderDialog
        title: qsTr("Select Target Folder")
        selectFolder: true

        folder: "file:///" + settings.epath // transform to URL

        property string folderPath: ""
        onAccepted: {
            // remove the file:/// at the beginning of the return value of targetFolderDialog.folder
            // However, what needs to be done depends on the platform.
            // See this stackoverflow post for more details:
            // https://stackoverflow.com/questions/24927850/get-the-path-from-a-qml-url
            if (folder.toString().indexOf("file:///") != -1) // startsWith is EcmaScript6, so not for now
                folderPath = folder.toString().substring(folder.toString().charAt(9) === ':' ? 8 : 7)
            else
                folderPath = folder
            work()
        }

        onRejected: {
            console.log("No target folder selected")
            batchConvert.parent.Window.window.close();
        }
        Component.onDestruction: {
            settings.epath = targetFolderDialog.folder
        }
    } // targetFolderDialog

    function collectInOutFormats() {
        return (1)
    } // collectInOutFormats

    // flag for abort request
    property bool abortRequested: false

    // dialog to show progress
    Dialog {
        id: workDialog
        modality: Qt.ApplicationModal
        visible: false
        width: 720
        standardButtons: StandardButton.Abort

        Label {
            id: currentStatus
            width: 600
            text: qsTr("Running...")
        }

        TextArea {
            id: resultText
            width: 700
            height: 250
            anchors {
                top: currentStatus.bottom
                topMargin: 5
            }
        }

        onAccepted: {
            Qt.quit()
        }

        onRejected: {
            abortRequested = true
            batchConvert.parent.Window.window.close();
        }
    }
    
    // createDefaultFileName
    // remove some special characters in a score title
    // when creating a file name
    function createDefaultFileName(fn) {
        fn = fn.trim()
        fn = fn.replace(/ /g,"_")
        fn = fn.replace(/\n/g,"_")
        fn = fn.replace(/[\\\/:\*\?\"<>|]/g,"_")
        return fn
    }

    // global list of folders to process
    property var folderList
    // global list of files to process
    property var fileList

    // variable to remember current parent score for parts
    property var curBaseScore

    // FolderListModel can be used to search the file system
    FolderListModel {
        id: files
    }

    FileIO {
        id: fileExcerpt
    }
    
    FileIO {
        id: fileScore // We need two because they they are used from 2 different processes,
        // which could cause threading problems
    }

    Timer {
        id: processTimer
        interval: 1
        running: false

        // this function processes one file and then
        // gives control back to Qt to update the dialog
        onTriggered: {
            if (fileList.length === 0) {
                // no more files to process
                workDialog.standardButtons = StandardButton.Ok
                if (!abortRequested)
                    currentStatus.text = /*qsTr("Done.")*/ qsTranslate("QWizzard", "Done") + "."
                else
                    console.log("abort!")
                return
            }

            var curFileInfo = fileList.shift()
            var filePath = curFileInfo[0]
            var fileName = curFileInfo[1]
            var fileExt = curFileInfo[2]

            var fileFullPath = filePath + fileName + "." + fileExt

            // read file
            var thisScore = readScore(fileFullPath, true)

            // make sure we have a valid score
            if (thisScore) {
                // get modification time of source file
                fileScore.source = fileFullPath
                var srcModifiedTime = fileScore.modifiedTime()
                // write for all target formats
                for (var j = 0; j < outFormats.extensions.length; j++) {
                    if (differentExportPath.checked && !traverseSubdirs.checked)
                        fileScore.source = targetFolderDialog.folderPath + "/" + fileName + "." + outFormats.extensions[j]
                    else
                        fileScore.source = filePath + fileName + "." + outFormats.extensions[j]

                    // get modification time of destination file (if it exists)
                    // modifiedTime() will return 0 for non-existing files
                    // if src is newer than existing write this file
                    if (srcModifiedTime > fileScore.modifiedTime()) {
                        var res = writeScore(thisScore, fileScore.source, outFormats.extensions[j])

                        if (res)
                            resultText.append("%1 → %2".arg(fileFullPath).arg(outFormats.extensions[j]))
                        else
                            resultText.append(qsTr("Error: %1 → %2 not exported").arg(fileFullPath).arg(outFormats.extensions[j]))
                    }
                    else
                        resultText.append(qsTr("%1 is up to date").arg(fileFullPath))
                }
                // check if we are supposed to export parts
                if (exportExcerpts.checked) {
                    // reset list
                    excerptsList = []
                    // do we have excertps?
                    var excerpts = thisScore.excerpts
                    for (var ex = 0; ex < excerpts.length; ex++) {
                        if (excerpts[ex].partScore !== thisScore) // only list when not base score
                            excerptsList.push([excerpts[ex], filePath, fileName, srcModifiedTime])
                    }
                    // if we have files start timer
                    if (excerpts.length > 0) {
                        curBaseScore = thisScore // to be able to close this later
                        excerptTimer.running = true
                        return
                    }
                }
                closeScore(thisScore)
            }
            else
                resultText.append(qsTr("ERROR reading file %1").arg(fileName))

            // next file
            if (!abortRequested)
                processTimer.running = true
        }
    }

    // FolderListModel returns what Qt calles the
    // completeSuffix for "fileSuffix" which means everything
    // that follows the first '.' in a file name. (e.g. 'tar.gz')
    // However, this is not what we want:
    // For us the suffix is the part after the last '.'
    // because some users have dots in their file names.
    // Qt::FileInfo::suffix() would get this, but seems not
    // to be available in FolderListModel.
    // So, we need to do this ourselves:
    function getFileSuffix(fileName) {

        var n = fileName.lastIndexOf(".");
        var suffix = fileName.substring(n+1);

        return suffix
    }

    // This timer contains the function that will be called
    // once the FolderListModel is set.
    Timer {
        id: collectFiles
        interval: 25
        running: false

        // Add all files found by FolderListModel to our list
        onTriggered: {
            // to be able to show what we're doing
            // we must create a list of files to process
            // and then use a timer to do the work
            // otherwise, the dialog window will not update

            for (var i = 0; i < files.count; i++) {

                // if we have a directory, we're supposed to
                // traverse it, so add it to folderList
                if (files.isFolder(i))
                    folderList.push(files.get(i, "fileURL"))
                else if (inInputFormats(getFileSuffix(files.get(i, "fileName")))) {
                    // found a file to process
                    // set file names for in and out files

                    // We need 3 things:
                    // 1) The file path: C:/Path/To/
                    // 2) The file name:            my_score
                    //                                      .
                    // 3) The file's extension:              mscz

                    var fln = files.get(i, "fileName") // returns  "my_score.mscz"
                    var flp = files.get(i, "filePath") // returns  "C:/Path/To/my_score.mscz"

                    var fileExt  = getFileSuffix(fln);  // mscz
                    var fileName = fln.substring(0, fln.length - fileExt.length - 1)
                    var filePath = flp.substring(0, flp.length - fln.length)

                    /// in doubt uncomment to double check
                    // console.log("fln", fln)
                    // console.log("flp", flp)
                    // console.log("fileExt", fileExt)
                    // console.log("fileName", fileName)
                    // console.log("filePath", filePath)

                    fileList.push([filePath, fileName, fileExt])
                }
            }

            // if folderList is non-empty we need to redo this for the next folder
            if (folderList.length > 0) {
                files.folder = folderList.shift()
                // restart timer for folder search
                collectFiles.running = true
            } else if (fileList.length > 0) {
                // if we found files, start timer do process them
                processTimer.running = true
            }
            else {
                // we didn't find any files
                // report this
                resultText.append(qsTr("No files found"))
                workDialog.standardButtons = StandardButton.Ok
                currentStatus.text = /*qsTr("Done.")*/ qsTranslate("QWizzard", "Done") + "."
            }
        }
    }

    function work() {
        console.log((traverseSubdirs.checked? "Sources Startfolder: ":"Sources Folder: ")
                    + sourceFolderDialog.folder)

        if (differentExportPath.checked && !traverseSubdirs.checked)
            console.log("Export folder: " + targetFolderDialog.folderPath)

        // initialize global variables
        fileList = []
        folderList = []

        // set folder and filter in FolderListModel
        files.folder = sourceFolderDialog.folder

        if (traverseSubdirs.checked) {
            files.showDirs = true
            files.showFiles = true
        }
        else {
            // only look for files
            files.showFiles = true
            files.showDirs = false
        }

        // wait for FolderListModel to update
        // therefore we start a timer that will
        // wait for 25 millis and then start working
        collectFiles.running = true
        workDialog.visible = true
    } // work
} // MuseScore
