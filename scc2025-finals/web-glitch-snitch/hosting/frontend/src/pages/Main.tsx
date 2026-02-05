import { Link } from "react-router-dom";

export default function Main() {
  return (
    <>
      <div className="container py-5">
        <div className="text-center mb-5">
          <div className="glitch-logo">GlitchSnitch</div>
          <p className="lead">
            Snitch the glitch. Claim the fame.
          </p>
        </div>

        <div
          className="glitch-box mx-auto"
          style={{
            maxWidth: "700px",
          }}
        >
          <h3 className="mb-3 text-light">Welcome to the GlitchSnitch Beta Program</h3>
          <p className="text-light">
            GlitchSnitch is the premier <em>“semi-verified”</em> vulnerability
            disclosure platform designed by hackers, for hackers — and tested on
            interns. Upload your zero-days, proof-of-concepts, or whatever
            half-baked exploit you cooked up at 3AM, and we’ll maybe do something
            about it.
          </p>
          <ul className="list-group list-group-flush mb-4">
            <li className="list-group-item bg-transparent text-light">
              ✅ Submit file-based PoCs
            </li>
            <li className="list-group-item bg-transparent text-light">
              🔒 Private beta: authentication required (we're not that
              open-source)
            </li>
            <li className="list-group-item bg-transparent text-light">
              🎁 Earn bounties in crypto, stickers, or solid handshake agreements
            </li>
          </ul>
          <div className="d-flex justify-content-between">
            <Link
              to="/login"
              className="btn btn-cyber btn-lg px-4 py-2 text-uppercase fw-bold"
              style={{
                backgroundColor: "#ff007f",
                color: "#fff",
                border: "2px solid #ff007f",
                transition: "all 0.3s ease",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.backgroundColor = "#ff4da6")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.backgroundColor = "#ff007f")
              }
            >
              Log In
            </Link>
            <Link
              to="/register"
              className="btn btn-cyber btn-lg px-4 py-2 text-uppercase fw-bold"
              style={{
                backgroundColor: "#007fff",
                color: "#fff",
                border: "2px solid #007fff",
                transition: "all 0.3s ease",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.backgroundColor = "#4da6ff")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.backgroundColor = "#007fff")
              }
            >
              Register
            </Link>
          </div>
        </div>

        <footer className="text-center mt-5">
          <small className="text-secondary">
            © 2025 GlitchSnitch LLC — "We may or may not be legally responsible."
          </small>
        </footer>
      </div>
    </>
  );
}
