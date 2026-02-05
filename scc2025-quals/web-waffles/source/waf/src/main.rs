use hyper::server::conn::AddrStream;
use hyper::service::{make_service_fn, service_fn};
use hyper::{Body, Request, Response, Server, StatusCode};
use std::net::IpAddr;
use std::{convert::Infallible, net::SocketAddr};

async fn handle(client_ip: IpAddr, req: Request<Body>) -> Result<Response<Body>, Infallible> {
    println!("{:?} {} {}", req.version(), req.method(), req.uri());
    if req.uri().to_string().to_lowercase().contains("flag") {
        Ok(Response::new(Body::from("BLOCKED!")))
    } else {
        match hyper_reverse_proxy::call(client_ip, "http://waffles:3000", req).await {
            Ok(response) => Ok(response),
            Err(_error) => Ok(Response::builder()
                .status(StatusCode::INTERNAL_SERVER_ERROR)
                .body(Body::empty())
                .unwrap()),
        }
    }
}

#[tokio::main]
async fn main() {
    let bind_addr = "0.0.0.0:8000";
    let addr: SocketAddr = bind_addr.parse().expect("Could not parse ip:port.");

    let make_svc = make_service_fn(|conn: &AddrStream| {
        let remote_addr = conn.remote_addr().ip();
        async move { Ok::<_, Infallible>(service_fn(move |req| handle(remote_addr, req))) }
    });

    let server = Server::bind(&addr).serve(make_svc);

    println!("Running server on {:?}", addr);

    if let Err(e) = server.await {
        eprintln!("server error: {}", e);
    }
}
