let balls = [];
let pegs = [];
let slots = [];
let slotCount = 9;
let rows = 7;
let counters = Array(slotCount).fill(0);
let prizes = [100, 50, 20, 10, 5, 10, 20, 50, 100]; // Prize values for each slot
let totalPrize = 0; // Total prize accumulated

function setup() {
    let canvas = createCanvas(800, 600);
    canvas.parent('plinko-container');

    // Create slots at the bottom
    for (let i = 0; i < slotCount; i++) {
        slots.push(new Slot(i * (width / slotCount) + (width / slotCount) / 2, height - 10, width / slotCount, prizes[i]));
    }

    // Create pegs in a pyramid shape
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col <= row; col++) {
            let x = width / 2 - (row * width) / (2 * slotCount) + (col * width) / slotCount;
            let y = (row + 1) * 60;
            pegs.push(new Peg(x, y, 10));
        }
    }
}

function draw() {
    background(15, 23, 25);

    // Draw slots
    for (let slot of slots) {
        slot.show();
    }

    // Draw pegs
    for (let peg of pegs) {
        peg.show();
    }

    // Update and draw balls
    for (let i = balls.length - 1; i >= 0; i--) {
        balls[i].update();
        balls[i].show();

        // Remove ball if it stops moving and increment the slot counter
        if (balls[i].isStopped()) {
            let slotIndex = balls[i].getSlot();
            if (slotIndex !== -1) {
                counters[slotIndex]++;
                totalPrize += slots[slotIndex].prize; // Add prize value to total
            }
            balls.splice(i, 1);
        }
    }

    // Display counters and total prize
    textAlign(CENTER, CENTER);
    textSize(16);
    fill(255);
    for (let i = 0; i < counters.length; i++) {
        text(`Count: ${counters[i]}`, slots[i].x, slots[i].y - 100);
        text(`€${slots[i].prize}`, slots[i].x, slots[i].y - 80); // Display prize values
    }

    textSize(20);
    text(`Total Prize: €${totalPrize}`, width / 2, 50);
}

function mousePressed() {
    balls.push(new Ball(width / 2, 20, 10)); // Always drop the ball in the middle
}

// Ball class
class Ball {
    constructor(x, y, r) {
        this.x = x;
        this.y = y;
        this.r = r;
        this.velY = 0;
        this.velX = 0;
        this.stopped = false;
    }

    update() {
        if (!this.stopped) {
            this.velY += 0.3; // Gravity
            this.y += this.velY;
            this.x += this.velX;

            // Check collision with pegs
            for (let peg of pegs) {
                let d = dist(this.x, this.y, peg.x, peg.y);
                if (d < this.r + peg.r) {
                    this.velX = random(-2, 2);
                    this.velY *= -0.5;
                    break;
                }
            }

            // Stop when it reaches the bottom
            if (this.y > height - 20) {
                this.stopped = true;
            }
        }
    }

    show() {
        fill(0, 179, 179);
        noStroke();
        ellipse(this.x, this.y, this.r * 2);
    }

    isStopped() {
        return this.stopped;
    }

    getSlot() {
        for (let i = 0; i < slots.length; i++) {
            if (this.x > slots[i].x - slots[i].w / 2 && this.x < slots[i].x + slots[i].w / 2) {
                return i;
            }
        }
        return -1;
    }
}

// Peg class
class Peg {
    constructor(x, y, r) {
        this.x = x;
        this.y = y;
        this.r = r;
    }

    show() {
        fill(255);
        noStroke();
        ellipse(this.x, this.y, this.r * 2);
    }
}

// Slot class
class Slot {
    constructor(x, y, w, prize) {
        this.x = x;
        this.y = y;
        this.w = w;
        this.prize = prize; // Assign prize value to the slot
    }

    show() {
        fill(200);
        stroke(255);
        rectMode(CENTER);
        rect(this.x, this.y - 20, this.w, 50);
    }
}
