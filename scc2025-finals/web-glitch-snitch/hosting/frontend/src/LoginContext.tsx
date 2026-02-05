import React, { createContext, useContext } from "react";
import useUser, { User } from "./hooks/useUser";

interface LoginContextProps {
  user: User | null;
  loading: boolean;
  refresh: () => void;
  logout: () => void;
}

const LoginContext = createContext<LoginContextProps | undefined>(undefined);

export const LoginProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { user, loading, refresh, logout } = useUser();

  return (
    <LoginContext.Provider value={{ user, loading, refresh, logout }}>
      {children}
    </LoginContext.Provider>
  );
};

export const useLogin = () => {
  const context = useContext(LoginContext);
  if (context === undefined) {
    throw new Error("useLogin must be used within a LoginProvider");
  }
  return context;
};
