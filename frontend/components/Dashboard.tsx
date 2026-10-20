"use client";

import { usePathname, useRouter } from "next/navigation";

import { useEffect, useMemo, useState } from "react";
import {
  Activity, AlertOctagon, AlertTriangle, ArrowDownRight, ArrowUpRight, Bell,
  CheckCircle2, ChevronDown, CircleHelp, Clock3, Cloud, Command, FileSearch,
  Filter, Gauge, LayoutDashboard, LifeBuoy, LockKeyhole, Menu, MoreHorizontal,
  Network, RefreshCw, Search, Settings2, Shield, ShieldCheck, ShieldAlert,
  Siren, X, Zap
} from "lucide-react";
import { DEMO_DATA_NOTE, fetchAlerts, startInvestigation, type SecurityAlert, type Severity } from "@/lib/api";

type NavItem = "Overview" | "Security alerts" | "Investigations" | "Evidence log" | "Settings";

const navItems: { label: NavItem; icon: typeof LayoutDashboard }[] = [
  { label: "Overview", icon: LayoutDashboard },
  { label: "Security alerts", icon: ShieldAlert },
  { label: "Investigations", icon: FileSearch },
  { label: "Evidence log", icon: Network },
  { label: "Settings", icon: Settings2 }
];

const severityOrder: Record<Severity, number> = { Critical: 0, High: 1, Medium: 2, Low: 3 };

function Badge({ children, kind = "neutral" }: { children: React.ReactNode; kind?: string }) {
  return <span className={`badge badge-${kind.toLowerCase().replaceAll(" ", "-")}`}>{children}</span>;
}

function severityKind(severity: Severity) {
  return severity === "Critical" ? "critical" : severity === "High" ? "high" : severity === "Medium" ? "medium" : "low";
}

function statusKind(status: string) {
  return status === "Investigating" ? "blue" : status === "Needs review" ? "review" : status === "Resolved" ? "green" : "neutral";
}

function shortTool(tool: string) {
  const map: Record<string, string> = {
    inspect_iam: "Inspect IAM",
    inspect_ec2: "Inspect EC2",
    review_cloudtrail: "Review CloudTrail",
    human_review: "Human review"
  };
  return map[tool] || tool.replaceAll("_", " ");
}

export default function Home() {
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [mode, setMode] = useState<"demo">("demo");
  const [backendStatus, setBackendStatus] = useState<"online" | "offline" | "not-configured">("not-configured");
  const [warning, setWarning] = useState("");
  const [selectedId, setSelectedId] = useState("CS-1048");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All severities");
  const pathname = usePathname();
    const router = useRouter();

    const routeToNav: Record<string, NavItem> = {
    "/": "Overview",
    "/alerts": "Security alerts",
    "/investigations": "Investigations",
    "/evidence": "Evidence log",
    "/settings": "Settings",
    };

    const activeNav = routeToNav[pathname] ?? "Overview";

    function navigateTo(label: NavItem) {
    const routes: Record<NavItem, string> = {
        "Overview": "/",
        "Security alerts": "/alerts",
        "Investigations": "/investigations",
        "Evidence log": "/evidence",
        "Settings": "/settings",
    };

    router.push(routes[label]);
    setSidebarOpen(false);
    }
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  async function loadData() {
    setLoading(true);
    const result = await fetchAlerts();
    setAlerts(result.alerts);
    setMode(result.mode);
    setBackendStatus(result.backendStatus);
    setWarning(result.warning || "");
    setSelectedId((current) => result.alerts.some((alert) => alert.id === current) ? current : result.alerts[0]?.id || "");
    setLoading(false);
  }

  useEffect(() => { void loadData(); }, []);

  const visibleAlerts = useMemo(() => alerts
    .filter((alert) => filter === "All severities" || alert.severity === filter)
    .filter((alert) => `${alert.id} ${alert.title} ${alert.resource} ${alert.source}`.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]), [alerts, filter, search]);

  const selectedAlert = alerts.find((alert) => alert.id === selectedId) || visibleAlerts[0];
  const criticalCount = alerts.filter((alert) => alert.severity === "Critical").length;
  const activeCount = alerts.filter((alert) => alert.status === "Investigating").length;
  const reviewCount = alerts.filter((alert) => alert.status === "Needs review").length;
  const averageConfidence = alerts.length ? Math.round(alerts.reduce((sum, item) => sum + item.confidence, 0) / alerts.length * 100) : 0;

  async function handleStartInvestigation() {
    if (!selectedAlert) return;
    setStarting(true);
    const result = await startInvestigation(selectedAlert);
    setNotice(result.message);
    setStarting(false);
    window.setTimeout(() => setNotice(""), 5000);
  }

  return (
    <main className="app-shell">
      {sidebarOpen && <button className="mobile-scrim" aria-label="Close menu" onClick={() => setSidebarOpen(false)} />}
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><ShieldCheck size={22} strokeWidth={2.2} /></div>
          <div><div className="brand-name">CloudSentinel<span>AI</span></div><div className="brand-caption">CLOUD DEFENSE CENTER</div></div>
          <button className="icon-button sidebar-close" aria-label="Close menu" onClick={() => setSidebarOpen(false)}><X size={18} /></button>
        </div>

        <div className="workspace-label">WORKSPACE</div>
        <button className="workspace-switch"><span className="workspace-icon"><Cloud size={17} /></span><span className="workspace-copy"><strong>Production Cloud</strong><small>AWS environment</small></span><ChevronDown size={16} /></button>

        <nav className="main-nav" aria-label="Main navigation">
          <div className="nav-label">SECURITY</div>
          {navItems.map(({ label, icon: Icon }) => (
            <button key={label} className={`nav-item ${activeNav === label ? "nav-active" : ""}`} onClick={() => navigateTo(label)}>
              <Icon size={18} /><span>{label}</span>{label === "Security alerts" && <span className="nav-count">{alerts.length}</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card"><div className="help-icon"><LifeBuoy size={17} /></div><strong>Need a hand?</strong><p>Review the demo notes and integration checklist.</p><button onClick={() => setNotice("Demo mode uses sample data. Confirm API routes with the backend teammate.")}>View quick guide <ArrowUpRight size={14} /></button></div>
          <div className="sidebar-user"><div className="avatar">CS</div><div className="user-copy"><strong>Security analyst</strong><small>Project workspace</small></div><MoreHorizontal size={18} /></div>
        </div>
      </aside>

      <section className="main-area">
        <header className="topbar">
          <div className="topbar-left"><button className="icon-button menu-button" aria-label="Open menu" onClick={() => setSidebarOpen(true)}><Menu size={21} /></button><div className="breadcrumb">Workspace <span>/</span> <strong>{activeNav}</strong></div></div>
          <div className="topbar-actions"><div className={`environment-pill ${mode === "api" ? "connected" : ""}`}><span className="status-dot" />{backendStatus === "online" ? "Backend online · sample data" : backendStatus === "offline" ? "Backend offline · demo" : "Demo environment"}</div><button className="icon-button notification-button" aria-label="Notifications" onClick={() => setNotice("You are all caught up on demo notifications.")}><Bell size={19} /><i /></button><button className="profile-button" onClick={() => setShowProfile(!showProfile)}><span className="avatar small-avatar">CS</span><ChevronDown size={15} /></button>{showProfile && <div className="profile-popover"><strong>Security analyst</strong><span>CloudSentinel demo</span><button onClick={() => { setShowProfile(false); setNotice(DEMO_DATA_NOTE); }}>About this environment</button></div>}</div>
        </header>

        <div className="content">
          <div className="page-heading">
            <div><div className="eyebrow"><span className="eyebrow-line" /> AI-POWERED CLOUD SECURITY</div><h1>{activeNav === "Overview" ? "Security overview" : activeNav}</h1><p className="page-subtitle">Investigate suspicious activity. Understand the evidence. Respond with confidence.</p></div>
            <div className="heading-actions"><button className="button button-secondary" onClick={() => void loadData()} disabled={loading}><RefreshCw size={16} className={loading ? "spin" : ""} /> Refresh</button><button className="button button-primary" onClick={() => void handleStartInvestigation()} disabled={!selectedAlert || starting}><Zap size={16} />{starting ? "Starting..." : "Run investigation"}</button></div>
          </div>

          {warning && <div className="warning-banner"><AlertTriangle size={17} /><span>{warning}</span><button onClick={() => setWarning("")} aria-label="Dismiss warning"><X size={16} /></button></div>}
          {notice && <div className="notice-banner"><CircleHelp size={17} /><span>{notice}</span><button onClick={() => setNotice("")} aria-label="Dismiss message"><X size={16} /></button></div>}

          <div className="demo-note"><span className="demo-note-icon"><LockKeyhole size={14} /></span><span><strong>Safe demo mode</strong> — {DEMO_DATA_NOTE}</span><span className="note-divider" /><span className="updated-label"><span className="status-dot" /> {backendStatus === "online" ? "API reachable · sample events" : "Sample events loaded"}</span></div>

          {activeNav === "Overview" && <>
          <section className="metric-grid" aria-label="Security metrics">
            <MetricCard title="Total alerts" value={String(alerts.length).padStart(2, "0")} foot="Events in this view" icon={<Shield size={18} />} tone="blue" trend="Live overview" />
            <MetricCard title="Critical severity" value={String(criticalCount).padStart(2, "0")} foot="Requires priority review" icon={<AlertOctagon size={18} />} tone="red" trend="High priority" />
            <MetricCard title="Investigations active" value={String(activeCount).padStart(2, "0")} foot="Currently being reviewed" icon={<Activity size={18} />} tone="purple" trend="In progress" />
            <MetricCard title="Needs human review" value={String(reviewCount).padStart(2, "0")} foot="Evidence needs validation" icon={<CircleHelp size={18} />} tone="amber" trend="Safety fallback" />
          </section>

          <section className="main-grid">
            <div className="panel alerts-panel">
              <div className="panel-header"><div><div className="panel-title-row"><h2>Security alerts</h2><span className="count-chip">{visibleAlerts.length}</span></div><p>Prioritized events that may need investigation</p></div><button className="icon-button" aria-label="More alert options" onClick={() => setNotice("Alerts are sorted by severity. Use search and severity filters to narrow the list.")}><MoreHorizontal size={20} /></button></div>
              <div className="alert-toolbar"><div className="search-field"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search alerts or resources..." aria-label="Search alerts" /><kbd>⌘ K</kbd></div><div className="filter-select"><Filter size={15} /><select value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filter by severity"><option>All severities</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select><ChevronDown size={14} /></div></div>
              <div className="alert-list">
                {loading ? <div className="empty-state"><RefreshCw className="spin" size={20} /> Loading alerts...</div> : visibleAlerts.length === 0 ? <div className="empty-state"><Search size={22} /><strong>No matching alerts</strong><span>Try a different search or severity filter.</span></div> : visibleAlerts.map((alert) => (
                  <button key={alert.id} className={`alert-row ${selectedAlert?.id === alert.id ? "alert-row-selected" : ""}`} onClick={() => setSelectedId(alert.id)}>
                    <span className={`alert-symbol symbol-${severityKind(alert.severity)}`}>{alert.severity === "Critical" ? <Siren size={17} /> : alert.severity === "High" ? <AlertTriangle size={17} /> : alert.severity === "Medium" ? <AlertOctagon size={17} /> : <Shield size={17} />}</span>
                    <span className="alert-main"><span className="alert-title-line"><strong>{alert.title}</strong><span className="alert-id">{alert.id}</span></span><span className="alert-resource">{alert.resource}</span><span className="alert-meta"><span>{alert.source}</span><span className="meta-dot" />{alert.time}</span></span>
                    <span className="alert-side"><Badge kind={severityKind(alert.severity)}>{alert.severity}</Badge><span className="alert-status"><span className={`mini-dot status-${statusKind(alert.status)}`} />{alert.status}</span></span>
                  </button>
                ))}
              </div>
              <div className="panel-footer"><span>Showing {visibleAlerts.length} of {alerts.length} alerts</span><button onClick={() => { navigateTo("Security alerts"); setNotice("Security alerts view selected."); }}>View all alerts <ArrowUpRight size={14} /></button></div>
            </div>

            <div className="panel investigation-panel">
              <div className="panel-header"><div><div className="panel-title-row"><h2>Investigation insight</h2><span className="live-indicator"><span />{backendStatus === "online" ? "API + DEMO" : "DEMO"}</span></div><p>Selected alert analysis</p></div><button className="icon-button" aria-label="Investigation details" onClick={() => setNotice("This panel shows the selected alert's current investigation summary.")}><MoreHorizontal size={20} /></button></div>
              {!selectedAlert ? <div className="empty-state">Select an alert to inspect details.</div> : <div className="insight-content">
                <div className="selected-alert-heading"><div className={`large-alert-icon symbol-${severityKind(selectedAlert.severity)}`}><ShieldAlert size={21} /></div><div><div className="selected-id">{selectedAlert.id} <span className="meta-dot" /> {selectedAlert.source}</div><h3>{selectedAlert.title}</h3></div></div>
                <p className="selected-description">{selectedAlert.description}</p>
                <div className="insight-tags"><Badge kind={severityKind(selectedAlert.severity)}>{selectedAlert.severity} severity</Badge><Badge kind={statusKind(selectedAlert.status)}>{selectedAlert.status}</Badge></div>
                <div className="section-divider" />
                <div className="section-heading"><span className="section-icon"><Command size={15} /></span><h4>Decider 2B tool selection</h4><span className="info-label">AI DECISION</span></div>
                <div className="tool-choice"><div className="tool-choice-icon"><FileSearch size={18} /></div><div className="tool-choice-copy"><strong>{shortTool(selectedAlert.selectedTool)}</strong><span>{selectedAlert.selectedTool}</span></div><Badge kind="blue">Selected</Badge></div>
                <div className="confidence-block"><div className="confidence-label"><span>Decision confidence</span><strong>{Math.round(selectedAlert.confidence * 100)}<small>%</small></strong></div><div className="confidence-track"><span style={{ width: `${Math.max(0, Math.min(100, selectedAlert.confidence * 100))}%` }} /></div><div className="confidence-foot"><span>Model-reported demo value</span><span>{selectedAlert.confidence < 0.6 ? "Human review recommended" : "Decision recorded"}</span></div></div>
                <div className="section-divider" />
                <div className="section-heading"><span className="section-icon"><Network size={15} /></span><h4>Evidence collected</h4><span className="evidence-count">{selectedAlert.evidence.length} items</span></div>
                <ul className="evidence-list">{selectedAlert.evidence.map((item, i) => <li key={item}><span className="evidence-check"><CheckCircle2 size={14} /></span><span>{item}</span></li>)}</ul>
                <div className="ai-explanation"><div className="ai-heading"><span className="ai-spark"><Zap size={14} /></span><strong>AI analysis</strong><span className="ai-model">BEDROCK-STYLE SUMMARY</span></div><p>{selectedAlert.explanation}</p><div className="recommendation"><div><ArrowDownRight size={15} /><strong>Suggested next step</strong></div><p>{selectedAlert.recommendation}</p></div></div>
                <button className="button button-primary full-button" onClick={() => void handleStartInvestigation()} disabled={starting}><Zap size={16} />{starting ? "Starting investigation..." : "Run investigation for this alert"}</button>
                <p className="human-review-note"><LockKeyhole size={13} /> Read-only workflow. Human approval is required before any remediation.</p>
              </div>}
            </div>
          </section>

          <section className="bottom-grid">
            <div className="panel workflow-panel"><div className="panel-header"><div><h2>Investigation workflow</h2><p>How CloudSentinel moves from alert to insight</p></div><Badge kind="neutral">4 stages</Badge></div><div className="workflow-steps">
              <WorkflowStep number="01" icon={<Bell size={17} />} title="Alert received" detail="Suspicious cloud event" state="complete" />
              <div className="workflow-connector" />
              <WorkflowStep number="02" icon={<Command size={17} />} title="Tool selected" detail="Decider 2B decision" state="complete" />
              <div className="workflow-connector" />
              <WorkflowStep number="03" icon={<FileSearch size={17} />} title="Evidence reviewed" detail="IAM · EC2 · CloudTrail" state="current" />
              <div className="workflow-connector" />
              <WorkflowStep number="04" icon={<ShieldCheck size={17} />} title="Human validation" detail="Review before action" state="pending" />
            </div></div>
            <div className="panel confidence-panel"><div className="panel-header"><div><h2>Decision quality</h2><p>Average confidence across visible demo alerts</p></div><span className="quality-icon"><Gauge size={18} /></span></div><div className="quality-score"><strong>{averageConfidence}<small>%</small></strong><Badge kind="blue"><ArrowUpRight size={12} /> Sample metric</Badge></div><div className="quality-track"><span style={{ width: `${averageConfidence}%` }} /></div><div className="quality-foot"><span><span className="mini-dot status-blue" /> Tool decision confidence</span><span>{alerts.length} sample events</span></div><div className="quality-disclaimer"><CircleHelp size={14} /> Values are illustrative sample data, not a measured model benchmark.</div></div>
          </section>

          <footer className="page-footer"><div><span className="footer-brand"><ShieldCheck size={15} /> CloudSentinel AI</span><span>Prototype dashboard for AI-assisted cloud security investigations.</span></div><div className="footer-right"><span><span className="status-dot" /> {backendStatus === "online" ? "API reachable · sample data" : "Sample data mode"}</span><span>Built for responsible investigation</span></div></footer>
          </>}

          {activeNav === "Security alerts" && <section className="panel page-panel">
            <div className="panel-header"><div><h2>All security alerts</h2><p>Search, filter, and select an alert to inspect its details.</p></div><Badge kind="blue">{visibleAlerts.length} alerts</Badge></div>
            <div className="alert-toolbar"><div className="search-field"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search alerts or resources..." aria-label="Search alerts" /></div><div className="filter-select"><Filter size={15} /><select value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filter by severity"><option>All severities</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select><ChevronDown size={14} /></div></div>
            <div className="alert-list">{visibleAlerts.map((alert) => <button key={alert.id} className={`alert-row ${selectedAlert?.id === alert.id ? "alert-row-selected" : ""}`} onClick={() => { setSelectedId(alert.id); setNotice(`Selected ${alert.id}. Return to Overview to view the full insight panel.`); }}><span className={`alert-symbol symbol-${severityKind(alert.severity)}`}><ShieldAlert size={17} /></span><span className="alert-main"><span className="alert-title-line"><strong>{alert.title}</strong><span className="alert-id">{alert.id}</span></span><span className="alert-resource">{alert.resource}</span><span className="alert-meta"><span>{alert.source}</span><span className="meta-dot" />{alert.time}</span></span><span className="alert-side"><Badge kind={severityKind(alert.severity)}>{alert.severity}</Badge><span className="alert-status">{alert.status}</span></span></button>)}{visibleAlerts.length === 0 && <div className="empty-state">No alerts match your search.</div>}</div>
          </section>}

          {activeNav === "Investigations" && <section className="panel page-panel">
            <div className="panel-header"><div><h2>Investigation queue</h2><p>Review the current state and AI-assisted summary for each alert.</p></div><Badge kind="blue">{alerts.filter(a => a.status !== "Resolved").length} open</Badge></div>
            <div className="investigation-cards">{alerts.map(alert => <article className="investigation-card" key={alert.id}><div className="investigation-card-top"><span className="selected-id">{alert.id} · {alert.source}</span><Badge kind={statusKind(alert.status)}>{alert.status}</Badge></div><h3>{alert.title}</h3><p>{alert.description}</p><div className="investigation-card-meta"><span><strong>Tool:</strong> {shortTool(alert.selectedTool)}</span><span><strong>Confidence:</strong> {Math.round(alert.confidence * 100)}%</span></div><div className="investigation-card-actions"><button className="button button-secondary" onClick={() => { setSelectedId(alert.id); navigateTo("Overview"); }}>View insight</button><button className="button button-primary" disabled={starting} onClick={() => { setSelectedId(alert.id); void startInvestigation(alert).then(r => setNotice(r.message)); }}>Run investigation</button></div></article>)}</div>
          </section>}

          {activeNav === "Evidence log" && <section className="panel page-panel">
            <div className="panel-header"><div><h2>Evidence log</h2><p>Evidence items attached to the sample investigation alerts.</p></div><Badge kind="neutral">{alerts.reduce((sum, a) => sum + a.evidence.length, 0)} items</Badge></div>
            <div className="evidence-log-list">{alerts.flatMap(alert => alert.evidence.map((item, index) => ({ alert, item, index }))).map(({ alert, item, index }) => <div className="evidence-log-row" key={`${alert.id}-${index}`}><span className="evidence-check"><CheckCircle2 size={16} /></span><div className="evidence-log-copy"><strong>{item}</strong><span>{alert.id} · {alert.title}</span></div><Badge kind={severityKind(alert.severity)}>{alert.severity}</Badge></div>)}</div>
            <div className="evidence-log-note"><LockKeyhole size={15} /> Demo evidence is illustrative sample data. Live evidence will appear after backend integration.</div>
          </section>}

          {activeNav === "Settings" && <section className="settings-grid">
            <div className="panel settings-panel"><div className="panel-header"><div><h2>Workspace settings</h2><p>Manage local dashboard preferences.</p></div><Settings2 size={19} /></div><div className="settings-row"><div><strong>Workspace name</strong><span>Label shown in the sidebar.</span></div><input className="settings-input" defaultValue="Production Cloud" aria-label="Workspace name" onChange={(e) => { const el = document.querySelector('.workspace-copy strong'); if (el) el.textContent = e.target.value || 'Production Cloud'; }} /></div><div className="settings-row"><div><strong>Environment mode</strong><span>Current data source for this dashboard.</span></div><Badge kind={backendStatus === "online" ? "green" : "blue"}>{backendStatus === "online" ? "Backend online · sample data" : backendStatus === "offline" ? "Backend offline · demo" : "Demo mode"}</Badge></div><div className="settings-row"><div><strong>Default alert severity filter</strong><span>Change the alert list filter.</span></div><select className="settings-input" value={filter} onChange={(e) => setFilter(e.target.value)}><option>All severities</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select></div><div className="settings-row"><div><strong>Reset search</strong><span>Clear the current alert search.</span></div><button className="button button-secondary" onClick={() => { setSearch(''); setFilter('All severities'); setNotice('Search and severity filters have been reset.'); }}>Reset filters</button></div></div>
            <div className="panel settings-panel"><div className="panel-header"><div><h2>Safety & integration</h2><p>Current prototype status.</p></div><ShieldCheck size={19} /></div><div className="settings-info"><span className="settings-info-icon"><LockKeyhole size={17} /></span><div><strong>Read-only by design</strong><p>No automatic remediation is performed by this frontend. Human approval should be required before any real cloud changes.</p></div></div><div className="settings-info"><span className="settings-info-icon"><Cloud size={17} /></span><div><strong>Backend integration</strong><p>{backendStatus === "online" ? "The Flask health endpoint is reachable, but alert cards remain sample data; the backend does not currently expose an alerts-list endpoint." : "The dashboard uses sample alerts. Investigation requests use the Flask /api/investigate endpoint when the API URL is configured."}</p></div></div><button className="button button-secondary" onClick={() => setNotice(DEMO_DATA_NOTE)}>View demo data notice</button></div>
          </section>}

        </div>
      </section>
    </main>
  );
}

function MetricCard({ title, value, foot, icon, tone, trend }: { title: string; value: string; foot: string; icon: React.ReactNode; tone: string; trend: string }) {
  return <div className="metric-card"><div className="metric-top"><span className={`metric-icon metric-${tone}`}>{icon}</span><span className="metric-trend">{trend}</span></div><div className="metric-title">{title}</div><div className="metric-value">{value}</div><div className="metric-foot">{foot}</div></div>;
}

function WorkflowStep({ number, icon, title, detail, state }: { number: string; icon: React.ReactNode; title: string; detail: string; state: string }) {
  return <div className={`workflow-step step-${state}`}><div className="workflow-icon">{icon}</div><div className="workflow-copy"><span className="workflow-number">{number}</span><strong>{title}</strong><span>{detail}</span></div><span className="workflow-state">{state === "complete" ? <CheckCircle2 size={16} /> : state === "current" ? <Activity size={16} /> : <Clock3 size={16} />}</span></div>;
}
