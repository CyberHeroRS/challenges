import { useCallback, useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import { fetchAPI } from "../func";
import useFetch from "./useFetch";

export interface User {
  email: string;
  username: string;
}

export default function useUser() {
  const [user, setUser] = useState<User | null>(null);
  const { data, loading, refetch } = useFetch<User>("/me");

  const history = useHistory();

  useEffect(() => {
    if (data) {
      setUser(data);
    }
  }, [data]);

  const refresh = useCallback(() => {
    refetch();
  }, [refetch]);

  const logout = useCallback(() => {
    fetchAPI("/logout");
    setUser(null);

    // Redirect to login page on logout
    history.push("/login");
  }, []);

  return { user, loading, refresh, logout };
}
