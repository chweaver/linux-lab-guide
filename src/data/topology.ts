// Single editable source for the guide's network topology.
// Every IP lives here, nowhere else in this repo. Values marked VERIFY are
// best-guess placeholders to correct after the first build (the IoT segment is
// not built yet, and the AD/DC addresses come from the separate ad-lab-guide).
//
// `labs` lists the lab ids that build or harden a node. A node whose labs are all
// complete (per lab-status.json) gets the "done" treatment in the topology. Nodes
// with no labs are established infrastructure (the AD lab, the firewall).

export type NodeType = 'firewall' | 'server' | 'workstation' | 'iot';

export interface TopoSubnet {
  id: string;
  label: string;
  color: string;
}

export interface TopoNode {
  id: string;
  type: NodeType;
  label: string;
  ip: string;
  subnet: string;
  role?: string;
  labs?: string[];
  established?: boolean;
  verify?: boolean;
}

export interface TopoEdge {
  source: string;
  target: string;
}

export const subnets: TopoSubnet[] = [
  { id: 'lan', label: 'LAN · 192.168.100.0/24', color: '#22d3ee' },
  { id: 'lab200', label: 'LAB200 · 192.168.200.0/24', color: '#10b981' },
  { id: 'iot', label: 'IoT VLAN · 192.168.30.0/24 (VERIFY)', color: '#f59e0b' },
];

export const nodes: TopoNode[] = [
  {
    id: 'pfsense',
    type: 'firewall',
    label: 'pfSense CE 2.7.x',
    ip: '192.168.100.1 / .200.1',
    subnet: 'lan',
    role: 'Router + firewall + DHCP',
    established: true,
  },
  {
    id: 'dc01',
    type: 'server',
    label: 'DC01 (corp.lab)',
    ip: '192.168.100.5',
    subnet: 'lan',
    role: 'AD DS / DNS',
    established: true,
  },
  {
    id: 'ws01',
    type: 'workstation',
    label: 'WS01 (Win 11)',
    ip: '192.168.100.20',
    subnet: 'lan',
    role: 'Domain client',
    established: true,
  },
  {
    id: 'ubuntu',
    type: 'server',
    label: 'ubuntu-base',
    ip: '192.168.100.10',
    subnet: 'lan',
    role: 'Samba file server',
    labs: ['ssh', 'samba'],
  },
  {
    id: 'rocky',
    type: 'server',
    label: 'rocky-base',
    ip: '192.168.200.12',
    subnet: 'lab200',
    role: 'BIND9 + rsync target',
    labs: ['bind9', 'rsync'],
  },
  {
    id: 'iot-1',
    type: 'iot',
    label: 'IoT device (VERIFY)',
    ip: '192.168.30.x (VERIFY)',
    subnet: 'iot',
    role: 'Untrusted segment',
    verify: true,
  },
];

export const edges: TopoEdge[] = [
  { source: 'pfsense', target: 'dc01' },
  { source: 'pfsense', target: 'ws01' },
  { source: 'pfsense', target: 'ubuntu' },
  { source: 'pfsense', target: 'rocky' },
  { source: 'pfsense', target: 'iot-1' },
];
