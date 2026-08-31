// The compiler checks this file before anything runs.
//
//   rustc --edition 2024 01_hello.rs -o hello
//   ./hello

fn main() {
    let engine = "Rust";
    println!("Hello from {engine}.");
    println!("This file was checked by the compiler before it ran.");
}
