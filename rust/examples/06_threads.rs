// Concurrency: real cores, no interpreter lock.
//
// The same CPU-bound total is computed with 1, 2, 4, and 8 threads. Each
// thread owns a disjoint slice of the range, so there is nothing to lock --
// and the compiler is what confirms the slices are disjoint.
//
// Usage: 06_threads [iterations]

use std::thread;
use std::time::Instant;

const DEFAULT_ITERATIONS: u64 = 1_000_000_000;
const MODULUS: u64 = 1_000_003;

/// Deliberately cheap-but-not-free arithmetic the optimizer cannot fold away.
fn partial_sum(from: u64, to: u64) -> u64 {
    let mut total = 0;
    for i in from..to {
        total += (i * i) % MODULUS;
    }
    total
}

fn run(iterations: u64, threads: u64) -> (u64, f64) {
    let start = Instant::now();

    let total = thread::scope(|scope| {
        let chunk = iterations / threads;
        let handles: Vec<_> = (0..threads)
            .map(|t| {
                let from = t * chunk;
                let to = if t == threads - 1 {
                    iterations
                } else {
                    from + chunk
                };
                scope.spawn(move || partial_sum(from, to))
            })
            .collect();

        handles.into_iter().map(|h| h.join().unwrap()).sum::<u64>()
    });

    (total, start.elapsed().as_secs_f64())
}

fn main() {
    let iterations = std::env::args()
        .nth(1)
        .and_then(|a| a.parse().ok())
        .unwrap_or(DEFAULT_ITERATIONS);

    println!(
        "{iterations} iterations, {} cores available\n",
        thread::available_parallelism().map(|n| n.get()).unwrap_or(0)
    );
    println!("{:>7}  {:>9}  {:>8}  {}", "threads", "seconds", "speedup", "total");

    let mut baseline = 0.0;
    for threads in [1, 2, 4, 8] {
        let (total, seconds) = run(iterations, threads);
        if threads == 1 {
            baseline = seconds;
        }
        println!(
            "{threads:>7}  {seconds:>9.3}  {:>7.2}x  {total}",
            baseline / seconds
        );
    }

    println!("\nThe total is identical every time -- the work was split, not changed.");
}
