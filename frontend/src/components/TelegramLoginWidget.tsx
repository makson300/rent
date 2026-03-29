"use client";

import { useEffect, useRef } from "react";

export default function TelegramLoginWidget({
  botName = "voro_test_bot", // Replace with your actual bot username
  buttonSize = "large",
  cornerRadius = 12,
  requestAccess = "write",
  onAuthCallback,
}: {
  botName?: string;
  buttonSize?: "large" | "medium" | "small";
  cornerRadius?: number;
  requestAccess?: string;
  onAuthCallback?: (user: any) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Add the callback function to the global window object
    if (typeof window !== "undefined") {
      (window as any).onTelegramAuth = (user: any) => {
        if (onAuthCallback) {
          onAuthCallback(user);
        } else {
          console.log("Logged in as:", user);
          // In real app, send this user object to your backend to get an auth cookie/token
          // e.g. fetch('/api/auth', { method: 'POST', body: JSON.stringify(user) })
        }
      };
    }

    // Load the script
    if (containerRef.current) {
      // Clear container in case of re-mount
      containerRef.current.innerHTML = "";

      const script = document.createElement("script");
      script.src = "https://telegram.org/js/telegram-widget.js?22";
      script.setAttribute("data-telegram-login", botName);
      script.setAttribute("data-size", buttonSize);
      script.setAttribute("data-radius", cornerRadius.toString());
      script.setAttribute("data-request-access", requestAccess);
      script.setAttribute("data-onauth", "onTelegramAuth(user)");
      script.async = true;

      containerRef.current.appendChild(script);
    }
  }, [botName, buttonSize, cornerRadius, requestAccess, onAuthCallback]);

  return <div ref={containerRef} className="telegram-login-container"></div>;
}
