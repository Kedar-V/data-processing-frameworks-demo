// EXPECTED TO FAIL: error[E0502]
//
// `for r in &ratings` holds a shared borrow for the whole loop, so nothing
// may write to `ratings` until the loop ends.
//
// The same code in Python runs happily and gives a wrong answer, because the
// iterator is walking a list that is changing underneath it.
//
// Fix: collect the changes first, apply them after -- see 05_borrow_rules.rs.

fn main() {
    let mut ratings = vec![5, 3, 4];

    for r in &ratings {
        if *r == 3 {
            ratings.push(0);
        }
    }

    println!("{ratings:?}");
}
