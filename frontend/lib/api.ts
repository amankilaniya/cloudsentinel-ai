export type Severity = "Critical" | "High" | "Medium" | "Low";
export type InvestigationStatus = "Investigating" | "Needs review" | "Resolved" | "New";

export type SecurityAlert = {
  id: string;
  title: string;
  resource: string;
  source: "IAM" | "EC2" | "CloudTrail";
  severity: Severity;
  status: InvestigationStatus;
  time: string;
  description: string;
  selectedTool: string;
  confidence: number;
  evidence: string[];
  explanation: string;
  recommendation: string;
};

const DEMO_ALERTS: SecurityAlert[] = [
  {
    id: "CS-1048",
    title: "Unusual IAM permission change",
    resource: "role/production-deployer",
    source: "IAM",
    severity: "Critical",
    status: "Investigating",
    time: "2 min ago",
    description: "A privileged policy was attached outside the usual deployment window.",
    selectedTool: "inspect_iam",
    confidence: 0.94,
    evidence: [
      "A new policy attachment was observed on a production role.",
      "The event occurred outside the usual deployment window.",
      "The activity should be correlated with the actor and recent CloudTrail events."
    ],
    explanation: "The permission change may increase the role's privileges. The available sample evidence is suspicious, but it does not by itself prove malicious activity.",
    recommendation: "Verify the change with the role owner and review related CloudTrail events. Do not change IAM policies automatically."
  },
  {
    id: "CS-1047",
    title: "Unexpected EC2 security group change",
    resource: "i-0a71c9d2 / sg-prod-web",
    source: "EC2",
    severity: "High",
    status: "Needs review",
    time: "18 min ago",
    description: "An inbound rule was changed on a production-facing security group.",
    selectedTool: "inspect_ec2",
    confidence: 0.87,
    evidence: [
      "A security group rule was modified in the sample event.",
      "The affected resource is labelled as production-facing.",
      "The source address and change request need verification."
    ],
    explanation: "A new inbound rule can expose a service more broadly than intended. Confirm the rule, source range, and approved change ticket before assessing impact.",
    recommendation: "Compare the rule with the approved baseline and ask the infrastructure owner to validate the change."
  },
  {
    id: "CS-1046",
    title: "Repeated API calls from a new location",
    resource: "principal/analyst-session",
    source: "CloudTrail",
    severity: "Medium",
    status: "Investigating",
    time: "42 min ago",
    description: "Several API calls differ from the principal's sample baseline.",
    selectedTool: "review_cloudtrail",
    confidence: 0.78,
    evidence: [
      "Multiple API events were grouped in the sample timeline.",
      "The location differs from the example baseline.",
      "No single event is sufficient to establish account compromise."
    ],
    explanation: "The activity differs from the sample baseline and merits contextual review. Location alone is not proof of malicious activity.",
    recommendation: "Review the full event sequence and validate the session with the account owner."
  },
  {
    id: "CS-1045",
    title: "Investigation has insufficient evidence",
    resource: "unknown/principal",
    source: "CloudTrail",
    severity: "Low",
    status: "Needs review",
    time: "1 hr ago",
    description: "The alert lacks enough context for a confident automated tool choice.",
    selectedTool: "human_review",
    confidence: 0.41,
    evidence: [
      "The sample alert has no confirmed resource identifier.",
      "The principal and action context are incomplete.",
      "Automated investigation confidence is below the review threshold."
    ],
    explanation: "The evidence is incomplete, so an automated conclusion would be unreliable. The safe choice is to request human review.",
    recommendation: "Ask an analyst to enrich the alert with a principal, resource, and event timeline before continuing."
  }
];

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "").replace(/\/$/, "");

export type BackendStatus = "online" | "offline" | "not-configured";
export type InvestigationResponse = {
  status?: string;
  selected_tool?: string;
  reason?: string;
  confidence?: number | null;
  model?: string | null;
  latency_ms?: number;
  result?: unknown;
};

export async function fetchAlerts(): Promise<{
  alerts: SecurityAlert[];
  mode: "demo";
  backendStatus: BackendStatus;
  warning?: string;
}> {
  // The current Flask backend exposes /api/health and /api/investigate, not /api/alerts.
  // Keep the sample alert cards clearly labelled as demo data until a real alerts endpoint exists.
  if (!API_BASE) {
    return { alerts: DEMO_ALERTS, mode: "demo", backendStatus: "not-configured", warning: "API URL is not configured. Showing sample alerts." };
  }
  try {
    const response = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Backend returned HTTP ${response.status}`);
    const data: unknown = await response.json();
    if (!data || typeof data !== "object" || !("status" in data) || (data as { status?: unknown }).status !== "healthy") {
      throw new Error("Health endpoint did not report healthy status");
    }
    return {
      alerts: DEMO_ALERTS,
      mode: "demo",
      backendStatus: "online",
      warning: "Backend is reachable. Alert cards are sample data because this API does not provide /api/alerts yet. Investigations will be sent to /api/investigate."
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown connection error";
    return { alerts: DEMO_ALERTS, mode: "demo", backendStatus: "offline", warning: `Backend unavailable (${message}). Showing sample alerts; investigations cannot run.` };
  }
}

export async function startInvestigation(alert: SecurityAlert): Promise<{ ok: boolean; message: string; data?: InvestigationResponse }> {
  if (!API_BASE) return { ok: false, message: "API URL is not configured. No investigation was sent." };
  const eventNameBySource: Record<SecurityAlert["source"], string> = {
    IAM: "AttachUserPolicy",
    EC2: "AuthorizeSecurityGroupIngress",
    CloudTrail: "StopLogging"
  };
  const event = {
    eventName: eventNameBySource[alert.source],
    resource: alert.resource,
    alertId: alert.id,
    source: alert.source,
    severity: alert.severity,
    sample: true
  };
  try {
    const response = await fetch(`${API_BASE}/api/investigate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ finding: alert.description, evidence: alert.evidence, event })
    });
    const data = await response.json().catch(() => null) as InvestigationResponse | null;
    if (!response.ok) throw new Error((data && "error" in data && typeof data.error === "string") ? data.error : `Backend returned HTTP ${response.status}`);
    if (!data || typeof data !== "object") throw new Error("Backend returned an invalid JSON response");
    const status = data.status || "unknown status";
    const tool = data.selected_tool || "not reported";
    const confidence = typeof data.confidence === "number" ? ` Confidence: ${Math.round(data.confidence * 100)}%.` : " Confidence was not returned by the backend.";
    const reason = data.reason ? ` Reason: ${data.reason}.` : "";
    return { ok: status === "completed", message: `Backend response: ${status}. Selected tool: ${tool}.${confidence}${reason}`, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown connection error";
    return { ok: false, message: `Investigation request failed: ${message}` };
  }
}

export const DEMO_DATA_NOTE = "Sample/demo alerts only. The investigation request sends a marked sample event to the configured Flask API; no AWS resources are queried or changed by this frontend.";
