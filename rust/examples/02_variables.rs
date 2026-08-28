// Variables are immutable unless you say otherwise.
// In Python every name can be reassigned; in Rust that is opt-in.

fn main() {
    // Immutable: the value is fixed once bound.
    let min_ratings = 1000;
    println!("min_ratings = {min_ratings}");

    // Mutable: `mut` is you telling the compiler this will change.
    let mut rows_read = 0;
    for _ in 0..3 {
        rows_read += 100_000;
    }
    println!("rows_read  = {rows_read}");

    // Shadowing: a new `let` makes a *new* variable reusing the name.
    // Useful for converting a value without inventing a second name.
    let threshold = "4.5";
    let threshold: f64 = threshold.parse().expect("not a number");
    println!("threshold  = {threshold} (now an f64, not a string)");

    // The type is fixed at compile time even though we never wrote it down.
    let average = 3.7;
    println!("average    = {average} inferred as f64");
}
