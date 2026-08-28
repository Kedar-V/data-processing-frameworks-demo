// The same task as part 1, written by hand: group ratings by movie, keep the
// movies with enough ratings, report the best one.
//
// Nothing is imported beyond the standard library, and the data is generated
// from a fixed seed so the Python version in the notebook produces byte-for-byte
// the same answer. Ratings are counted in half-stars (2..=10) so the totals are
// integers and cannot drift between languages.
//
// The aggregation is timed three times and the median is reported, because a
// single run of something this fast is mostly noise.
//
// Usage: 07_groupby [rows] [movies]

use std::time::Instant;

const DEFAULT_ROWS: usize = 5_000_000;
const DEFAULT_MOVIES: usize = 10_000;
const MIN_RATINGS: u64 = 100;
const REPEATS: usize = 3;

struct Answer {
    best_movie: usize,
    best_average: f64,
    qualifying: u64,
    checksum: u64,
}

/// A linear congruential generator, so Python can reproduce the same stream.
fn generate(rows: usize, movies: usize) -> (Vec<u32>, Vec<u8>) {
    let mut movie_ids = Vec::with_capacity(rows);
    let mut half_stars = Vec::with_capacity(rows);
    let mut state: u64 = 42;
    for _ in 0..rows {
        state = (state * 1_103_515_245 + 12_345) & 0x7FFF_FFFF;
        movie_ids.push((state % movies as u64) as u32);
        half_stars.push(((state >> 8) % 9 + 2) as u8);
    }
    (movie_ids, half_stars)
}

/// The group-by itself: sum and count per movie, then pick the best.
fn aggregate(movie_ids: &[u32], half_stars: &[u8], movies: usize) -> Answer {
    let mut totals = vec![0u64; movies];
    let mut counts = vec![0u64; movies];
    for i in 0..movie_ids.len() {
        let movie = movie_ids[i] as usize;
        totals[movie] += half_stars[i] as u64;
        counts[movie] += 1;
    }

    let mut answer = Answer {
        best_movie: 0,
        best_average: 0.0,
        qualifying: 0,
        checksum: totals.iter().sum(),
    };
    for movie in 0..movies {
        if counts[movie] < MIN_RATINGS {
            continue;
        }
        answer.qualifying += 1;
        let average = totals[movie] as f64 / counts[movie] as f64 / 2.0;
        if average > answer.best_average {
            answer.best_average = average;
            answer.best_movie = movie;
        }
    }
    answer
}

fn median(mut seconds: Vec<f64>) -> f64 {
    seconds.sort_by(f64::total_cmp);
    seconds[seconds.len() / 2]
}

fn main() {
    let mut args = std::env::args().skip(1);
    let rows: usize = args
        .next()
        .and_then(|a| a.parse().ok())
        .unwrap_or(DEFAULT_ROWS);
    let movies: usize = args
        .next()
        .and_then(|a| a.parse().ok())
        .unwrap_or(DEFAULT_MOVIES);

    let start = Instant::now();
    let (movie_ids, half_stars) = generate(rows, movies);
    let generate_seconds = start.elapsed().as_secs_f64();

    let mut timings = Vec::with_capacity(REPEATS);
    let mut answer = aggregate(&movie_ids, &half_stars, movies);
    for _ in 0..REPEATS {
        let start = Instant::now();
        answer = aggregate(&movie_ids, &half_stars, movies);
        timings.push(start.elapsed().as_secs_f64());
    }

    // One `key value` pair per line, so the notebook can read these back.
    println!("rows               {rows}");
    println!("movies             {movies}");
    println!("qualifying_movies  {}", answer.qualifying);
    println!("best_movie         {}", answer.best_movie);
    println!("best_average       {:.6}", answer.best_average);
    println!("checksum           {}", answer.checksum);
    println!("generate_seconds   {generate_seconds:.4}");
    println!("aggregate_seconds  {:.4}", median(timings));
}
