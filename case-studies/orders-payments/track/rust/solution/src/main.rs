#![forbid(unsafe_code)]
mod learner;
#[path = "../../shared.rs"]
mod shared;

fn main() {
    std::process::exit(shared::run(learner::decide));
}
