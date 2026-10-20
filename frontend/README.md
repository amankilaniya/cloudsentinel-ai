# CloudSentinel AI — Next.js Dashboard

A responsive frontend prototype for the CloudSentinel AI project. It shows sample cloud-security alerts, severity, investigation status, a Decider 2B tool choice, confidence, evidence, AI-style explanation, and a suggested next step.

## Safety and demo data

- The included alerts are **illustrative sample data**, not real AWS findings.
- The UI does not query or modify AWS resources by itself.
- No automated remediation is implemented.
- Human validation is required before any real-world change.
- Confidence values are sample values; do not present them as measured model performance.

## Requirements

- Node.js 20.9 or newer
- npm

## Run locally

1. Extract this ZIP.
2. Open a terminal in the `cloudsentinel-ai-dashboard` folder.
3. Install dependencies:

   ```bash
   npm install
   ```

4. Copy `.env.example` to `.env.local` if you want to configure the Flask API. You can leave it unconfigured to use sample data.
5. Start the development server:

   ```bash
   npm run dev
   ```

6. Open `http://localhost:3000`.

## Flask integration contract (must be agreed with the backend teammate)

The frontend currently proposes these endpoints:

### `GET /api/alerts`

Expected response:

```json
{
  "alerts": [
    {
      "id": "CS-1048",
      "title": "Unusual IAM permission change",
      "resource": "role/production-deployer",
      "source": "IAM",
      "severity": "Critical",
      "status": "Investigating",
      "time": "2 min ago",
      "description": "Short alert summary",
      "selectedTool": "inspect_iam",
      "confidence": 0.94,
      "evidence": ["Evidence item one"],
      "explanation": "Explanation grounded in collected evidence",
      "recommendation": "Safe next step requiring validation"
    }
  ]
}
```

Valid `source` values: `IAM`, `EC2`, `CloudTrail`.
Valid `severity` values: `Critical`, `High`, `Medium`, `Low`.
Valid `status` values: `Investigating`, `Needs review`, `Resolved`, `New`.
Valid `selectedTool` values used in the UI: `inspect_iam`, `inspect_ec2`, `review_cloudtrail`, `human_review`.

### `POST /api/investigations`

Request body:

```json
{ "alert_id": "CS-1048" }
```

The frontend treats a successful HTTP response as an accepted request. Confirm the exact route, payload, response, and CORS settings with the backend teammate before relying on this integration. The current routes are a proposed contract, not facts about the backend that already exists.

## Suggested hand-off checklist

- Confirm the backend's real API routes and JSON response schema.
- Confirm how Decider 2B's selected tool, confidence, latency, evidence, and rationale are returned.
- Configure `NEXT_PUBLIC_API_BASE_URL` in `.env.local`.
- Ensure Flask allows requests from the frontend development origin (typically `http://localhost:3000`) if cross-origin requests are used.
- Test loading, empty results, malformed data, backend errors, mobile layout, and the human-review fallback.
- Replace the illustrative sample data before presenting any output as a real investigation.

## Main files

- `app/page.tsx` — dashboard layout and client-side interactions
- `app/globals.css` — responsive UI styling
- `app/layout.tsx` — page metadata and global stylesheet
- `lib/api.ts` — sample data and Flask API calls
- `.env.example` — backend URL configuration example
