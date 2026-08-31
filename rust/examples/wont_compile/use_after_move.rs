// EXPECTED TO FAIL: error[E0382]
//
// `let moved = ratings;` moves ownership. There is no longer a valid `ratings`.
//
// In Python the same two lines give you two names for one list.
//
// Fix: `let moved = ratings.clone();` or only use `moved` afterwards.

fn main() {
    let ratings = vec![4.5, 3.0, 5.0];
    let moved = ratings;

    println!("{ratings:?} {moved:?}");
}
