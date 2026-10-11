#![forbid(unsafe_code)]
use roo_postgres_case::{
    database::{Database, scope},
    fixture::{self, HEADER},
};
fn run() -> Result<String, String> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    // Parse all input and configuration before opening a database connection.
    match args
        .iter()
        .map(String::as_str)
        .collect::<Vec<_>>()
        .as_slice()
    {
        ["fixtures", path] => {
            let input =
                std::fs::read_to_string(path).map_err(|_| "could not read fixture".to_owned())?;
            let scenarios = fixture::parse(&input)?;
            let prefix =
                std::env::var("ROO_RUN_ID").map_err(|_| "ROO_RUN_ID is required".to_owned())?;
            scope(&prefix).map_err(|e| e.to_string())?;
            let scopes: Vec<_> = scenarios
                .iter()
                .map(|(name, _)| format!("{prefix}_{name}"))
                .collect();
            let db = Database::from_env().map_err(|e| e.to_string())?;
            db.reserve_fresh(&scopes).map_err(|e| e.to_string())?;
            let mut output = format!("{HEADER}\n");
            for ((label, actions), s) in scenarios.into_iter().zip(scopes) {
                let mut last = "-".to_owned();
                for action in actions {
                    last = db.step(&s, &action).map_err(|e| e.to_string())?.to_string();
                }
                output.push_str(&db.snapshot(&s, &label, &last).map_err(|e| e.to_string())?);
            }
            Ok(output)
        }
        [command, s] if *command == "init" || *command == "snapshot" => {
            scope(s).map_err(|e| e.to_string())?;
            let db = Database::from_env().map_err(|e| e.to_string())?;
            if *command == "init" {
                db.init(s, false).map_err(|e| e.to_string())?;
            }
            Ok(format!(
                "{HEADER}\n{}",
                db.snapshot(s, s, "-").map_err(|e| e.to_string())?
            ))
        }
        ["step", s, text] => {
            scope(s).map_err(|e| e.to_string())?;
            let action = fixture::parse_action(text)?;
            let db = Database::from_env().map_err(|e| e.to_string())?;
            let last = db.step(s, &action).map_err(|e| e.to_string())?;
            Ok(format!(
                "{HEADER}\n{}",
                db.snapshot(s, s, &last.to_string())
                    .map_err(|e| e.to_string())?
            ))
        }
        _ => Err(
            "usage: roo-postgres fixtures PATH | init SCOPE | step SCOPE ACTION | snapshot SCOPE"
                .into(),
        ),
    }
}
fn main() {
    match run() {
        Ok(output) => print!("{output}"),
        Err(error) => {
            eprintln!(
                "roo-postgres: {}",
                error.chars().take(240).collect::<String>()
            );
            std::process::exit(1);
        }
    }
}
