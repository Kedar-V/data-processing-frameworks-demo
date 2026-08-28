// EXPECTED TO FAIL: error[E0499]
//
// Four threads each want to write to the same counter. That is a data race,
// and it is rejected at compile time -- not detected later, under load, in
// production, one run in a thousand.
//
// The equivalent Python code has the same bug. It usually appears to work,
// because the interpreter lock happens to serialize the increments.
//
// Fix: give each thread its own subtotal and add them up at the end
// (06_threads.rs), or wrap the counter in a Mutex or AtomicU64.

fn main() {
    let mut total = 0u64;

    std::thread::scope(|scope| {
        for _ in 0..4 {
            scope.spawn(|| {
                total += 1;
            });
        }
    });

    println!("{total}");
}
