# CloudSentinel AI

CloudSentinel AI is a cloud security investigation and risk management prototype built with Python, Flask, and Strands Decider integration. It analyzes supplied security-event data, identifies suspicious activity, and provides investigation recommendations.

> **Project status:** The local investigation tools and Flask API have been tested with synthetic events. Real Strands Decider inference and live AWS data collection are not yet verified.

## Features

- **IAM investigation:** Flags suspicious IAM changes, including privileged policy attachments.
- **EC2 investigation:** Identifies public IP exposure and SSH access open to the internet.
- **CloudTrail review:** Flags security events such as stopped logging for further review.
- **Flask REST API:** Provides health and investigation endpoints.
- **Safe fallback:** Requests human review when the Decider is unavailable or a decision cannot be used.
- **Automated tests:** Unit tests cover the investigation tools, workflow, API, and Decider client behavior.
- **Demo scenarios:** Synthetic security events demonstrate the investigation workflow without modifying AWS resources.

## Architecture

```text
Security Event / Finding
          |
          v
     Flask REST API
          |
          v
  Decider Client / Workflow
          |
          v
 IAM / EC2 / CloudTrail Tools
          |
          v
 Findings, Risk Level, Recommendation
```

The direct tool workflow can be demonstrated locally without a running Decider model. The real model inference path requires a valid model checkpoint and an available inference server.

## Technology Stack

- Python
- Flask
- Flask-CORS
- Requests
- Strands Decider
- Unit testing with `unittest`

## Project Structure

```text
cloudsentinel-ai/
├── agent/
│   ├── decision_options.py
│   ├── decision_request.py
│   ├── decider_client.py
│   └── workflow.py
├── backend/
│   └── app.py
├── tools/
│   ├── inspect_iam.py
│   ├── inspect_ec2.py
│   └── review_cloudtrail.py
├── sample-data/
├── tests/
├── demo.py
├── requirements.txt
└── README.md
```

## Setup

Activate the existing virtual environment:

```bash
cd /root/cloudsentinel-ai
source .venv/bin/activate
```

Install project dependencies if needed:

```bash
python -m pip install -r requirements.txt
```

## Run the Demo

Run the local synthetic-event demonstration:

```bash
python demo.py
```

The demo exercises the IAM, EC2, and CloudTrail investigation tools directly.

Example findings include:

- IAM: suspicious privileged policy attachment, high risk.
- EC2: public IP and SSH access open to the internet, high risk.
- CloudTrail: stopped logging flagged for review.

These are rule-based results from synthetic events, not live AWS findings or model-generated decisions.

## Run the Automated Tests

```bash
python -m unittest discover -s tests -v
```

**Verified locally:** 20 tests passed in the current test run.

## Start the Flask API

```bash
python -m backend.app
```

The development server listens on port `5000`.

### Health endpoint

```bash
curl -i http://127.0.0.1:5000/api/health
```

Expected response:

```json
{
  "service": "CloudSentinel AI API",
  "status": "healthy"
}
```

### Investigation endpoint

```bash
curl -i -X POST http://127.0.0.1:5000/api/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "finding": "Suspicious IAM policy attachment",
    "event": {
      "event_name": "AttachUserPolicy",
      "principal": "demo-user",
      "changes": ["AdministratorAccess"]
    },
    "evidence": ["Demo security event"]
  }'
```

When the Decider service is unavailable, the API can return a response with `status` set to `human_review_required`. This is the safe fallback and does not mean the investigation tool ran successfully.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check API health |
| POST | `/api/investigate` | Submit a finding, event, and optional evidence |

## Current Limitations

- The investigation tools currently analyze supplied event dictionaries.
- Live AWS evidence collection has not been implemented or verified.
- Real Strands Decider inference has not yet been verified end to end.
- The frontend integration and production deployment are not verified.
- Findings and recommendations should be reviewed by a qualified human before taking action.

## Roadmap

- [ ] Connect and verify real Strands Decider inference.
- [ ] Integrate authorized AWS evidence collection.
- [ ] Add comprehensive API and integration tests.
- [ ] Integrate the frontend.
- [ ] Add monitoring, audit logging, and production security controls.

## Security Notes

- Use synthetic data for demonstrations.
- Do not commit credentials, access keys, tokens, or other secrets.
- Apply least-privilege permissions when adding AWS integrations.
- Do not expose the Flask development server as a production service.
- Require human review before applying changes to cloud resources.

## License

See [LICENSE](LICENSE).
