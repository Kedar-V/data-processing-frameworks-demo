// Ownership: every value has exactly one owner.
//
// `let moved = ratings;` hands the list over. `ratings` is no longer usable.
// In Python those two names would point at the same list.

fn main() {
    let ratings = vec![4.5, 3.0, 5.0];
    println!("ratings = {ratings:?}");

    let moved = ratings;
    println!("moved   = {moved:?}");
    // println!("{ratings:?}");  // would not compile: ratings was moved

    // Clone when you really do want a second copy.
    let ratings = vec![4.5, 3.0, 5.0];
    let copy = ratings.clone();
    let moved = ratings;
    println!("moved   = {moved:?}");
    println!("copy    = {copy:?}");
}
