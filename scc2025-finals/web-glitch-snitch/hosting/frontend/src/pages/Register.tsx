import { useState } from "react";
import { useHistory } from "react-router-dom";
import { fetchAPI } from "../func";
import { BaseAPIResponse } from "../types";
import { useLogin } from "../LoginContext";

export default function Register() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const history = useHistory();

  const { refresh } = useLogin();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    try {
      const response = await fetchAPI<BaseAPIResponse>("/register", {
        email,
        username,
        password,
      });
      if (response.success) {
        refresh();
        history.push("/dashboard");
      }
    } catch (error) {
      alert("Registration failed");
    }
  };

  return (
    <div className="container py-5">
      <div className="text-center mb-5">
        <div className="glitch-logo">GlitchSnitch</div>
        <p className="lead">Snitch the glitch. Claim the fame.</p>
      </div>

      <div
        className="glitch-box mx-auto"
        style={{
          maxWidth: "700px",
        }}
      >
        <h3 className="mb-3">Create Your Account</h3>
        <form onSubmit={handleSubmit}>
          {/* Email */}
          <div className="mb-3">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              type="email"
              className="form-control"
              id="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          {/* Username */}
          <div className="mb-3">
            <label htmlFor="username" className="form-label">
              Username
            </label>
            <input
              type="text"
              className="form-control"
              id="username"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          {/* Password */}
          <div className="mb-3">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              type="password"
              className="form-control"
              id="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="d-grid">
            <button
              type="submit"
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
            </button>
          </div>
        </form>
        <p className="text-center mt-3">
          Already have an account?{" "}
          <a
            href="/login"
            onClick={(e) => {
              e.preventDefault();
              history.push("/login");
            }}
            style={{
              color: "#ff007f",
              textDecoration: "none",
              fontWeight: "bold",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#ff4da6")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "#ff007f")}
          >
            Log In
          </a>
        </p>
      </div>

      <footer className="text-center mt-5">
        <small className="text-secondary">
          © 2025 GlitchSnitch LLC — "We may or may not be legally responsible."
        </small>
      </footer>
    </div>
  );
}
