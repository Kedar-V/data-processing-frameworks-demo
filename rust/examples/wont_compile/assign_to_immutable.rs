// EXPECTED TO FAIL: error[E0384]
//
// `let` alone means immutable. Python has no equivalent of this error --
// there, every name can be pointed at something new at any time.
//
// Fix: `let mut min_ratings = 1000;`

fn main() {
    let min_ratings = 1000;
    println!("keep movies with at least {min_ratings} ratings");

    min_ratings = 2000;
    println!("keep movies with at least {min_ratings} ratings");
}
