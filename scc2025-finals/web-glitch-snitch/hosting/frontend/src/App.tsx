import 'bootstrap/dist/css/bootstrap.min.css';

import { LoginProvider } from "./LoginContext";
import MainNavigation from "./MainNavigation";

export default function App() {
  return (
    <LoginProvider>
      <MainNavigation />
    </LoginProvider>
  );
}
