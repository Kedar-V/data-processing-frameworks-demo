// Borrowing comes in exactly two forms, and the difference is the whole game:
//
//   &T      shared borrow      many at once, read only
//   &mut T  exclusive borrow   one at a time, may write
//
// One writer or many readers, never both. That single rule is also what makes
// the data race in example 06 impossible rather than merely unlikely.

fn average(ratings: &Vec<u64>) -> f64 {
    let mut total = 0;
    for i in 0..ratings.len() {
        total += ratings[i];
    }
    total as f64 / ratings.len() as f64
}

fn add_rating(ratings: &mut Vec<u64>, rating: u64) {
    ratings.push(rating);
}

fn main() {
    let mut ratings = vec![5, 3, 4, 4];

    // Two shared borrows at the same time: fine, nobody is writing.
    let first = &ratings;
    let second = &ratings;
    println!("two readers see the same thing: {first:?} and {second:?}");
    println!("average = {:.2}", average(first));

    // The exclusive borrow can start now that the readers are finished.
    add_rating(&mut ratings, 2);
    println!("after write: {ratings:?}");

    // Deleting items while looping over them does not compile. Build the list
    // you want instead, then replace the old one.
    let mut keep = Vec::new();
    for i in 0..ratings.len() {
        if ratings[i] >= 3 {
            keep.push(ratings[i]);
        }
    }
    ratings = keep;
    println!("ratings of 3 or more: {ratings:?}");
}
