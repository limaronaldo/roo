//! Shared synthetic command traces; the oracle is read only by the verifier.
use roo::authorization::{Coordinator, Error, Status};
use std::io::Write;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args().nth(1).ok_or("expected one fixture path")?;
    let input = std::fs::read_to_string(path)?;
    run(&input, &mut std::io::stdout().lock())
}

/// Evaluates a fixture, writing one result row per command as it is processed.
fn run(input: &str, out: &mut impl Write) -> Result<(), Box<dyn std::error::Error>> {
    let mut scenario = String::new();
    let mut coordinator = Coordinator::new(&[]);
    let mut step = 0;
    for line in input.lines().filter(|line| !line.starts_with('#')) {
        let [name, action, principal, order_id] = line.split('\t').collect::<Vec<_>>()[..] else {
            return Err("expected four tab-separated input columns".into());
        };
        if name.is_empty() {
            return Err("invalid scenario: name must not be empty".into());
        }
        if scenario != name {
            scenario = name.to_owned();
            coordinator = Coordinator::new(&["order-1", "order-2"]);
            step = 0;
        }
        step += 1;
        let result = match action {
            "grant" => {
                if coordinator.grant(principal, order_id).expect("available") {
                    "granted"
                } else {
                    "unchanged"
                }
            }
            "revoke" => {
                if coordinator.revoke(principal, order_id).expect("available") {
                    "revoked"
                } else {
                    "unchanged"
                }
            }
            "observe" => {
                if coordinator
                    .observe(principal, order_id)
                    .expect("available")
                    .allowed
                {
                    "allowed"
                } else {
                    "denied"
                }
            }
            "approve" => match coordinator.approve(principal, order_id) {
                Ok(()) => "approved",
                Err(Error::Forbidden) => "forbidden",
                Err(Error::NotFound) => "not_found",
                Err(Error::AlreadyApproved) => "already_approved",
                Err(Error::Unavailable) => return Err("coordinator unavailable".into()),
            },
            _ => return Err("unknown fixture action".into()),
        };
        let state = |id| {
            let snapshot = coordinator
                .snapshot(id)
                .expect("available")
                .expect("seeded");
            let status = match snapshot.status {
                Status::Draft => "draft",
                Status::Approved => "approved",
            };
            format!("{status}/{}", snapshot.approvals)
        };
        writeln!(
            out,
            "{scenario}\t{step}\t{result}\t{}\t{}",
            state("order-1"),
            state("order-2")
        )?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::run;

    fn evaluate(input: &str) -> (Result<(), String>, String) {
        let mut out = Vec::new();
        let result = run(input, &mut out).map_err(|error| error.to_string());
        (result, String::from_utf8(out).expect("utf-8 output"))
    }

    #[test]
    fn valid_fixture_output_is_unchanged() {
        let input = "# comment\nallowed\tgrant\talice\torder-1\n\
                     allowed\tobserve\talice\torder-1\n\
                     allowed\tapprove\talice\torder-1\n\
                     no_grant\tobserve\talice\torder-1\n\
                     no_grant\tapprove\talice\torder-1\n";
        let (result, output) = evaluate(input);
        assert_eq!(result, Ok(()));
        assert_eq!(
            output,
            "allowed\t1\tgranted\tdraft/0\tdraft/0\n\
             allowed\t2\tallowed\tdraft/0\tdraft/0\n\
             allowed\t3\tapproved\tapproved/1\tdraft/0\n\
             no_grant\t1\tdenied\tdraft/0\tdraft/0\n\
             no_grant\t2\tforbidden\tdraft/0\tdraft/0\n"
        );
    }

    #[test]
    fn empty_scenario_is_a_fixture_error_not_a_panic() {
        let (result, output) = evaluate("\tobserve\talice\torder-1\n");
        assert_eq!(
            result,
            Err("invalid scenario: name must not be empty".to_owned())
        );
        assert_eq!(output, "");
    }

    #[test]
    fn empty_scenario_after_a_valid_one_is_also_rejected() {
        let (result, output) =
            evaluate("allowed\tgrant\talice\torder-1\n\tobserve\talice\torder-1\n");
        assert_eq!(
            result,
            Err("invalid scenario: name must not be empty".to_owned())
        );
        assert_eq!(output, "allowed\t1\tgranted\tdraft/0\tdraft/0\n");
    }
}
