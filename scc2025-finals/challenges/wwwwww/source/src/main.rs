use std::{
    io::{stdin, BufRead},
    process::exit,
};

mod arena;

static mut PLAYER: (u8, u8) = arena::PLAYER_START;
static mut GRAVITY: i8 = 1;

fn main() {
    loop {
        for line in stdin().lock().lines() {
            let line = line.unwrap();
            for c in line.chars() {
                if c == 'q' {
                    return;
                }
                if !command(c) {
                    return;
                }
            }
        }
    }
}

#[inline(always)]
fn command(c: char) -> bool {
    match c {
        'w' => unsafe {
            GRAVITY = -GRAVITY;
            // step()
            true
        },
        'a' => unsafe {
            if 0 < PLAYER.0 && PLAYER.0 < u8::MAX {
                PLAYER.0 -= 1;
            }
            step()
        },
        's' => step(),
        'd' => unsafe {
            if 0 < PLAYER.0 && PLAYER.0 < u8::MAX {
                PLAYER.0 += 1;
            }
            step()
        },
        _ => true,
    }
}

#[inline(always)]
fn step() -> bool {
    let pos;
    unsafe {
        PLAYER.1 = PLAYER.1.wrapping_add_signed(GRAVITY) % 32;
        // Capture
        pos = PLAYER;
    }
    win();
    check_pos!(pos)
}

fn win() {
    unsafe {
        if PLAYER != arena::BABA_IS_WIN {
            return;
        }
    }

    println!("{}", std::fs::read_to_string("flag.txt").unwrap());
    exit(0);
}
