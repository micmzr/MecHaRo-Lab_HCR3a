// ROS 2 HCR Driver socket forwarding server

use std::io::{Read, Write};
use std::net::{Ipv4Addr, SocketAddrV4};
use std::env;
use std::net::{TcpListener, TcpStream};
use std::thread;

struct Adress {
    name: String,
    ip: Ipv4Addr,
    port: u16,
}

impl Adress {
    fn open(&self) -> TcpListener {
        match TcpListener::bind(SocketAddrV4::new(self.ip, self.port)) {
            Ok(listener) => listener,
            Err(e) => panic!("{} could not bind to address: {}", self.name, e),
        }
    }

    fn new(name: String, ip: Ipv4Addr, port: u16) -> Adress {
        Adress { name, ip, port }
    }
}

fn main() {
    println!("HCR Controller <--> ROS2 driver socket forwarding server");

    let args: Vec<String> = env::args().collect();

    let _ = args
        .iter()
        .enumerate()
        .find(|(_, arg)| *arg == "--help" || *arg == "-h")
        .map_or((), |_| {
            println!("Usage: hcr_ros2_socket_forwarder [--help|-h]");
            println!("Forwards data between HCR controller and ROS2 driver over TCP sockets.");
            println!("-hcr_ip <IP_ADDRESS>    Set HCR controller IP address (default: 127.0.0.1)");
            println!("-hcr_port <PORT>        Set HCR controller port (default: 6668)");
            println!("-ros2_ip <IP_ADDRESS>   Set ROS2 driver IP address (default: 172.31.112.1)");
            println!("-ros2_port <PORT>       Set ROS2 driver port (default: 6669)");
            std::process::exit(0);
        });

    let mut hcr_ip = Ipv4Addr::new(127, 0, 0, 1);
    let mut hcr_port = 6668;
    let mut ros2_ip = Ipv4Addr::new(172, 31, 112, 1);
    let mut ros2_port = 6669;

    let _ = args
        .iter()
        .enumerate()
        .find(|(_, arg)| *arg == "-hcr_ip")
        .map_or((), |(i, _)| {
            if let Some(ip_str) = args.get(i + 1) {
                if let Ok(ip) = ip_str.parse() {
                    hcr_ip = ip;
                } else {
                    eprintln!("Invalid HCR IP address: {}", ip_str);
                    std::process::exit(1);
                }
            }
        });

    let _ = args
        .iter()
        .enumerate()
        .find(|(_, arg)| *arg == "-hcr_port")
        .map_or((), |(i, _)| {
            if let Some(port_str) = args.get(i + 1) {
                if let Ok(port) = port_str.parse() {
                    hcr_port = port;
                } else {
                    eprintln!("Invalid HCR port: {}", port_str);
                    std::process::exit(1);
                }
            }
        });

    let _ = args
        .iter()
        .enumerate()
        .find(|(_, arg)| *arg == "-ros2_ip")
        .map_or((), |(i, _)| {
            if let Some(ip_str) = args.get(i + 1) {
                if let Ok(ip) = ip_str.parse() {
                    ros2_ip = ip;
                } else {
                    eprintln!("Invalid ROS2 IP address: {}", ip_str);
                    std::process::exit(1);
                }
            }
        });

    let _ = args
        .iter()
        .enumerate()
        .find(|(_, arg)| *arg == "-ros2_port")
        .map_or((), |(i, _)| {
            if let Some(port_str) = args.get(i + 1) {
                if let Ok(port) = port_str.parse() {
                    ros2_port = port;
                } else {
                    eprintln!("Invalid ROS2 port: {}", port_str);
                    std::process::exit(1);
                }
            }
        });

    let hcr = Adress::new(String::from("HCR"), hcr_ip, hcr_port);
    let ros2 = Adress::new(String::from("ROS2"), ros2_ip, ros2_port);

    let data_ros2 = [0_u8; 80];
    let data_hcr = [0_u8; 80];

    let hcr_listener = hcr.open();
    let ros2_listener = ros2.open();

    println!("HCR {:?}", hcr_listener);
    println!("ROS2 {:?}", ros2_listener);

    let hcr_stream = get_stream(&hcr_listener, &hcr.name);
    let ros2_stream = get_stream(&ros2_listener, &ros2.name);

    ros2_stream
        .set_read_timeout(Some(std::time::Duration::new(1, 0)))
        .expect("set_read_timeout call failed for ros2_stream");
    ros2_stream
        .set_write_timeout(Some(std::time::Duration::new(1, 0)))
        .expect("set_write_timeout call failed for ros2_stream");
    hcr_stream
        .set_read_timeout(Some(std::time::Duration::new(1, 0)))
        .expect("set_read_timeout call failed for hcr_stream");
    hcr_stream
        .set_write_timeout(Some(std::time::Duration::new(1, 0)))
        .expect("set_write_timeout call failed for hcr_stream");
    hcr_stream
        .set_nodelay(true)
        .expect("set_nodelay call failed for hcr_stream");
    ros2_stream
        .set_nodelay(true)
        .expect("set_nodelay call failed for ros2_stream");

    let ros2_stream_clone = ros2_stream
        .try_clone()
        .expect("Failed to clone ROS2 stream");
    let hcr_stream_clone = hcr_stream.try_clone().expect("Failed to clone HCR stream");

    thread::spawn(move || {
        handle_connection(ros2_stream, hcr_stream_clone, data_ros2);
    });

    handle_connection(hcr_stream, ros2_stream_clone, data_hcr);
}

fn get_stream(listener: &TcpListener, name: &str) -> TcpStream {
    match listener.accept() {
        Ok((stream, addr)) => {
            println!("New {} connection: {}", name, addr);
            stream
        }
        Err(e) => panic!("couldn't get client: {:?}", e),
    }
}

fn handle_connection(mut stream: TcpStream, mut stream_out: TcpStream, mut data: [u8; 80]) {
    while match stream.read(&mut data) {
        Ok(size) => {
            // println!("{} received {}", stream.peer_addr().unwrap(), size);

            let mut error = false;

            match stream_out.write(&data[0..size]) {
                Ok(_) => {
                    // println!("{} sent {}", stream_out.peer_addr().unwrap(), size);
                }
                Err(e) => {
                    println!(
                        "Failed to send data to {}: {}",
                        stream_out.peer_addr().unwrap(),
                        e
                    );
                    error = true;
                }
            }

            !error
        }
        Err(_) => {
            println!(
                "An error occurred, terminating connection with {}",
                stream.peer_addr().unwrap()
            );
            false
        }
    } {}
    // println!("Terminating stream thread.");
}
