import React, { useState } from "react";
import "./App.css";
import ChatWindow from "./components/ChatWindow";
import InsightsDashboard from "./components/InsightsDashboard";

function App() {
  const [activeTab, setActiveTab] = useState("assistant");

  return (
    <div className="App">
      <div className="header">
        <div className="header-title">PartSelect Parts Assistant</div>
        <div className="header-subtitle">
          Find refrigerator and dishwasher parts, check compatibility, troubleshoot issues, and get installation help.
        </div>
      </div>

      <div className="top-nav">
        <button
          className={activeTab === "assistant" ? "nav-button active" : "nav-button"}
          onClick={() => setActiveTab("assistant")}
        >
          Assistant
        </button>
        <button
          className={activeTab === "insights" ? "nav-button active" : "nav-button"}
          onClick={() => setActiveTab("insights")}
        >
          Insights Dashboard
        </button>
      </div>

      {activeTab === "assistant" ? <ChatWindow /> : <InsightsDashboard />}
    </div>
  );
}

export default App;