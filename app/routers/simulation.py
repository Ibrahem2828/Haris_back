from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.log_generator import LogGenerator

router = APIRouter(prefix="/simulate", tags=["Simulation"])


def _response(events, message: str):
    return {"created_events": len(events), "message": message}


@router.post("/normal")
def simulate_normal(db: Session = Depends(get_db)):
    return _response(LogGenerator(db).generate_normal(), "Normal traffic generated.")


@router.post("/ssh-bruteforce")
def simulate_ssh_bruteforce(db: Session = Depends(get_db)):
    return _response(LogGenerator(db).generate_ssh_bruteforce(), "SSH brute force events generated.")


@router.post("/port-scan")
def simulate_port_scan(db: Session = Depends(get_db)):
    return _response(LogGenerator(db).generate_port_scan(), "Port scan events generated.")


@router.post("/icmp-flood")
def simulate_icmp_flood(db: Session = Depends(get_db)):
    return _response(LogGenerator(db).generate_icmp_flood(), "ICMP flood events generated.")


@router.post("/vlan-violation")
def simulate_vlan_violation(db: Session = Depends(get_db)):
    return _response(LogGenerator(db).generate_vlan_violation(), "VLAN violation event generated.")


@router.post("/arp-spoofing")
def simulate_arp_spoofing(db: Session = Depends(get_db)):
    return _response(LogGenerator(db).generate_arp_spoofing(), "ARP spoofing indicators generated.")


@router.post("/all")
def simulate_all(db: Session = Depends(get_db)):
    return _response(LogGenerator(db).generate_all(), "All educational scenarios generated.")
