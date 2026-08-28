// Borrowing has exactly two forms, and the compiler enforces the difference.
//
//   &T      shared borrow      -- many at once, read only
//   &mut T  exclusive borrow   -- one at a time, may write
//
// One writer or many readers, never both. That single rule is what makes
// the data races in example 06 impossible rather than merely unlikely.

fn average(values: &[u64]) -> f64 {
    values.iter().sum::<u64>() as f64 / values.len() as f64
}

fn highest(values: &[u64]) -> u64 {
    *values.iter().max().unwrap()
}

fn add_rating(values: &mut Vec<u64>, rating: u64) {
    values.push(rating);
}

fn main() {
    let mut ratings = vec![5, 3, 4, 4];

    // Many shared borrows at the same time: fine, nobody is writing.
    let a = &ratings;
    let b = &ratings;
    println!("two readers agree: {:?} == {:?}", a, b);
    println!("average = {:.2}, highest = {}", average(a), highest(b));

    // The exclusive borrow starts here, after the readers are done with.
    add_rating(&mut ratings, 2);
    println!("after write: {ratings:?}");

    // Mutating a collection you are iterating is a real bug in Python and a
    // compile error here. The fix is to decide *first*, then write.
    let to_drop: Vec<usize> = ratings
        .iter()
        .enumerate()
        .filter(|&(_, &r)| r < 3)
        .map(|(i, _)| i)
        .collect();
    println!("plan: remove positions {to_drop:?}");

    for index in to_drop.into_iter().rev() {
        ratings.remove(index);
    }
    println!("after removal: {ratings:?}");
}
