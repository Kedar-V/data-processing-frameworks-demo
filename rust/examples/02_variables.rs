// Variables cannot change unless you say `mut`.
// In Python every name can be reassigned; in Rust that is something you opt in to.

fn main() {
    // Immutable: this value is fixed once it is set.
    let min_ratings = 1000;
    println!("keep movies with at least {min_ratings} ratings");

    // Mutable: `mut` is you telling the compiler this one will change.
    let mut rows_read = 0;
    for _ in 0..3 {
        rows_read += 100_000;
        println!("rows_read = {rows_read}");
    }
}
