use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};
use std::env;
use std::io::{self, Write};
use std::panic;

const MAX_NAME_LEN: usize = 50;
const SEED: u64 = 0x1337; // haxxor seed

fn custom_panic_handler(_info: &panic::PanicHookInfo) {
    if let Ok(flag) = env::var("FLAG") {
        println!("A panic occurred! FLAG: {}", flag);
    } else {
        println!("A panic occurred! FLAG environment variable not found.");
    }
}

fn main() {
    let mut rng = StdRng::seed_from_u64(SEED);
    panic::set_hook(Box::new(custom_panic_handler));

    println!("╔═══════════════════════════════════════════════════════╗");
    println!("║       WELCOME TO THE SECURE PASSWORD GENERATOR        ║");
    println!("║    Each password is tailored for a specific user      ║");
    println!("╚═══════════════════════════════════════════════════════╝");
    println!();
    println!();
    print!("Enter your username: ");
    io::stdout().flush().unwrap();

    let mut user_input = String::new();
    if io::stdin().read_line(&mut user_input).is_err() {
        println!("Error reading username");
        return;
    }

    let user_name = user_input.trim();
    if user_name.chars().count() > MAX_NAME_LEN {
        println!("Username is too long");
        return;
    }

    let mut password = [0u8; MAX_NAME_LEN * 2 + 69]; // Just to be safe
    for i in 0..user_name.len() {
        password[i] =
            ((rng.random::<u8>().wrapping_add(user_name.as_bytes()[i])) % (127 - 32) + 32) as u8;
    }

    print!(
        "Your secure password is: {}",
        String::from_utf8(password.to_vec()).unwrap()
    );
}
