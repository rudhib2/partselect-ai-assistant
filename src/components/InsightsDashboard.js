import React, { useEffect, useState } from "react";
import { getInsightsSummary } from "../api/api";
import "./InsightsDashboard.css";

function MetricCard({ label, value }) {
  return (
    <div className="metric-card">
      <div className="metric-value">{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  );
}

function RankedList({ title, items, emptyText, renderItem }) {
  return (
    <div className="dashboard-panel">
      <div className="panel-title">{title}</div>
      {items && items.length > 0 ? (
        <div className="ranked-list">
          {items.map((item, index) => (
            <div className="ranked-row" key={index}>
              {renderItem(item, index)}
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">{emptyText}</div>
      )}
    </div>
  );
}

function KeyValuePanel({ title, data, emptyText }) {
  const entries = Object.entries(data || {});

  return (
    <div className="dashboard-panel">
      <div className="panel-title">{title}</div>
      {entries.length > 0 ? (
        <div className="ranked-list">
          {entries.map(([key, value]) => (
            <div className="ranked-row" key={key}>
              <span className="row-primary">{key}</span>
              <span className="row-badge">{value}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">{emptyText}</div>
      )}
    </div>
  );
}

function InsightsDashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await getInsightsSummary();
      setSummary(data);
    } catch (err) {
      setError("Could not load insights summary.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading) {
    return <div className="dashboard-shell">Loading insights...</div>;
  }

  if (error) {
    return (
      <div className="dashboard-shell">
        <div className="dashboard-error">{error}</div>
        <button className="refresh-button" onClick={fetchSummary}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard-shell">
        <div className="dashboard-header-row">
            <div>
                <div className="dashboard-title">Insights Dashboard</div>
                <div className="dashboard-subtitle">
                Business analytics from assistant conversations
                </div>
                <div className="dashboard-context">
                These insights highlight customer demand trends, common appliance issues, and potential product gaps in the catalog.
                </div>
            </div>
            <button className="refresh-button" onClick={fetchSummary}>
                Refresh
            </button>
        </div>

      <div className="metrics-grid">
        <MetricCard label="Total Queries" value={summary?.total_queries ?? 0} />
        <MetricCard
          label="Avg Response Time"
          value={`${summary?.average_response_time_ms ?? 0} ms`}
        />
        <MetricCard
          label="Unique Intents"
          value={Object.keys(summary?.intent_distribution || {}).length}
        />
        <MetricCard
          label="Unavailable Requests"
          value={(summary?.top_unavailable_queries || []).reduce(
            (acc, item) => acc + item.count,
            0
          )}
        />
      </div>

      <div className="dashboard-grid">
        <KeyValuePanel
          title="Intent Distribution"
          data={summary?.intent_distribution}
          emptyText="No intent data yet."
        />

        <KeyValuePanel
          title="Appliance Distribution"
          data={summary?.appliance_distribution}
          emptyText="No appliance data yet."
        />

        <RankedList
          title="Top Requested Parts"
          items={summary?.top_parts}
          emptyText="No part data yet."
          renderItem={(item, index) => (
            <>
              <div className="row-left">
                <span className="row-rank">{index + 1}</span>
                <span className="row-primary">{item.part_number}</span>
              </div>
              <span className="row-badge">{item.count}</span>
            </>
          )}
        />

        <RankedList
          title="Top Symptoms"
          items={summary?.top_symptoms}
          emptyText="No symptom data yet."
          renderItem={(item, index) => (
            <>
              <div className="row-left">
                <span className="row-rank">{index + 1}</span>
                <span className="row-primary">{item.symptom}</span>
              </div>
              <span className="row-badge">{item.count}</span>
            </>
          )}
        />

        <RankedList
          title="Top Unavailable Queries"
          items={summary?.top_unavailable_queries}
          emptyText="No unavailable queries yet."
          renderItem={(item, index) => (
            <>
              <div className="row-left">
                <span className="row-rank">{index + 1}</span>
                <span className="row-primary">{item.query}</span>
              </div>
              <span className="row-badge">{item.count}</span>
            </>
          )}
        />
      </div>
    </div>
  );
}

export default InsightsDashboard;