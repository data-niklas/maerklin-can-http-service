BIRDCONFIG = {
    bg: "#ffffff",
    fg: "#000000",
    ball: "#b02a4b",
    pipe_bg: "#48b12a",
    pipe_w: 40,
    interval: 50,
    pipe_space: 180,
    bird_velocity: 20,
    gravity: 1.7,
    bird_size: 20,
    bird_x: 800,
    pipe_interval: 5000,
    pipe_velocity: 3.5,
    text_size: 30
}

class Bird{
    constructor(y){
        this.y = y
        this.dy = 0
    }
}

class Pipe{
    constructor(y_offset, x_offset){
        this.y_offset = y_offset
        this.x_offset = x_offset
        this.passed = false
    }
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

class FlappyBird{
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


        this.reset()
    }

    reset(){
        this.started = false
        this.score = 0
        this.bird = new Bird((this.bounds.h - this.config.bird_size) / 2)
        this.pipes = []
    }

    draw_bg(){
        this.set_color(this.config.bg)
        this.ctx.fillRect(0, 0, this.bounds.w, this.bounds.h)
    }

    draw_pipes(){
        this.set_color(this.config.pipe_bg)
        for (let pipe of this.pipes){
            this.ctx.fillRect(pipe.x_offset, 0, this.config.pipe_w, pipe.y_offset)
            this.ctx.fillRect(pipe.x_offset, pipe.y_offset + this.config.pipe_space, this.config.pipe_w, this.bounds.h - (pipe.y_offset + this.config.pipe_space))
        }
    }

    draw_ball(){
        this.set_color(this.config.ball)
        this.ctx.beginPath()
        this.ctx.arc(this.config.bird_x, this.bird.y, this.config.bird_size, 0, 2 * Math.PI, false)
        this.ctx.stroke()
        this.ctx.fill()
    }

    draw_score(){
        this.set_color(this.config.fg)
        this.ctx.font = "" + this.config.text_size + "px Arial"
        
        this.ctx.fillText("Score: " + this.score, 10, this.config.text_size)
    }
   
    redraw(){
        this.draw_bg()
        this.draw_pipes()
        this.draw_ball()
        this.draw_score()
    }

    physics(){
        this.move_ball()
        this.move_pipes()
        this.check_bounds()
    }

    set_color(color){
        this.ctx.fillStyle = color
        this.ctx.strokeStyle = color
    }

    check_bounds(){
        for (let pipe of this.pipes){
            if (pipe.passed)continue
            if (this.config.bird_x + this.config.bird_size > pipe.x_offset && pipe.x_offset >= this.config.bird_x - this.config.bird_size && (this.bird.y - this.config.bird_size <= pipe.y_offset || this.bird.y + this.config.bird_size >= pipe.y_offset + this.config.pipe_space)){
                this.stop()
                setTimeout(()=>{
                    this.reset()
                }, 1000)
            }
            if (this.config.bird_x - this.config.bird_size >= pipe.x_offset + this.config.pipe_w){
                pipe.passed = true
                this.score++
            }
            break
        }
        if (this.bird.y - this.config.bird_size < 0 || this.bird.y + this.config.bird_size > this.bounds.h){
            this.stop()
            setTimeout(()=>{
                this.reset()
            }, 1000)
        }
    }

    move_pipes(){
        for (let pipe of this.pipes){
            pipe.x_offset -= this.config.pipe_velocity
        }
    }

    move_ball(){
        this.bird.dy += this.config.gravity
        this.bird.y += this.bird.dy
    }

    move(){
        if (!this.started){
            this.started = true
            this.start()
        }
        this.bird.dy = -this.config.bird_velocity
    }

    spawn_pipe(){
        this.pipes.push(new Pipe(Math.random() * (this.bounds.h - this.config.pipe_space) * 0.8, this.bounds.w))
    }

    start(){
        this.interval = setInterval(()=>{
            flappybird.redraw()
            flappybird.physics()
        },this.config.interval)
        this.pipe_interval = setInterval(()=>{
            flappybird.spawn_pipe()
        }, this.config.pipe_interval)
        this.spawn_pipe()
    }

    stop(){
        clearInterval(this.interval)
        clearInterval(this.pipe_interval)
    }
}

window.onload = ()=>{
    window.flappybird = new FlappyBird("screen", BIRDCONFIG)
    flappybird.redraw()
    websocket = new WebSocket("ws://127.0.0.1:8001")

    websocket.addEventListener("message", (e) => {
        let t = e.data.substring(0, e.data.indexOf("{"))
        let data = e.data.substring(e.data.indexOf("{"))
        data = JSON.parse(data)
        
        if (t === "LocomotiveDirectionCommand")flappybird.move();
        
    })
}

window.onkeydown = (e)=>{
    if (e.key == " ")flappybird.move()
}