(function() {
    var STAGE_WIDTH = 500;
    var STAGE_HEIGHT = 640;
    var SET_MODE = "SET";
    var GET_MODE = "GET";
    var FILL_MODE = "FILL";
    var ALL_MODE = "ALL";

    var CELL_OFFSETS = [
            [0, 0],
            [0, -1],
            [0, -1],
            [1, -1],
            [0, 1],
            [0, 1],
            [0, 1],
            [1, 0],
            [0, -1],
            [0, -1],
            [0, -1],
            [0, -1],
            [1, -1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [1, -1],
            [0, -1],
            [0, -1],
            [0, -1],
            [0, -1],
            [1, -1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [1, -1],
            [0, -1],
            [0, -1],
            [0, -1],
            [0, -1],
            [1, -1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [1, -1],
            [0, -1],
            [0, -1],
            [0, -1],
            [0, -1],
            [1, -1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [1, -1],
            [0, -1],
            [0, -1],
            [0, -1],
            [0, -1],
            [1, 0],
            [0, 1],
            [0, 1],
            [0, 1],
            [1, -1],
            [0, -1],
            [0, -1],
        ];
    var CELL_RADIUS = 25;
    var CELL_X = 30;
    var CELL_Y = 185;
    var cells = [];

    var stage;

    var frames = [];
    var frameIndex = 0;
    var mode = SET_MODE;
    var isPlaying = false;

    var cellNeighbors = [];
    cellNeighbors[0] =  [1, 5, 6, null, null, null];
    cellNeighbors[1] =  [2, 4, 5, 0, null, null];
    cellNeighbors[2] =  [null, 3, 4, 1, null, null];
    cellNeighbors[3] =  [null, 11, 10, 4, 2, null];
    cellNeighbors[4] =  [3, 10, 9, 5, 1, 2];
    cellNeighbors[5] =  [4, 9, 8, 6, 0, 1];
    cellNeighbors[6] =  [5, 8, 7, null, null, 0];
    cellNeighbors[7] =  [8, 16, 17, null, null, 6];
    cellNeighbors[8] =  [9, 15, 16, 7, 6, 5];
    cellNeighbors[9] =  [10, 14, 15, 8, 5, 4];
    cellNeighbors[10] =  [11, 13, 14, 9, 4, 3];
    cellNeighbors[11] =  [null, 12, 13, 10, 3, null];
    cellNeighbors[12] =  [null, null, 22, 13, 11, null];
    cellNeighbors[13] =  [12, 22, 21, 14, 10, 11];
    cellNeighbors[14] =  [13, 21, 20, 15, 9, 10];
    cellNeighbors[15] =  [14, 20, 19, 16, 8, 9];
    cellNeighbors[16] =  [15, 19, 18, 17, 7, 8];
    cellNeighbors[17] =  [16, 18, null, null, null, 7];
    cellNeighbors[18] =  [19, 27, 28, null, 17, 16];
    cellNeighbors[19] =  [20, 26, 27, 18, 16, 15];
    cellNeighbors[20] =  [21, 25, 26, 19, 15, 14];
    cellNeighbors[21] =  [22, 24, 25, 20, 14, 13];
    cellNeighbors[22] =  [null, 23, 24, 21, 13, 12];
    cellNeighbors[23] =  [null, null, 33, 24, 22, null];
    cellNeighbors[24] =  [23, 33, 32, 25, 21, 22];
    cellNeighbors[25] =  [24, 32, 31, 26, 20, 21];
    cellNeighbors[26] =  [25, 31, 30, 27, 19, 20];
    cellNeighbors[27] =  [26, 30, 29, 28, 18, 19];
    cellNeighbors[28] =  [27, 29, null, null, null, 18];
    cellNeighbors[29] =  [30, 38, 39, null, 28, 27];
    cellNeighbors[30] =  [31, 37, 38, 29, 27, 26];
    cellNeighbors[31] =  [32, 36, 37, 30, 26, 25];
    cellNeighbors[32] =  [33, 35, 36, 31, 25, 24];
    cellNeighbors[33] =  [null, 34, 35, 32, 24, 23];
    cellNeighbors[34] =  [null, null, 44, 35, 33, null];
    cellNeighbors[35] =  [34, 44, 43, 36, 32, 33];
    cellNeighbors[36] =  [35, 43, 42, 37, 31, 32];
    cellNeighbors[37] =  [36, 42, 41, 38, 30, 31];
    cellNeighbors[38] =  [37, 41, 40, 39, 29, 30];
    cellNeighbors[39] =  [38, 40, null, null, null, 29];
    cellNeighbors[40] =  [41, 49, 50, null, 39, 38];
    cellNeighbors[41] =  [42, 48, 49, 40, 38, 37];
    cellNeighbors[42] =  [43, 47, 48, 41, 37, 36];
    cellNeighbors[43] =  [44, 46, 47, 42, 36, 35];
    cellNeighbors[44] =  [null, 45, 46, 43, 35, 34];
    cellNeighbors[45] =  [null, null, 55, 46, 44, null];
    cellNeighbors[46] =  [45, 55, 54, 47, 43, 44];
    cellNeighbors[47] =  [46, 54, 53, 48, 42, 43];
    cellNeighbors[48] =  [47, 53, 52, 49, 41, 42];
    cellNeighbors[49] =  [48, 52, 51, 50, 40, 41];
    cellNeighbors[50] =  [49, 51, null, null, null, 40];
    cellNeighbors[51] =  [52, 59, null, null, 50, 49];
    cellNeighbors[52] =  [53, 58, 59, 51, 49, 48];
    cellNeighbors[53] =  [54, 57, 58, 52, 48, 47];
    cellNeighbors[54] =  [55, 56, 57, 53, 47, 46];
    cellNeighbors[55] =  [null, null, 56, 54, 46, 45];
    cellNeighbors[56] =  [null, null, 62, 57, 54, 55];
    cellNeighbors[57] =  [56, 62, 61, 58, 53, 54];
    cellNeighbors[58] =  [57, 61, 60, 59, 52, 53];
    cellNeighbors[59] =  [58, 60, null, null, 51, 52];
    cellNeighbors[60] =  [61, null, null, null, 59, 58];
    cellNeighbors[61] =  [62, null, null, 60, 58, 57];
    cellNeighbors[62] =  [null, null, null, 61, 57, 56];

    function updateEye() {
        for (var i=0; i<cells.length; ++i) {
            cell = cells[i];
            g = cell.graphics;
            g.clear();
            g.setStrokeStyle(1);
            g.beginStroke("#000");
            g.beginFill("#" + frames[frameIndex][i]);
            g.drawPolyStar(0, 0, CELL_RADIUS, 6, 0, 0);
            g.endFill();
        }
        stage.update();
    }

    function onClickCell(event) {
        var id = event.target.id;

        if (mode == GET_MODE) {
            $(".pick-a-color").focus();
            $(".pick-a-color").val(frames[frameIndex][id]);
            $(".pick-a-color").blur();
            $("#set-color").click();
        }

        if (mode == SET_MODE) {
            stage.enableMouseOver(10);

            var color = $(".pick-a-color").val();
            frames[frameIndex][id] = color;

            updateEye();
        }

        if (mode == FILL_MODE) {
            var color = frames[frameIndex][id];
            var cellTable = {};

            getFillArea(id, color, cellTable, {});

            var nextColor = $(".pick-a-color").val();

            for (id in cellTable) {
                frames[frameIndex][id] = nextColor;
            }

            updateEye();

            $("#set-color").click();
        }

        if (mode == ALL_MODE) {
            var color = $(".pick-a-color").val();
            for (var i=0; i<cells.length; ++i) {
                frames[frameIndex][i] = color;
            }
            updateEye();
            $("#set-color").click();
        }
    }

    function getFillArea(id, color, cellTable, visited) {
        visited[id] = true;

        if (frames[frameIndex][id] == color) {
            cellTable[id] = true;

            for (var i=0; i<6; ++i) {
                if (cellNeighbors[id][i] != null && visited[cellNeighbors[id][i]] == null) {
                    getFillArea(cellNeighbors[id][i], color, cellTable, visited);
                }
            }
        }
    }

    function onRollOverCell(event) {
        var id = event.target.id;
        var color = $(".pick-a-color").val();
        frames[frameIndex][id] = color;

        updateEye();
    }

    function updateFrameList() {
        var frameList = $("#frames");
        frameList.empty();

        for (var i=0; i<frames.length; ++i) {
            var option = $("<option></option>").attr("value", i).text(i+1);
            frameList.append(option);
        }

        frameList.val(frameIndex);
    }

    function animateEye(event) {
        if (event.paused == false) {
            frameIndex++;

            if (frameIndex == frames.length) {
                frameIndex = 0;
            }

            var list = $("#frames option");

            for (var i=0; i<list.length; ++i) {
                if (i == frameIndex) {
                    $(list[i]).attr("selected", true);
                } else {
                    $(list[i]).removeAttr("selected");
                }
            }

            updateEye();
        }
    }

    function shiftCells(direction) {
        var currentFrame = frames[frameIndex];
        var newFrame = [];
        var neighbor;
        var color = $(".pick-a-color").val();

        for (var i=0; i<currentFrame.length; ++i) {
            neighbor = cellNeighbors[i][direction];
            if (neighbor == null) {
                newFrame[i] = color;
            } else {
                newFrame[i] = currentFrame[neighbor];
            }
        }

        frames[frameIndex] = newFrame;
        updateEye();

    }

    function init() {
        var cell;
        var g;
        var x = CELL_X;
        var y = CELL_Y;
        var offset = Math.cos(60/(Math.PI/2)) * CELL_RADIUS * 2;

        $(".pick-a-color").pickAColor({
            showSpectrum            : true,
            showSavedColors         : true,
            saveColorsPerElement    : true,
            fadeMenuToggle          : true,
            showAdvanced            : true,
            showBasicColors         : true,
            showHexInput            : true,
            allowBlank              : false
        });


        $('input[type=radio][name=mode]').change(function(event) {
            mode = event.target.value;
        });

        $("#new-frame").click(function() {
            var frame = [];
            for (var i=0; i<cells.length; ++i) {
                frame[i] = "ffffff";
            }

            frames.splice(frameIndex+1, 0, frame);
            frameIndex++;
            updateFrameList();
            updateEye();
        });

        $("#duplicate-frame").click(function() {
            var selected = $("#frames").val();
            var newFrames = [];
            var insertPoint = parseInt(frameIndex) + selected.length;
            var newSelected = [];

            for (var i=0; i<selected.length; ++i) {
                var frame = [];
                for (var j=0; j<cells.length; ++j) {
                    frame[j] = frames[selected[i]][j];
                }

                newFrames.push(frame);

                newSelected.push(String(i + insertPoint));
            }

            for (var i=0; i<newFrames.length; ++i) {
                frames.splice(i  + insertPoint , 0, newFrames[i]);
            }

            updateFrameList();
            frameIndex = insertPoint;
            $("#frames").val(newSelected);


            updateEye();
        });

        $("#reverse-frames").click(function() {
            var selected = $("#frames").val();

            for (var i=0; i<Math.floor(selected.length/2); ++i) {
                var tmp = frames[selected[i]];
                frames[selected[i]] = frames[selected[selected.length - i - 1]];
                frames[selected[selected.length - i - 1]] = tmp;
            }

            updateEye();
        });

        $("#delete-frame").click(function() {
            if (frames.length > 1) {
                var max = $("#frames").val().length;

                frames.splice(frameIndex, max);
                frameIndex -= max;

                updateFrameList();
                updateEye();
            }
        });

        $("#down-frame").click(function() {
            var max = $("#frames").val().length;
            if (frameIndex + max < frames.length) {
                var newSelection = [];
                var movedFrames = [];

                for (var i=0; i<max; ++i) {
                    movedFrames.push(frames[frameIndex + i]);
                    newSelection.push(parseInt(frameIndex) +i + 1);
                }

                frames.splice(frameIndex, max);

                for (var i=0; i<max; ++i) {
                    frames.splice(frameIndex + i + 1, 0, movedFrames[i]);
                }

                updateFrameList();
                frameIndex += 1
                $("#frames").val(newSelection);
                updateEye();
            }
        });

        $("#up-frame").click(function() {
            var max = $("#frames").val().length;
            if (frameIndex > 0) {
                var newSelection = [];
                var movedFrames = [];

                for (var i=0; i<max; ++i) {
                    movedFrames.push(frames[frameIndex + i]);
                    newSelection.push(parseInt(frameIndex) +i - 1);
                }

                frames.splice(frameIndex, max);

                for (var i=0; i<max; ++i) {
                    frames.splice(frameIndex + i - 1, 0, movedFrames[i]);
                }

                updateFrameList();
                frameIndex -= 1
                $("#frames").val(newSelection);
                updateEye();
            }
        });

        $("#play-toggle").click(function() {
            if (isPlaying == false) {
                isPlaying = true;
                $("input").prop('disabled', true);
                $("button").prop('disabled', true);
                $("select").prop('disabled', true);
                $("label").prop('disabled', true);

                $("#play-toggle").removeClass("btn-success");
                $("#play-toggle").addClass("btn-danger");
                $("#play-toggle").prop('disabled', false);
                $("#play-toggle").text("Stop Animation");
                createjs.Ticker.setPaused(false);
            } else {
                isPlaying = false;
                $("input").prop('disabled', false);
                $("button").prop('disabled', false);
                $("select").prop('disabled', false);

                $("#play-toggle").addClass("btn-success");
                $("#play-toggle").removeClass("btn-danger");
                $("#play-toggle").text("Start Animation");
                createjs.Ticker.setPaused(true);
                updateFrameList();
                updateEye();
            }
        });

        $("#frames").change(function() {
            var selected = $("#frames").val();

            var list = [];
            for (var i=selected[0]; i<=selected[selected.length -1]; ++i) {
                list.push(i);
            }

            $("#frames").val(list);

            frameIndex = parseInt(selected[0]);

            updateEye();
        });

        $("#save").click(function() {
            window.URL = window.webkitURL || window.URL;

            var MIME_TYPE = "application/json";
            var filename = prompt("File name");
            var textFileAsBlob = new Blob([JSON.stringify(frames)], {type:MIME_TYPE});

            var downloadLink = document.createElement("a");
            downloadLink.download = filename;
            downloadLink.innerHTML = "Download File";
            downloadLink.href = window.webkitURL.createObjectURL(textFileAsBlob);
            downloadLink.draggable = true;
            downloadLink.dataset.downloadurl = [MIME_TYPE, downloadLink.download, downloadLink.href].join(':');
            downloadLink.click();
        })

        $("#load").click(function() {
            $("#loader").click();
        });

        $("#shift-n").click(function() { shiftCells(3) });
        $("#shift-ne").click(function() { shiftCells(4) });
        $("#shift-se").click(function() { shiftCells(5) });
        $("#shift-s").click(function() { shiftCells(0) });
        $("#shift-sw").click(function() { shiftCells(1) });
        $("#shift-nw").click(function() { shiftCells(2) });

        $("#loader").change(function(){
            var fileToLoad = document.getElementById("loader").files[0];

            var fileReader = new FileReader();
            fileReader.onload = function(fileLoadedEvent)
            {
                var data = fileLoadedEvent.target.result;
                frames = JSON.parse(data);
                frameIndex = 0;
                updateFrameList();
                updateEye();
            };
            fileReader.readAsText(fileToLoad, "UTF-8");
        })

        stage = new createjs.Stage($("canvas")[0]);
        stage.addEventListener("stagemouseup", function() {
            stage.enableMouseOver(0);
        });

        $("canvas").mousedown(function(event){
            event.preventDefault();
            return false;
        });

        for (var i=0; i<CELL_OFFSETS.length; ++i) {
            cell = new createjs.Shape();
            g = cell.graphics;
            g.setStrokeStyle(1);
            g.beginStroke("#000");
            g.drawPolyStar(0, 0, CELL_RADIUS, 6, 0, 0);

            if (CELL_OFFSETS[i][0] == 1) {
                x += CELL_RADIUS + offset/4;
                y += offset/2
            }
            y += CELL_OFFSETS[i][1] * offset;
            cell.x = x;
            cell.y = y;
            cell.id = i;
            cells.push(cell);
            stage.addChild(cell);
            cell.addEventListener("mousedown", onClickCell);
            cell.addEventListener("rollover", onRollOverCell);
        }


        frames[0] = [];
        for (var i=0; i<cells.length; ++i) {
            frames[0][i] = "ffffff";
        }

        updateFrameList();

        updateEye();

        createjs.Ticker.addEventListener("tick", animateEye);
        createjs.Ticker.setFPS(30);
        createjs.Ticker.setPaused(true);
    }

    $(document).ready(init);

})();
