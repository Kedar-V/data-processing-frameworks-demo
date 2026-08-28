// Where does the memory go?
//
// There is no garbage collector here and no reference counting at runtime.
// The compiler knows where each value stops being used and puts the free
// there. `Drop` lets us print at that exact moment so it is visible.

struct Buffer {
    name: &'static str,
    bytes: Vec<u8>,
}

impl Buffer {
    fn new(name: &'static str, megabytes: usize) -> Buffer {
        println!("  allocate {name}: {megabytes} MB");
        Buffer {
            name,
            bytes: vec![0u8; megabytes * 1024 * 1024],
        }
    }
}

// Runs automatically when the value goes out of scope. You never call it.
impl Drop for Buffer {
    fn drop(&mut self) {
        let megabytes = self.bytes.len() / (1024 * 1024);
        println!("  FREE {}: {} MB released", self.name, megabytes);
    }
}

fn main() {
    println!("enter main");

    {
        println!("enter inner scope");
        let _scratch = Buffer::new("scratch", 64);
        println!("inner scope is about to end");
    } // <- the free happens here, on this closing brace

    println!("back in main: scratch is already gone");

    let _a = Buffer::new("a", 8);
    let _b = Buffer::new("b", 16);

    println!("end of main (watch the order)");
    // Values drop in reverse order of creation: b, then a.
}
