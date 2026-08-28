// Concurrency: real cores, no interpreter lock.
//
// The same total is added up with 1, 2, 4, and 8 threads. Each thread gets its
// own slice of the range, so there is nothing shared and nothing to lock --
// and the compiler is what checks that the slices really are separate.

use std::thread;
use std::time::Instant;

const ITERATIONS: u64 = 1_000_000_000;

// Cheap arithmetic, repeated often enough to be worth splitting up.
fn partial_sum(from: u64, to: u64) -> u64 {
    let mut total = 0;
    for i in from..to {
        total += (i * i) % 1_000_003;
    }
    total
}

fn run(threads: u64) -> (u64, f64) {
    let start = Instant::now();
    let chunk = ITERATIONS / threads;

    let total = thread::scope(|scope| {
        // Start every thread ...
        let mut handles = Vec::new();
        for t in 0..threads {
            let from = t * chunk;
            let mut to = from + chunk;
            if t == threads - 1 {
                to = ITERATIONS; // the last thread mops up any remainder
            }
            handles.push(scope.spawn(move || partial_sum(from, to)));
        }

        // ... then wait for every thread and add up what they found.
        let mut total = 0;
        for handle in handles {
            total += handle.join().unwrap();
        }
        total
    });

    (total, start.elapsed().as_secs_f64())
}

fn main() {
    let cores = thread::available_parallelism().unwrap();
    println!("{ITERATIONS} iterations, {cores} cores available\n");
    println!("threads   seconds   speedup   total");

    let mut one_thread = 0.0;
    for threads in [1, 2, 4, 8] {
        let (total, seconds) = run(threads);
        if threads == 1 {
            one_thread = seconds;
        }
        let speedup = one_thread / seconds;
        println!("{threads:>7}   {seconds:>7.3}   {speedup:>6.2}x   {total}");
    }

    println!("\nThe total never changes: the work was split up, not changed.");
}
