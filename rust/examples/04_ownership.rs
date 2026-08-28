// Ownership: every value has exactly one owner.
//
// This is the rule that replaces the garbage collector. If there is always
// exactly one owner, the compiler always knows where the free belongs.

// The `&` means borrowed: this function may look at the values, not keep them.
fn average(ratings: &Vec<f64>) -> f64 {
    let mut total = 0.0;
    for rating in ratings {
        total += rating;
    }
    total / ratings.len() as f64
}

// No `&`: this function takes ownership, and frees the values when it ends.
fn consume(ratings: Vec<f64>) -> usize {
    ratings.len()
}

fn main() {
    let ratings = vec![4.5, 3.0, 5.0, 2.5];

    // 1. Borrow with `&`. `ratings` still belongs to main afterwards.
    println!("average      = {:.2}", average(&ratings));
    println!("still usable = {ratings:?}");

    // 2. Move. Assigning hands ownership over, it does not copy the data.
    let moved = ratings;
    println!("moved        = {moved:?}");
    // Using `ratings` now would not compile: see wont_compile/use_after_move.rs

    // 3. Clone when you really do want a second copy. The cost is visible.
    let copy = moved.clone();
    println!("clone        = {copy:?}");

    // 4. Give a value away for good.
    println!("consume took {} values", consume(moved));
    // `moved` is gone now, but `copy` was never touched.
    println!("copy survives: {copy:?}");
}
