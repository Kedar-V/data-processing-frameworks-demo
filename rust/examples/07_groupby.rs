// The same task as part 1, written out by hand: group ratings by movie, keep
// the movies with enough ratings, and report the best one.
//
// Nothing is used here beyond the standard library, and the data is built from
// a fixed seed, so the Python version in the notebook produces exactly the same
// answer. Ratings are counted in half-stars (2 to 10, meaning 1.0 to 5.0) so
// every total is a whole number and cannot drift between the two languages.

use std::time::Instant;

const ROWS: usize = 5_000_000;
const MOVIES: usize = 10_000;
const MIN_RATINGS: u64 = 100;
const REPEATS: usize = 3;

// A very simple random number generator, so Python can copy it exactly.
fn generate() -> (Vec<usize>, Vec<u64>) {
    let mut movie_ids = Vec::new();
    let mut half_stars = Vec::new();
    let mut state: u64 = 42;

    for _ in 0..ROWS {
        state = (state * 1_103_515_245 + 12_345) & 0x7FFF_FFFF; // keep 31 bits
        movie_ids.push(state as usize % MOVIES);
        half_stars.push((state >> 8) % 9 + 2);
    }

    (movie_ids, half_stars)
}

// The group-by itself: one running total and one count per movie.
fn group_by_movie(movie_ids: &Vec<usize>, half_stars: &Vec<u64>) -> (Vec<u64>, Vec<u64>) {
    let mut totals = vec![0; MOVIES];
    let mut counts = vec![0; MOVIES];

    for i in 0..movie_ids.len() {
        let movie = movie_ids[i];
        totals[movie] += half_stars[i];
        counts[movie] += 1;
    }

    (totals, counts)
}

fn main() {
    let start = Instant::now();
    let (movie_ids, half_stars) = generate();
    let generate_seconds = start.elapsed().as_secs_f64();

    // Time it a few times and keep the fastest. The slower runs were sharing
    // the machine with something else.
    let mut fastest = f64::MAX;
    for _ in 0..REPEATS {
        let start = Instant::now();
        group_by_movie(&movie_ids, &half_stars);
        let seconds = start.elapsed().as_secs_f64();
        if seconds < fastest {
            fastest = seconds;
        }
    }

    let (totals, counts) = group_by_movie(&movie_ids, &half_stars);

    // Now pick the best movie out of the ones with enough ratings.
    let mut best_movie = 0;
    let mut best_average = 0.0;
    let mut qualifying = 0;
    let mut checksum = 0;

    for movie in 0..MOVIES {
        checksum += totals[movie];
        if counts[movie] < MIN_RATINGS {
            continue;
        }
        qualifying += 1;
        let average = totals[movie] as f64 / counts[movie] as f64 / 2.0;
        if average > best_average {
            best_average = average;
            best_movie = movie;
        }
    }

    // One `key value` pair per line, so the notebook can read these back.
    println!("rows               {ROWS}");
    println!("movies             {MOVIES}");
    println!("qualifying_movies  {qualifying}");
    println!("best_movie         {best_movie}");
    println!("best_average       {best_average:.6}");
    println!("checksum           {checksum}");
    println!("generate_seconds   {generate_seconds:.4}");
    println!("aggregate_seconds  {fastest:.4}");
}
