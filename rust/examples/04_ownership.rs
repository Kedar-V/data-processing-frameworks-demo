// Ownership: every value has exactly one owner.
//
// This is the rule that replaces the garbage collector. If there is always
// one owner, the compiler always knows where the free belongs.

fn summarize(ratings: &Vec<f64>) -> f64 {
    // Borrowed, not owned: this function may look, not keep.
    ratings.iter().sum::<f64>() / ratings.len() as f64
}

fn consume(ratings: Vec<f64>) -> usize {
    // Owned: this function took the value and will free it when it returns.
    ratings.len()
}

fn main() {
    let ratings = vec![4.5, 3.0, 5.0, 2.5];

    // 1. Borrow with `&`. `ratings` still belongs to main afterwards.
    println!("average      = {:.2}", summarize(&ratings));
    println!("still usable = {ratings:?}");

    // 2. Move. Assigning transfers ownership instead of copying the data.
    let moved = ratings;
    println!("moved        = {moved:?}");
    // Using `ratings` here would not compile -- see wont_compile/use_after_move.rs

    // 3. Clone when you genuinely want a second copy. The cost is explicit.
    let copy = moved.clone();
    println!("clone        = {copy:?}");

    // 4. Give a value away for good.
    println!("consume took {} values", consume(moved));
    // `moved` is gone now; `copy` is untouched.
    println!("copy survives: {copy:?}");
}
