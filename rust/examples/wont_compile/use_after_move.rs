// EXPECTED TO FAIL: error[E0382]
//
// `let second = first;` moves ownership. There is no longer a valid `first`.
//
// In Python the same two lines give you two names for one list, which is
// where aliasing bugs come from: mutate through `second` and `first` changes
// too, silently. Rust makes you choose -- move it, borrow it, or clone it.
//
// Fix: `let second = first.clone();` or read through a borrow.

fn main() {
    let first = vec![1, 2, 3];
    let second = first;

    println!("{first:?} {second:?}");
}
