// Where does the memory go?
//
// Rust has no garbage collector, and it does not count references while the
// program runs. The compiler works out where each value stops being used and
// writes the `free` there, before the program ever starts.
//
// `Drop` lets a type print something at the moment it is freed, so you can
// watch it happen.

struct Buffer {
    data: Vec<u8>,
}

fn make_buffer(megabytes: usize) -> Buffer {
    println!("  allocate {megabytes} MB");
    Buffer {
        data: vec![0; megabytes * 1024 * 1024],
    }
}

// Rust calls this for you. You never call it yourself.
impl Drop for Buffer {
    fn drop(&mut self) {
        let megabytes = self.data.len() / 1024 / 1024;
        println!("  FREE {megabytes} MB");
    }
}

fn main() {
    println!("enter main");

    {
        println!("  enter inner scope");
        let _scratch = make_buffer(64);
        println!("  inner scope is about to end");
    } // <- the 64 MB is freed here, on this closing brace

    println!("back in main: that memory is already gone");

    let _small = make_buffer(8);
    let _large = make_buffer(16);

    println!("end of main (watch the order)");
    // _large and _small are freed here, in reverse order of creation.
}
