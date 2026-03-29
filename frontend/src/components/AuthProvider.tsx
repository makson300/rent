"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export interface User {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
  token?: string;
  user_type?: "private" | "company";
  has_license?: boolean;
}

interface AuthContextType {
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check local storage for user object on app load
    const storedUser = localStorage.getItem("skyrent_user");
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error("Failed to parse user session", e);
      }
    }
  }, []);

  const login = async (userData: User) => {
    // Send Telegram data to FastAPI backend to verify hash and get real profile + JWT token
    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/telegram", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        // data should contain { token: "...", user: { ... } }
        const fullUser = { ...userData, ...data.user, token: data.access_token };
        setUser(fullUser);
        localStorage.setItem("skyrent_user", JSON.stringify(fullUser));
      } else {
        console.error("Auth failed on backend");
        // Fallback for development without backend
        setUser(userData);
        localStorage.setItem("skyrent_user", JSON.stringify(userData));
      }
    } catch (e) {
      console.error("Backend unreachable", e);
      // Fallback for UI development
      setUser(userData);
      localStorage.setItem("skyrent_user", JSON.stringify(userData));
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("skyrent_user");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
