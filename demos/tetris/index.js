TETRISCONFIG = {
    speed_modifier: 1.0005,
    w: 10,
    h: 24,
    color1: "#91e52b",
    color2: "#e5e22b",
    color3: "#2b98e5",
    color4: "#e52bd6",
    color5: "#e5372b",
    color6: "#2b60e5",
    color7: "#d82ce6",
    bg: "#ffffff",
    bg_board: "#e8e1e1",
    bg_board_grid: "#b7b7b7",
    fg: "#383636",
    initial_delay: 300,
    fast_drop_delay: 70,
    padding: 25,
    border_w: 2,
    redraw_interval: 150,
    text_size: 40
}

class Piece{
    constructor(color, rotation_matrices){
        this.color = color
        this.rotation_matrices = rotation_matrices
    }
}

class BoardPiece{
    constructor(matrix, x, y, piece, rotation, color_index){
        this.matrix = matrix
        this.x = x
        this.y = y
        this.piece = piece
        this.rotation = rotation
        this.color_index = color_index
    }
}

// colored PIECE values range from 0 to len(PIECES) - 1
const PIECE = 0
const NO_PIECE = -1

class Matrix{
    constructor(arr, w, h){
        this.arr = arr
        this.w = w
        this.h = h
    }

    at(x, y){
        let i = this.w*y + x
        if (x < 0 || x >= this.w || y < 0 || y >= this.h)return PIECE
        return this.arr[i]
    }

    set(x, y, value){
        this.arr[this.w*y + x] = value
    }
}

PIECES = [
    new Piece(TETRISCONFIG.color1,[new Matrix([1, 1, 1, 1], 2, 2), new Matrix([1, 1, 1, 1], 2, 2), new Matrix([1, 1, 1, 1], 2, 2), new Matrix([1, 1, 1, 1], 2, 2)]),
    new Piece(TETRISCONFIG.color2, [new Matrix([0, 1, 0, 1, 1, 1, 0, 0, 0], 3, 3), new Matrix([0, 1, 0, 0, 1, 1, 0, 1, 0], 3, 3), new Matrix([0, 0, 0, 1, 1, 1, 0, 1, 0], 3, 3), new Matrix([0, 1, 0, 1, 1, 0, 0, 1, 0], 3, 3)]),
    new Piece(TETRISCONFIG.color3, [new Matrix([0, 0, 0, 1, 1, 1, 0, 0, 1], 3, 3), new Matrix([0, 1, 0, 0, 1, 0, 1, 1, 0], 3, 3), new Matrix([1, 0, 0, 1, 1, 1, 0, 0, 0], 3, 3), new Matrix([0, 1, 1, 0, 1, 0, 0, 1, 0], 3, 3)]),
    new Piece(TETRISCONFIG.color4, [new Matrix([1, 0, 0, 1, 1, 0, 0, 1, 0], 3, 3), new Matrix([0, 1, 1, 1, 1, 0, 0, 0, 0], 3, 3), new Matrix([0, 1, 0, 0, 1, 1, 0, 0, 1], 3, 3), new Matrix([0, 0, 0, 0, 1, 1, 1, 1, 0], 3, 3)]),
    new Piece(TETRISCONFIG.color5, [new Matrix([0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 4, 4), new Matrix([0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0], 4, 4), new Matrix([0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0], 4, 4), new Matrix([0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0], 4, 4)]),
    new Piece(TETRISCONFIG.color6, [new Matrix([0, 0, 0, 1, 1, 1, 1, 0, 0], 3, 3), new Matrix([0, 1, 0, 0, 1, 0, 0, 1, 1], 3, 3), new Matrix([0, 0, 1, 1, 1, 1, 0, 0, 0], 3, 3), new Matrix([1, 1, 0, 0, 1, 0, 0, 1, 0], 3, 3)]),
    new Piece(TETRISCONFIG.color7, [new Matrix([0, 0, 1, 0, 1, 1, 0, 1, 0], 3, 3), new Matrix([1, 1, 0, 0, 1, 1, 0, 0, 0], 3, 3), new Matrix([0, 1, 0, 1, 1, 0, 1, 0, 0], 3, 3), new Matrix([0, 0, 0, 1, 1, 0, 0, 1, 1], 3, 3)])
    
]

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

var PIXEL_RATIO = (function () {
    var ctx = document.createElement("canvas").getContext("2d"),
        dpr = window.devicePixelRatio || 1,
        bsr = ctx.webkitBackingStorePixelRatio ||
              ctx.mozBackingStorePixelRatio ||
              ctx.msBackingStorePixelRatio ||
              ctx.oBackingStorePixelRatio ||
              ctx.backingStorePixelRatio || 1;

    return dpr / bsr;
})() * 4;


class Tetris{
    constructor(canvas_id, config){
        this.canvas = document.getElementById(canvas_id)
        this.canvas.width = this.canvas.clientWidth * PIXEL_RATIO
        this.canvas.height = this.canvas.clientHeight * PIXEL_RATIO
        this.canvas.getContext("2d").setTransform(PIXEL_RATIO, 0, 0, PIXEL_RATIO, 0, 0)
        this.ctx = this.canvas.getContext("2d", {alpha: false})
        this.ctx.shadowBlur = 0
        this.config = config
        this.bounds = {
            x: 0,
            y: 0,
            w: this.canvas.clientWidth,
            h: this.canvas.clientHeight
        }
        this.interval = this.config.initial_delay

        this.score = 0

        this.down_fast = false
        
        this.clear_board()
        
        this.next_piece = this.random_board_piece()
        this.next()

        this.calc_sizes()

    }

    calc_sizes(){
        let board_w = (this.bounds.w / 2) - this.config.padding * 2
        let cell_w = Math.round(board_w / this.board.w)

        let board_h = this.bounds.h - this.config.padding * 2
        let cell_h = Math.round(board_h / this.board.h)
        cell_h = cell_w = Math.min(cell_w, cell_h)


        board_w = cell_w * this.board.w
        board_h = cell_h * this.board.h
        this.board_w = board_w
        this.board_x = (this.bounds.w - board_w) / 2
        this.board_h = board_h
        this.cell_w = cell_w
        this.cell_h = cell_h
    }

    next(){
        this.current_piece = this.next_piece
        this.next_piece = this.random_board_piece()
    }

    random_board_piece(){
        let color_index = getRandomInt(PIECES.length)
        let type = PIECES[color_index]
        let rot = getRandomInt(3)
        let matrix = type.rotation_matrices[rot]
        return new BoardPiece(matrix, Math.round((this.board.w - matrix.w) / 2), 0, type, rot, color_index)
    }

    clear_board(){
        this.board = new Matrix(Array(this.config.w*this.config.h).fill(NO_PIECE), this.config.w, this.config.h)
    }

    draw_board(){
        this.set_color(this.config.bg_board)
        this.ctx.fillRect(this.board_x, this.config.padding, this.board_w, this.board_h)

        for (let i = 0; i < this.board.w; i++){
            for (let j = 0; j < this.board.h; j++){
                let value = this.board.at(i, j)
                if (value == NO_PIECE){
                    this.set_color(this.config.bg_board)
                }
                else {
                    this.set_color(PIECES[value].color)
                }
                this.ctx.fillRect(this.board_x + this.cell_w * i, this.config.padding + this.cell_h * j, this.cell_w, this.cell_h)
            }
        }

        this.set_color(this.current_piece.color)
        for (let i = 0; i < this.current_piece.matrix.w; i++) {
            for (let j = 0; j < this.current_piece.matrix.h; j++){
                let value = this.current_piece.matrix.at(i, j)
                if (value == 0){
                    continue
                }
                else {
                    this.set_color(this.current_piece.piece.color)
                }
                
                this.ctx.fillRect(this.board_x + this.cell_w * (i + this.current_piece.x), this.config.padding + this.cell_h * (j + this.current_piece.y), this.cell_w, this.cell_h)
            }
        }

        this.set_color(this.config.bg_board_grid)
        for (let i = 0; i <= this.board.w; i++){
            this.ctx.fillRect(this.board_x + this.cell_w * i - this.config.border_w / 2, this.config.padding, this.config.border_w, this.board_h)
        }
        for (let i = 0; i <= this.board.h; i++){
            this.ctx.fillRect(this.board_x, this.config.padding + this.cell_h * i - this.config.border_w / 2, this.board_w, this.config.border_w)
        }
    }

    draw_next(){
        let board_w = this.cell_w * this.next_piece.matrix.w
        let board_h = this.cell_h * this.next_piece.matrix.h

        let start_x = this.board_x + this.config.padding + this.board_w
        this.set_color(this.config.bg_board)
        this.ctx.fillRect(start_x, this.config.padding, board_w, board_h)
        for (let i = 0; i < this.next_piece.matrix.w; i++){
            for (let j = 0; j < this.next_piece.matrix.h; j++){
                let value = this.next_piece.matrix.at(i, j)
                if (value == 0){
                    this.set_color(this.config.bg_board)
                }
                else {
                    this.set_color(PIECES[this.next_piece.color_index].color)
                }
                this.ctx.fillRect(start_x + this.cell_w * i, this.config.padding + this.cell_h * j, this.cell_w, this.cell_h)
            }
        }

        this.set_color(this.config.bg_board_grid)
        for (let i = 0; i <= this.next_piece.matrix.w; i++){
            this.ctx.fillRect(start_x + this.cell_w * i - this.config.border_w / 2, this.config.padding, this.config.border_w, board_h)
        }
        for (let i = 0; i <= this.next_piece.matrix.h; i++){
            this.ctx.fillRect(start_x, this.config.padding + this.cell_h * i - this.config.border_w / 2, board_w, this.config.border_w)
        }
    }

    draw_score(){
        this.set_color(this.config.fg)
        this.ctx.font = "" + this.config.text_size + "px Arial"
        
        this.ctx.fillText("Score: " + this.score, this.config.padding, this.config.padding + this.config.text_size)
    }

    redraw(){
        this.set_color(this.config.bg)
        this.ctx.fillRect(0, 0, this.bounds.w, this.bounds.h)
        this.draw_board()
        this.draw_next()
        this.draw_score()
        this.ctx.imageSmoothingEnabled = false
    }

    drop(){
        if (this.down_fast)return
        this.down_fast = true
        this.stop()
        this.start(this.config.fast_drop_delay)
    }

    check_intersects(){
        for (let i = 0; i < this.current_piece.matrix.w; i++){
            let y_index = -1
            for (let j = this.current_piece.matrix.h - 1; j >= 0; j--){
                if (this.current_piece.matrix.at(i, j) != 0){
                    y_index = j
                    break
                }
            }
            if (y_index == -1)continue
            if (this.board.at(this.current_piece.x + i, this.current_piece.y + y_index + 1) != NO_PIECE){
                //FOUND SOMETHING!
                this.place()
                this.check_clear()
                return
            }
        }
    }

    is_row_filled(j){
        for (let i = 0; i < this.board.w; i++){
            if (this.board.at(i,j) == NO_PIECE)return false
        }
        return true
    }

    clear_row(j){
        for (let i = 0; i < this.board.w; i++){
            this.board.set(i,j, NO_PIECE)
        }
    }

    move_rows_down(j){
        if (j == 0)return
        for (let k = j; k > 0; k--){
            for (let i = 0; i < this.board.w; i++){
                this.board.set(i, k, this.board.at(i, k-1))
            }
        }
    }

    check_clear(){
        let cleared_rows = 0
        for (let j = this.board.h-1; j >= 0; j--){
            if (this.is_row_filled(j)){
                this.clear_row(j)
                this.move_rows_down(j)
                cleared_rows++
                
                j++
            }
        }
        this.score += Math.round((this.board.w * cleared_rows) * Math.max(1, cleared_rows / 1.5))
    }

    place(){
        for (let i = 0; i < this.current_piece.matrix.w; i++){
            for (let j = 0; j < this.current_piece.matrix.h; j++){
                if (this.current_piece.matrix.at(i, j) != 0){
                    this.board.set(this.current_piece.x + i, this.current_piece.y + j, this.current_piece.color_index)
                }
            }
        }
        this.down_fast = false
        this.stop()
        this.next()
        this.adjust_interval()
        
        this.start()
    }

    adjust_interval(){
        this.interval *= this.config.speed_modifier
    }

    move_down(){
        this.current_piece.y++
        this.check_intersects()
    }
    
    physics(){
        this.move_down()  
    }

    set_color(color){
        this.ctx.fillStyle = color
        this.ctx.strokeStyle = color
    }

    start(interval = this.interval){
        this.gameloop = setInterval(()=>{
            tetris.physics()
            //tetris.redraw()
        },interval, interval)
        this.renderloop = setInterval(()=>{
            tetris.redraw()
        }, this.config.redraw_interval)
    }

    stop(){
        clearInterval(this.gameloop)
        clearInterval(this.renderloop)
    }

    try_position(x, y, matrix){
        for (let i = 0; i < matrix.w; i++){
            for (let j = 0; j < matrix.h; j++){
                if (matrix.at(i, j) == 1 && this.board.at(x + i, y + j) != NO_PIECE)return false
            }
        }
        return true
    }

    turn_clockwise(){
        // if (this.down_fast)return
        let i = (this.current_piece.rotation+1) % 4
        let matrix = this.current_piece.piece.rotation_matrices[i]
        if (this.try_position(this.current_piece.x, this.current_piece.y, matrix)){
            this.current_piece.matrix = matrix
            this.current_piece.rotation = i
        }
    }

    turn_counterclockwise(){
        // if (this.down_fast)return
        let i = this.current_piece.rotation-1
        if (i == -1)i = 3
        let matrix = this.current_piece.piece.rotation_matrices[i]
        if (this.try_position(this.current_piece.x, this.current_piece.y, matrix)){
            this.current_piece.matrix = matrix
            this.current_piece.rotation = i
        }
    }

    left(){
        // if (this.down_fast)return
        if (this.try_position(this.current_piece.x-1,this.current_piece.y,this.current_piece.matrix)){
            this.current_piece.x--
        }
    }

    right(){
        // if (this.down_fast)return
        if (this.try_position(this.current_piece.x+1,this.current_piece.y,this.current_piece.matrix)){
            this.current_piece.x++
        }
    }
}

var speed1 = 0;
var speed2 = 0;
var rotateCount = 0;
var speedCount = 3;
const LOC1_ID = 16390;
const LOC2_ID = 16389;

window.onload = ()=>{
    let music = document.getElementById("music")
    music.volume = 0.4
    window.tetris = new Tetris("screen", TETRISCONFIG)

    websocket = new WebSocket("ws://127.0.0.1:8001")

    tetris.start()

    websocket.addEventListener("message", (e) => {
        let t = e.data.substring(0, e.data.indexOf("{"))
        let data = e.data.substring(e.data.indexOf("{"))
        data = JSON.parse(data)
        if (t === "LocomotiveSpeedCommand") {
            let speed = data.speed;
            if (data.loc_id === LOC1_ID) {
                // rotate
                if (speed < speed1 || speed === 0) {
                    rotateCount -= 1;
                } else if (speed === 0) {
                    rotateCount -= 3;
                } else if (speed >= 1000){
                    rotateCount += 3;
                } else {
                    rotateCount += 1;
                }
                if (rotateCount > 5) {
                    tetris.turn_clockwise();
                    rotateCount = 0;
                } else if (rotateCount < -5) {
                    tetris.turn_counterclockwise();
                    rotateCount = 0;
                }
                speed1 = speed;
            } else if (data.loc_id === LOC2_ID) {
                // move
                if (speed < speed2) {
                    speedCount -= 1;
                } else if (speed === 0)  {
                    speedCount -= 3;
                } else if (speed >= 1000) {
                    speedCount += 3;
                } else {
                    speedCount += 1;
                }
                if (speedCount > 2) {
                    speedCount = 0;
                    tetris.right();
                } else if (speedCount < -2) {
                    speedCount = 0;
                    tetris.left();
                }
                speed2 = speed;
            }
        } else if (t === "LocomotiveDirectionCommand") {
            tetris.drop();
        } else {
            console.log(t);
        }
    })
}

window.onkeydown = (e) => {
    if (e.key == "ArrowLeft")tetris.left()
    else if (e.key == "ArrowRight")tetris.right()
    else if (e.key == "ArrowDown")tetris.drop()
    else if (e.key == "d")tetris.turn_clockwise()
    else if (e.key == "a")tetris.turn_counterclockwise()
}