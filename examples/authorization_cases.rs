//! Shared synthetic command traces; the oracle is read only by the verifier.
use roo::authorization::{Coordinator, Error, Status};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args().nth(1).ok_or("expected one fixture path")?;
    let input = std::fs::read_to_string(path)?;
    let mut scenario = String::new();
    let mut coordinator = Coordinator::new(&[]);
    let mut step = 0;
    for line in input.lines().filter(|line| !line.starts_with('#')) {
        let [name, action, principal, order_id] = line.split('\t').collect::<Vec<_>>()[..] else {
            return Err("expected four tab-separated input columns".into());
        };
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
        println!(
            "{scenario}\t{step}\t{result}\t{}\t{}",
            state("order-1"),
            state("order-2")
        );
    }
    Ok(())
}
