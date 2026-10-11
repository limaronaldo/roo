use std::{env, fs, process::ExitCode};
fn main() -> ExitCode {
    let args: Vec<_> = env::args_os().collect();
    if args.len() != 2 {
        eprintln!("usage: roo-payments <fixture.tsv>");
        return ExitCode::FAILURE;
    }
    let result = fs::read_to_string(&args[1])
        .map_err(|e| e.to_string())
        .and_then(|input| orders_payments_case::fixture::run(&input));
    match result {
        Ok(output) => {
            print!("{output}");
            ExitCode::SUCCESS
        }
        Err(error) => {
            eprintln!("fixture error: {error}");
            ExitCode::FAILURE
        }
    }
}
