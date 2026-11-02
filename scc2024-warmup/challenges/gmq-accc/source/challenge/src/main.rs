use rand::Rng;
use std::io::{self, Write};

fn generate_equation() -> (i32, i32) {
    let mut rng = rand::thread_rng();
    let x: i32 = rng.gen_range(200000..200000000);
    let y: i32 = rng.gen_range(200000..200000000);
    (x, y)
}

fn main() {
    const NUM_ROUNDS: usize = 500;

    println!(
        "You need to solve {} rounds under 30 seconds to initialize communication with aliens.",
        NUM_ROUNDS
    );
    println!("Good luck agent!!");

    for round in 1..=NUM_ROUNDS {
        let (x, y) = generate_equation();
        let correct_answer = x + y;

        print!("Round {}: {} + {} = ", round, x, y);
        io::stdout().flush().unwrap();

        let mut user_input = String::new();
        io::stdin()
            .read_line(&mut user_input)
            .expect("Failed to read line");

        match user_input.trim().parse::<i32>() {
            Ok(user_answer) if user_answer == correct_answer => {
                println!("Correct!");
            }
            _ => {
                println!("Incorrect. Correct answer is: {}", correct_answer);
                std::process::exit(1);
            }
        }
    }

    println!("Congratulations! All answers are correct.");
    println!(
        "Here is your flag agent, {}",
        std::env::var("FLAG").expect("FLAG is not set")
    );
}
