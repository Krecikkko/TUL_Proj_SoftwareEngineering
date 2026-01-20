import { useState } from "react";
import { AlertsPage } from "./components/AlertsPage";
import { MeasurementsPage } from "./components/MeasurementsPage"; // Twoja strona
import { ForecastsPage } from "./components/ForecastsPage";       // Twoja strona
import { LoginScreen } from "./components/login";
import { DashboardTestPage } from "./components/DashboardPage";

function App() {
  const [activeTab, setActiveTab] = useState("alerts");

  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return !!localStorage.getItem('access_token');
  });

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('userRole');
    setIsLoggedIn(false);
  };

  const btnStyle = (tabName) => ({
    padding: "10px 20px",
    cursor: "pointer",
    fontWeight: "bold",
    borderBottom: activeTab === tabName ? "3px solid #646cff" : "3px solid transparent",
    background: "transparent",
    border: "none", 
    borderBottom: activeTab === tabName ? "3px solid #646cff" : "none",
    color: activeTab === tabName ? "#646cff" : "inherit"
  });

  // --- JEŚLI NIEZALOGOWANY -> POKAŻ LOGIN SCREEN ---
  if (!isLoggedIn) {
    return <LoginScreen onLoginSuccess={() => setIsLoggedIn(true)} />;
  }

  return (
    <div>
      {/* --- NAWIGACJA --- */}
      <nav style={{ 
          display: "flex", 
          gap: "20px", 
          borderBottom: "1px solid #ccc", 
          marginBottom: "20px",
          padding: "0 20px"
      }}>
        <button style={btnStyle("alerts")} onClick={() => setActiveTab("alerts")}>
          Alerts
        </button>
        <button style={btnStyle("measurements")} onClick={() => setActiveTab("measurements")}>
          Measuements
        </button>
        <button style={btnStyle("forecasts")} onClick={() => setActiveTab("forecasts")}>
          Forecats
        </button>
             <button style={btnStyle("dashboard")} onClick={() => setActiveTab("dashboard")}>
          Dashboard
        </button>
      </nav>

      {/* --- WIDOKI --- */}
      <div className="content">
        {activeTab === "alerts" && <AlertsPage />}
        {activeTab === "measurements" && <MeasurementsPage />}
        {activeTab === "forecasts" && <ForecastsPage />}
        { activeTab === "dashboard" && <DashboardTestPage/>}
      </div>
    </div>
  );
}

export default App;