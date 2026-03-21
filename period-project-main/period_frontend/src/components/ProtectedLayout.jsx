// src/components/ProtectedLayout.jsx
import React from "react";

export default function ProtectedLayout({ children }) {
  return (
    <div className="relative min-h-screen pb-24">
      {/* Page content */}
      {children}
    </div>
  );
}