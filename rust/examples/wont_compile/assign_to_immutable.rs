// EXPECTED TO FAIL: error[E0384]
//
// `let` alone means immutable. Python has no equivalent of this error --
// there, every name can be pointed at something new at any time.
//
// Fix: `let mut limit = 1000;`

fn main() {
    let limit = 1000;
    println!("limit starts at {limit}");

    limit = 2000;
    println!("limit is now {limit}");
}
