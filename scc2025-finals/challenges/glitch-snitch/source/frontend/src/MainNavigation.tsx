import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Main from "./pages/Main";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { useLogin } from "./LoginContext";

export default function MainNavigation() {
  const { user, loading, logout } = useLogin();

  if (loading) {
    return <div>Loading...</div>;
  }
  return (
    <Router>
      <div>
        <nav
          className="navbar navbar-expand-lg glitch-box shadow-sm py-3"
          style={{
            backgroundColor: "#000",
            color: "#fff",
          }}
        >
          <Link
            className="glitch-logo"
            to="/"
            style={{
              textDecoration: "none",
              marginLeft: "20px",
              marginRight: "20px",
            }}
          >
            GlitchSnitch
          </Link>
          <button
            className="navbar-toggler"
            type="button"
            data-toggle="collapse"
            data-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
            style={{
              borderColor: "#fff",
            }}
          >
            <span
              className="navbar-toggler-icon"
              style={{
          backgroundColor: "#fff",
              }}
            ></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ml-auto">
              <li className="nav-item">
          <Link
            className="nav-link"
            to="/"
            style={{
              color: "#fff",
            }}
          >
            Main
          </Link>
              </li>
              {user && (
          <>
            <li className="nav-item">
              <Link
                className="nav-link"
                to="/dashboard"
                style={{
            color: "#fff",
                }}
              >
                Dashboard
              </Link>
            </li>
            <li className="nav-item">
              <a
                className="nav-link"
                href="#"
                onClick={logout}
                style={{
            color: "#ff4da6",
                }}
              >
                Logout
              </a>
            </li>
          </>
              )}
              {!user && (
          <>
            <li className="nav-item">
              <Link
                className="nav-link"
                to="/login"
                style={{
            color: "#fff",
                }}
              >
                Login
              </Link>
            </li>
            <li className="nav-item">
              <Link
                className="nav-link"
                to="/register"
                style={{
            color: "#fff",
                }}
              >
                Register
              </Link>
            </li>
          </>
              )}
            </ul>
          </div>
        </nav>

        <Switch>
          <Route exact path="/">
            <Main />
          </Route>
          {user && (
            <Route path="/dashboard">
              <Dashboard />
            </Route>
          )}
          <Route path="/login">
            <Login />
          </Route>
          <Route path="/register">
            <Register />
          </Route>

          <Route path="*">
            <div>Page not found</div>
          </Route>
        </Switch>
      </div>
    </Router>
  );
}
