import { useState } from 'react'
import Editor from '@monaco-editor/react'
import axios from 'axios'
import './CodeChallenge.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

function CodeChallenge({ userId }) {
  const [code, setCode] = useState('import pandas as pd\n\n# Напишите ваш код здесь\n')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleRun = async () => {
    setLoading(true)
    setResult(null)

    try {
      const response = await axios.post(`${API_BASE}/code/execute/`, {
        code
      })
      setResult(response.data)
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.error || error.response?.data?.code?.[0] || 'Ошибка выполнения кода'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="code-challenge">
      <h2>💻 Практика кода</h2>

      <div className="editor-container">
        <Editor
          height="300px"
          defaultLanguage="python"
          theme="vs-dark"
          value={code}
          onChange={(value) => setCode(value)}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
          }}
        />
      </div>

      <button
        className="run-button"
        onClick={handleRun}
        disabled={loading}
      >
        {loading ? '⏳ Выполняется...' : '▶️ Запустить'}
      </button>

      {result && (
        <div className={`result ${result.success ? 'success' : 'error'}`}>
          <h3>{result.success ? '✅ Успешно' : '❌ Ошибка'}</h3>
          <pre>{result.output || result.error}</pre>
        </div>
      )}
    </div>
  )
}

export default CodeChallenge
