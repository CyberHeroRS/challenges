import React, { useState } from "react";
import { useHistory } from "react-router-dom";
import { fetchAPI } from "../func";
import { BaseAPIResponse } from "../types";
import { useLogin } from "../LoginContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const history = useHistory();

  const { refresh } = useLogin();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    try {
      const response = await fetchAPI<BaseAPIResponse>("/login", {
        email,
        password,
      });
      if (response.success) {
        refresh();
        history.push("/dashboard");
      }
    } catch (error) {
      alert("Login failed");
      return;
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
          maxWidth: "500px",
        }}
      >
        <h3 className="mb-3 text-center">Log In</h3>
        <form onSubmit={handleSubmit}>
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
            </button>
          </div>
          <p className="text-center mt-3">
          Don't have an account?{" "}
            <a
              href="/register"
              className="text-decoration-none"
              style={{ color: "#007fff" }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#4da6ff")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "#007fff")}
              onClick={(e) => {
                e.preventDefault();
                history.push("/register");
              }}
            >
              Register
            </a>
          </p>
        </form>
      </div>

      <footer className="text-center mt-5">
        <small className="text-secondary">
          © 2025 GlitchSnitch LLC — "We may or may not be legally responsible."
        </small>
      </footer>
    </div>
  );
}
