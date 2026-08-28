// Where does the memory go?
//
// Rust has no garbage collector, and it does not count references while the
// program runs. The compiler works out where each value stops being used and
// writes the `free` there, before the program ever starts.
//
// `Drop` lets a type print something at the moment it is freed, so you can
// watch it happen.

struct Buffer {
    name: String,
    data: Vec<u8>,
}

fn make_buffer(name: &str, megabytes: usize) -> Buffer {
    println!("  allocate {name}: {megabytes} MB");
    Buffer {
        name: name.to_string(),
        data: vec![0; megabytes * 1024 * 1024],
    }
}

// Rust calls this for you. You never call it yourself.
impl Drop for Buffer {
    fn drop(&mut self) {
        let megabytes = self.data.len() / 1024 / 1024;
        println!("  FREE {}: {} MB released", self.name, megabytes);
    }
}

fn main() {
    println!("enter main");

    {
        println!("  enter inner scope");
        let _scratch = make_buffer("scratch", 64);
        println!("  inner scope is about to end");
    } // <- scratch is freed here, on this closing brace

    println!("back in main: scratch is already gone");

    let _a = make_buffer("a", 8);
    let _b = make_buffer("b", 16);

    println!("end of main (watch the order)");
    // b and a are freed here, in reverse order of creation.
}
