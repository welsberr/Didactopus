# API Outline

## Review-and-promotion workflow

### Candidate intake
- `POST /api/knowledge-candidates`
- `GET /api/knowledge-candidates`
- `GET /api/knowledge-candidates/{candidate_id}`

### Review
- `POST /api/knowledge-candidates/{candidate_id}/reviews`
- `GET /api/knowledge-candidates/{candidate_id}/reviews`

### Promotion
- `POST /api/knowledge-candidates/{candidate_id}/promote`
- `GET /api/promotions`
- `GET /api/promotions/{promotion_id}`

### Archive / reject
- `POST /api/knowledge-candidates/{candidate_id}/archive`
- `POST /api/knowledge-candidates/{candidate_id}/reject`

## Synthesis engine

### Candidate generation
- `POST /api/synthesis/run`
- `GET /api/synthesis/candidates`
- `GET /api/synthesis/candidates/{synthesis_id}`

### Clusters
- `GET /api/synthesis/clusters`
- `GET /api/synthesis/clusters/{cluster_id}`

### Promotion path
- `POST /api/synthesis/candidates/{synthesis_id}/promote`

## Artifact lifecycle additions
- `GET /api/artifacts/{artifact_id}/download`
- `POST /api/artifacts/{artifact_id}/retention`
- `DELETE /api/artifacts/{artifact_id}`

## Learner knowledge export
- `POST /api/learners/{learner_id}/knowledge-export/{pack_id}`
