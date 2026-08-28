// Variables cannot change unless you say `mut`.
// In Python every name can be reassigned; in Rust that is something you opt in to.

fn main() {
    // Immutable: this value is fixed once it is set.
    let min_ratings = 1000;
    println!("min_ratings = {min_ratings}");

    // Mutable: `mut` is you telling the compiler that this one will change.
    let mut rows_read = 0;
    for _ in 0..3 {
        rows_read += 100_000;
        println!("rows_read   = {rows_read}");
    }

    // Types are decided at compile time, even when you do not write them down.
    let average = 3.7; // a decimal point, so this is a float
    let count = 42; // no decimal point, so this is an integer
    println!("average = {average}, count = {count}");
}
