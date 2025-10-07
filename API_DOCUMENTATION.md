# 📡 API Documentation

REST API documentation for Telegram Mini App.

## Base URL

```
Development: http://localhost:8000/api/
Production: https://yourdomain.com/api/
```

## Authentication

Currently using simple user_id based authentication (Telegram user ID).
No additional authentication required for public endpoints.

---

## Endpoints

### 1. Topics

#### List all topics
```http
GET /api/topics/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "DataFrames",
    "description": "Learn about pandas DataFrames",
    "documentation": "# DataFrame basics...",
    "order": 1
  }
]
```

#### Get single topic
```http
GET /api/topics/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "DataFrames",
  "description": "Learn about pandas DataFrames",
  "documentation": "# DataFrame basics...",
  "order": 1
}
```

---

### 2. Questions

#### Get next question
```http
GET /api/questions/next/
```

**Query Parameters:**
- `user_id` (required): Telegram user ID
- `topic_id` (optional): Filter by topic

**Response:**
```json
{
  "id": 42,
  "topic": "DataFrames",
  "difficulty": "beginner",
  "question_text": "What method creates a DataFrame?",
  "code_example": "import pandas as pd",
  "options": [
    {"letter": "A", "text": "pd.DataFrame()"},
    {"letter": "B", "text": "pd.create()"},
    {"letter": "C", "text": "pd.new()"},
    {"letter": "D", "text": "pd.make()"}
  ],
  "correct_option": "A",
  "explanation": "pd.DataFrame() is the correct constructor",
  "documentation_link": "https://pandas.pydata.org/..."
}
```

**Error Responses:**
```json
// 400 Bad Request
{
  "error": "user_id parameter is required"
}

// 404 Not Found
{
  "error": "User not found"
}

// 404 Not Found
{
  "error": "No questions available"
}
```

---

#### Submit answer
```http
POST /api/questions/answer/
```

**Request Body:**
```json
{
  "user_id": 123456789,
  "question_id": 42,
  "answer": "A"
}
```

**Response:**
```json
{
  "success": true,
  "is_correct": true,
  "correct_option": "A",
  "explanation": "pd.DataFrame() is the correct constructor"
}
```

**Validation:**
- `answer` must be A, B, C, or D
- `user_id` and `question_id` must exist

**Error Responses:**
```json
// 400 Bad Request (validation error)
{
  "answer": ["Answer must be A, B, C, or D"]
}

// 404 Not Found
{
  "error": "User not found"
}
```

---

### 3. Code Execution

#### Execute Python/Pandas code
```http
POST /api/code/execute/
```

**Request Body:**
```json
{
  "code": "import pandas as pd\ndf = pd.DataFrame({'a': [1, 2, 3]})\nprint(df)"
}
```

**Response (Success):**
```json
{
  "success": true,
  "output": "   a\n0  1\n1  2\n2  3"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "NameError: name 'x' is not defined"
}
```

**Limitations:**
- Max code length: 10,000 characters
- Restricted namespace (only safe builtins + pandas + numpy)
- No file system access
- No network access
- Execution timeout: 5 seconds

**Validation Errors:**
```json
// 400 Bad Request
{
  "code": ["Code cannot be empty"]
}

// 400 Bad Request
{
  "code": ["Code is too long (max 10000 characters)"]
}
```

---

### 4. User Statistics

#### Get user stats
```http
GET /api/users/stats/
```

**Query Parameters:**
- `user_id` (required): Telegram user ID

**Response:**
```json
{
  "total_questions": 50,
  "correct_answers": 38,
  "accuracy": 76.0,
  "topics": [
    {
      "topic": "DataFrames",
      "attempted": 20,
      "correct": 16,
      "accuracy": 80.0
    },
    {
      "topic": "Series",
      "attempted": 15,
      "correct": 12,
      "accuracy": 80.0
    }
  ]
}
```

---

## Rate Limiting

- **Anonymous requests**: 100 requests per hour per IP
- No authentication required for current version

**Rate limit exceeded response:**
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

## Error Handling

### Standard Error Responses

**400 Bad Request:**
```json
{
  "field_name": ["Error message"],
  "another_field": ["Another error message"]
}
```

**404 Not Found:**
```json
{
  "error": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Data Models

### Topic
```typescript
{
  id: number
  name: string
  description: string
  documentation: string  // Markdown
  order: number
}
```

### Question
```typescript
{
  id: number
  topic: string  // Topic name
  difficulty: "beginner" | "intermediate" | "advanced"
  question_text: string
  code_example: string | null
  options: Array<{letter: string, text: string}>
  correct_option: "A" | "B" | "C" | "D"
  explanation: string
  documentation_link: string | null
}
```

### User Stats
```typescript
{
  total_questions: number
  correct_answers: number
  accuracy: number  // 0-100
  topics: Array<{
    topic: string
    attempted: number
    correct: number
    accuracy: number
  }>
}
```

---

## Development

### Testing endpoints

Using curl:
```bash
# Get topics
curl http://localhost:8000/api/topics/

# Get next question
curl "http://localhost:8000/api/questions/next/?user_id=123456789"

# Submit answer
curl -X POST http://localhost:8000/api/questions/answer/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":123456789,"question_id":42,"answer":"A"}'

# Execute code
curl -X POST http://localhost:8000/api/code/execute/ \
  -H "Content-Type: application/json" \
  -d '{"code":"import pandas as pd\nprint(pd.__version__)"}'
```

### Browsable API

DRF provides a browsable API interface in development:
```
http://localhost:8000/api/
```

Navigate to any endpoint to see interactive documentation and test forms.

---

## Migration from old API

### Endpoint changes:

| Old Endpoint | New Endpoint | Notes |
|-------------|-------------|-------|
| `/api/topics/` | `/api/topics/` | ✅ No change |
| `/api/next-question/` | `/api/questions/next/` | Updated path |
| `/api/answer-question/` | `/api/questions/answer/` | Updated path |
| `/api/run-code/` | `/api/code/execute/` | Updated path |

### Response format changes:

**Options format (Questions):**
```javascript
// Old (array of arrays)
"options": [["A", "text"], ["B", "text"]]

// New (array of objects)
"options": [
  {"letter": "A", "text": "text"},
  {"letter": "B", "text": "text"}
]
```

**Frontend compatibility:**
Both formats are supported in the frontend for backward compatibility.

---

## Security Notes

1. **Code Execution**: Sandboxed environment with restricted namespace
2. **User IDs**: Currently trusting Telegram-provided user IDs
3. **CORS**: Configured for specific origins in production
4. **Rate Limiting**: Prevents abuse of API endpoints
5. **Input Validation**: All inputs validated via DRF serializers

---

## Future Improvements

- [ ] JWT authentication
- [ ] Pagination for topics/questions
- [ ] WebSocket support for real-time updates
- [ ] More granular permissions
- [ ] API versioning (v1, v2)
- [ ] Request/response caching
