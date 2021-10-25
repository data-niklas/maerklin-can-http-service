PONGCONFIG = {
    bg: "#ffffff",
    fg: "#000000",
    p1: "#1f5b96",
    p2: "#961f5b",
    ball: "#111111",
    margin: 40,
    player_height: 300,
    player_width: 30,
    ball_r: 12,
    text_size: 40,
    ball_x_vel: 5,
    ball_y_vel: 1,
    interval: 10
}

class Player{
    constructor(name, bounds){
        this.name = name
        this.points = 0
        this.bounds = bounds
    }
}

class Pong{
    constructor(canvas_id, config){
        this.canvas = document.getElementById(canvas_id)
        this.canvas.width = this.canvas.clientWidth
        this.canvas.height = this.canvas.clientHeight
        this.ctx = this.canvas.getContext("2d", {alpha: false})
        this.ctx.shadowBlur = 0
        this.config = config
        this.bounds = {
            x: 0,
            y: 0,
            w: this.canvas.clientWidth,
            h: this.canvas.clientHeight
        }

        this.reset_ball()


        this.p1 = new Player("P1", this.center_y({
            x: this.config.margin,
            y: 0,
            w: this.config.player_width,
            h: this.config.player_height
        }))


        this.p2 = new Player("P2", this.center_y({
            x: this.bounds.w - this.config.margin - this.config.player_width,
            y: 0,
            w: this.config.player_width,
            h: this.config.player_height
        }))
    }


    reset_ball(){

        //Center of the circle
        this.ball = {
            x: this.bounds.w / 2,
            y: this.bounds.h / 2,
            direction: {
                x: 0,
                y: this.config.ball_y_vel
            }
        }

        if (Math.random() >= 0.5){
            this.ball.direction.x = this.config.ball_x_vel
        }
        else{
            this.ball.direction.x = -1 * this.config.ball_x_vel
        }
    }


    center_y(bounds){
        return {
            x: bounds.x,
            y: (this.bounds.h - bounds.h) / 2,
            w: bounds.w,
            h: bounds.h
        }
    }

    draw_bg(){
        this.set_color(this.config.bg)
        this.ctx.fillRect(this.bounds.x, this.bounds.y, this.bounds.w, this.bounds.h)
    }

    draw_players(){
        this.set_color(this.config.p1)
        this.ctx.fillRect(this.p1.bounds.x, this.p1.bounds.y, this.p1.bounds.w, this.p1.bounds.h)

        this.set_color(this.config.p2)
        this.ctx.fillRect(this.p2.bounds.x, this.p2.bounds.y, this.p2.bounds.w, this.p2.bounds.h)
    }

    draw_ball(){
        this.set_color(this.config.ball)
        this.ctx.beginPath()
        this.ctx.arc(this.ball.x, this.ball.y, this.config.ball_r, 0, 2 * Math.PI, false)
        this.ctx.stroke()
        this.ctx.fill()
    }

    draw_score(){
        this.set_color(this.config.fg)
        this.ctx.font = "" + this.config.text_size + "px Arial"
        
        this.ctx.fillText("" + this.p1.points, this.p1.bounds.x, this.config.margin)
        this.ctx.fillText("" + this.p2.points, this.p2.bounds.x, this.config.margin)
    }

    redraw(){
        this.draw_bg()
        this.draw_players()
        this.draw_ball()
        this.draw_score()
    }

    move_ball(){
        this.ball.x += this.ball.direction.x
        this.ball.y += this.ball.direction.y

        if (this.ball.y < 0){
            this.ball.y = 0
            this.ball.direction.y *= -1
        }
        else if (this.ball.y > this.bounds.h){
            this.ball.y = this.bounds.h
            this.ball.direction.y *= -1
        }//x is unnecessary
        else if (this.ball.x < 0){
            this.ball.x = 0
            this.ball.direction.x *= -1
        }
        else if (this.ball.x > this.bounds.w){
            this.ball.x = this.bounds.w
            this.ball.direction.x *= -1
        }
    }

    check_bounds(){
        if (this.ball.x < this.p1.bounds.x + this.p1.bounds.w){
            if (this.height_of(this.p1)){
                this.ball.direction.x *= -1
                this.ball.x = this.p1.bounds.x + this.p1.bounds.w
            }
            else{
                this.p2.points++
                this.reset_ball()
            }
        }
        else if (this.ball.x > this.p2.bounds.x){
            if (this.height_of(this.p2)){
                this.ball.direction.x *= -1
                this.ball.x = this.p2.bounds.x
            }
            else{
                this.p1.points++
                this.reset_ball()
            }
        }
    }

    height_of(p){
        return this.ball.y > p.bounds.y && this.ball.y < p.bounds.y + p.bounds.h
    }

    physics(){
        this.move_ball()
        this.check_bounds()
    }

    set_color(color){
        this.ctx.fillStyle = color
        this.ctx.strokeStyle = color
    }

    movePUp(p, y){
        p.bounds.y = Math.max(0, p.bounds.y - y)
    }

    movePDown(p, y){
        p.bounds.y = Math.min(this.bounds.h, p.bounds.y + y)
    }

    moveP1Up(y){
        this.movePUp(this.p1, y)
    }

    moveP1Down(y){
        this.movePDown(this.p1, y)
    }

    moveP2Up(y){
        this.movePUp(this.p2, y)
    }

    moveP2Down(y){
        this.movePDown(this.p2, y)
    }

    start(){
        this.interval = setInterval(()=>{
            pong.physics()
            pong.redraw()
        },this.config.interval)
    }

    stop(){
        clearInterval(this.interval)
    }
}

window.onload = ()=>{
    window.pong = new Pong("screen", PONGCONFIG)
    pong.start()
}