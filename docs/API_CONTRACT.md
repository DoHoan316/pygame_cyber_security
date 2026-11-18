# CyberSafe API Contract v3

All protected requests use `Authorization: Bearer <access_token>`. Success envelope: `{ "success": true, "message": "...", "data": {} }`. Errors use HTTP status and `{ "success": false, "message": "...", "error_code": "...", "details": {} }`.

## Authentication
- `POST /api/auth/register`: `{email,password,display_name}`; password minimum 8 chars.
- `POST /api/auth/login`: `{email,password}`.
- `GET /api/auth/me`.

## Campaign/game
- `GET /api/campaigns`; `GET /api/campaigns/{campaign_id}`.
- `POST /api/game/sessions`: `{campaign_id}`. Returns an existing PLAYING/FEEDBACK session if one exists for the user/campaign.
- `GET /api/game/sessions/{session_id}`: returns current scenario or persisted feedback.
- `POST /api/game/sessions/{session_id}/choices`: `{scenario_id,choice_id}`. Backend validates ownership, state, current scenario and choice ownership; calculates points and records one history row.
- `POST /api/game/sessions/{session_id}/continue`: moves to pending next scenario or COMPLETED.
- `GET /api/game/sessions/{session_id}/result`: completed sessions only.

## Player analytics
- `GET /api/me/dashboard`, `/api/me/history`, `/api/me/errors`.
- `GET /api/leaderboard/{campaign_id}`: top 10 completed best results, sorted SafetyScore desc, RiskScore asc, completion time asc.

## Admin
- `GET /api/admin/users?q=&offset=&limit=`
- `GET /api/admin/users/{user_id}`
- `PATCH /api/admin/users/{user_id}/status`: `{is_active:boolean}`
- `GET /api/admin/analytics/overview`

## Scoring
Original V2 `score_delta` is preserved semantically: positive values become `safety_points`; negative values become positive `risk_points`. Session SafetyScore = total safety points / (total safety points + total risk points) × 100. RiskScore is the complement. This normalization is an implementation decision because the source assignment requires normalized scores but does not provide a fixed numeric formula. It must be confirmed by the group before the final report/demo.
