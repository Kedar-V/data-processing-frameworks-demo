// Rust has a step Python does not: the compiler runs before the program does.
//
//   rustc --edition 2024 01_hello.rs -o hello   # compile once
//   ./hello                                     # run as often as you like

fn main() {
    let engine = "Rust";
    let year = 2026;

    println!("Hello from {engine}, {year}.");
    println!("This file was checked by the compiler before it ran.");
}
